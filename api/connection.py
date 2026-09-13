"""Microsoft Graph connection: env, token, and authenticated requests."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import msal
import requests
from dotenv import load_dotenv

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]
TARGET_FILE_PATH = "excel_files/pricing_sheet.xlsm"


class GraphAPIError(RuntimeError):
    """Raised when a Microsoft Graph request fails."""

    def __init__(self, message: str, status_code: int | None = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


class GraphConnection:
    """Client-credentials session against one user's OneDrive file."""

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        user_email: str,
        file_path: str = TARGET_FILE_PATH,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_email = user_email
        self.file_path = file_path
        self.access_token: str | None = None
        self.item_id: str | None = None

    @classmethod
    def from_env(cls, file_path: str = TARGET_FILE_PATH) -> GraphConnection:
        load_dotenv()
        return cls(
            tenant_id=required_env("TENANT_ID"),
            client_id=required_env("CLIENT_ID"),
            client_secret=required_env("CLIENT_SECRET"),
            user_email=required_env("USER_EMAIL"),
            file_path=file_path,
        )

    def acquire_token(self) -> str:
        app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(scopes=GRAPH_SCOPE)
        if "access_token" not in result:
            error = result.get("error")
            description = result.get("error_description")
            raise GraphAPIError(f"Token request failed: {error} — {description}", body=result)
        self.access_token = result["access_token"]
        return self.access_token

    def resolve_item_id(self) -> str:
        encoded_user = quote(self.user_email)
        url = f"{GRAPH_BASE}/users/{encoded_user}/drive/root:/{self.file_path}"
        payload = self.request("GET", url)
        item_id = payload.get("id")
        if not item_id:
            raise GraphAPIError("Drive item response did not include an id.", body=payload)
        self.item_id = item_id
        return item_id

    def connect(self) -> GraphConnection:
        self.acquire_token()
        self.resolve_item_id()
        return self

    def request(
        self,
        method: str,
        url: str,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.access_token:
            raise GraphAPIError("Access token is not set. Call acquire_token() first.")

        response = requests.request(
            method,
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            json=json_body,
            timeout=60,
        )
        if not response.ok:
            try:
                error_body = response.json()
            except ValueError:
                error_body = response.text
            raise GraphAPIError(
                f"Graph {method} {url} failed ({response.status_code}): {error_body}",
                status_code=response.status_code,
                body=error_body,
            )
        if not response.content:
            return {}
        return response.json()
