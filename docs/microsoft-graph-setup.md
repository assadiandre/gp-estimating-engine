# Microsoft Graph API Setup Guide (Excel Sheet Automation)

Quick guide to setting up Microsoft Graph API for background Python automation with Excel spreadsheets.

---

## Prerequisites
* A **Microsoft 365 Business Account** (e.g., Business Basic) or a **Microsoft 365 Developer Sandbox Account**.
* An Excel file saved in OneDrive for Business (e.g., `excel_files/pricing_sheet.xlsm`).

---

## 1. Register Your App in Azure
1. Log in to [Azure Portal](https://portal.azure.com).
2. Go to **Microsoft Entra ID** > **App registrations** > **+ New registration**.
3. Name your app (e.g., `Excel Automation App`).
4. Set account type to **Single tenant**.
5. Click **Register**.
6. Copy and save these two IDs from the **Overview** page:
   * **Application (client) ID**
   * **Directory (tenant) ID**

---

## 2. Create a Client Secret
1. In your app registration menu, click **Certificates & secrets**.
2. Under **Client secrets**, click **+ New client secret**.
3. Enter a description, set an expiration, and click **Add**.
4. **Copy the Secret Value immediately** (it will never be displayed again).

---

## 3. Grant API Permissions
1. In your app registration menu, click **API permissions** > **+ Add a permission**.
2. Select **Microsoft Graph** > **Application permissions**.
3. Search for `Files`, expand **Files**, and check **`Files.ReadWrite.All`**.
4. Click **Add permissions**.
5. Click **Grant admin consent for [Your Organization]** and select **Yes**.  
   *(Ensure a green checkmark appears under Status)*.

---

## 4. Prepare Your Excel File
1. Upload your file (`pricing_sheet.xlsm`) to **OneDrive for Business** inside a folder named `excel_files`.
2. Note down the **User Email** of the account owning that OneDrive (e.g., `admin@yourcompany.onmicrosoft.com`).

---

## 5. Environment File (`.env`)
Create a `.env` file in your Python project directory with your copied values:

```env
TENANT_ID=your_directory_tenant_id_here
CLIENT_ID=your_application_client_id_here
CLIENT_SECRET=your_client_secret_value_here
USER_EMAIL=your_email@yourcompany.onmicrosoft.com
```
