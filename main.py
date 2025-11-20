from fastapi import FastAPI
from pydantic import BaseModel
import base64
import pandas as pd
import io

app = FastAPI()


class InvoiceRequest(BaseModel):
    contentBytes: str


@app.post("/parse-invoice")
def parse_invoice(data: InvoiceRequest):

    # Decode Base64 CSV
    decoded = base64.b64decode(data.contentBytes)
    text = decoded.decode("utf-8", errors="ignore")

    # Load CSV
    df = pd.read_csv(io.StringIO(text))

    # customerName should always be null
    customer_name = None

    # Ensure required columns exist
    if "Document Reference" not in df or "Amount Due" not in df:
        return {
            "customerName": None,
            "invoices": [],
            "totalAmount": 0
        }

    # Group by Document Reference and sum Amount Due
    grouped = df.groupby("Document Reference")["Amount Due"].sum()

    # Prepare invoice list
    invoice_details = [
        {
            "invoiceNumber": str(invoice),    # always Document Reference
            "amount": round(float(amount), 2)
        }
        for invoice, amount in grouped.items()
    ]

    # Total amount
    total_amount = round(float(df["Amount Due"].sum()), 2)

    return {
        "customerName": customer_name,
        "invoices": invoice_details,
        "totalAmount": total_amount
    }
