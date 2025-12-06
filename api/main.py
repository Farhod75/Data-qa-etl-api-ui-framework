from fastapi import FastAPI, HTTPException
from typing import List, Dict
from utils import db_client

app = FastAPI()

# Placeholder for a simple in-memory "authentication"
# In a real app, this would be a proper auth system
VALID_CUSTOMER_IDS = {1001, 1002}

@app.get("/")
async def read_root():
    return {"message": "Banking API is running"}

@app.get("/customers/{customer_id}/balances", response_model=List[Dict])
async def get_customer_balances(customer_id: int):
    if customer_id not in VALID_CUSTOMER_IDS:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch balances from the dw.customer_balances table
    sql = f"SELECT account_id, balance FROM dw.customer_balances WHERE customer_id = {customer_id}"
    results = db_client.fetch_all("dw", sql)

    if not results:
        return [] # No balances found for this customer

    balances = []
    for row in results:
        balances.append({"account_id": row[0], "balance": float(row[1])}) # Convert Decimal to float
    return balances

@app.get("/customers/{customer_id}/transactions", response_model=List[Dict])
async def get_customer_transactions(customer_id: int):
    if customer_id not in VALID_CUSTOMER_IDS:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch transactions from the dw.transactions_fact table
    sql = f"SELECT id, account_id, amount, currency, status, created_at FROM dw.transactions_fact WHERE customer_id = {customer_id} ORDER BY created_at DESC LIMIT 10"
    results = db_client.fetch_all("dw", sql)

    if not results:
        return [] # No transactions found for this customer

    transactions = []
    for row in results:
        transactions.append({
            "id": row[0],
            "account_id": row[1],
            "amount": float(row[2]),
            "currency": row[3],
            "status": row[4],
            "created_at": row[5].isoformat() # Convert datetime to ISO format string
        })
    return transactions

# You can add more endpoints here, e.g., for transfers, but keep it simple for now.