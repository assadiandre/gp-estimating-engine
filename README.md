# GP Estimating Engine

A chat agent that quotes print jobs by writing inputs into a live Excel Pricing Tool workbook and reading the results back.

You ask for a quote in plain language. The agent updates the sheet through Microsoft Graph and returns cost, price, and turnaround.

```bash
python -m agent "quote 5000 flat cards"
```

## v1

A simple text → output price calculator.

You type what you want. It writes those inputs to the Pricing Tool and returns the quote.

See [Microsoft Graph API setup](docs/microsoft-graph-setup.md) to connect the Excel workbook.
