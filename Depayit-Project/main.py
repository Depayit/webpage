import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

app = FastAPI()

# 1. อนุญาตให้คุยข้าม Domain (เผื่อไว้)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. จำลอง Database (เก็บข้อมูลใน RAM)
fake_db = {}

# --- Data Models ---
class TransactionCreate(BaseModel):
    product_name: str
    price: float
    phone_number: str
    description: Optional[str] = None

class ShippingUpdate(BaseModel):
    courier: str
    tracking_number: str
    bank_name: str
    account_name: str
    account_number: str

# --- API Endpoints (สมอง) ---

@app.post("/api/transactions")
def create_transaction(data: TransactionCreate):
    tx_id = f"TX-{random.randint(10000, 99999)}"
    pin = f"{random.randint(100000, 999999)}"
    fake_db[tx_id] = {
        "id": tx_id,
        "pin": pin,
        "product": data.product_name,
        "amount": data.price,
        "phone": data.phone_number,
        "status": "CREATED",
        "created_at": datetime.now().isoformat()
    }
    return {"message": "Success", "tx_id": tx_id, "pin": pin}

@app.get("/api/transactions/{tx_id}")
def get_transaction(tx_id: str):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="Not found")
    return fake_db[tx_id]

@app.post("/api/transactions/{tx_id}/shipment")
def update_shipping(tx_id: str, data: ShippingUpdate):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="Not found")
    fake_db[tx_id].update({
        "status": "SHIPPED",
        "shipping": data.dict(),
        "auto_release_at": "48 hours"
    })
    return {"status": "SHIPPED"}

@app.post("/api/transactions/{tx_id}/pay")
def simulate_payment(tx_id: str):
    if tx_id not in fake_db: raise HTTPException(status_code=404)
    fake_db[tx_id]["status"] = "PAID"
    return {"status": "PAID"}

# --- Serving Frontend (หัวใจสำคัญ) ---

# เข้าเว็บมาปุ๊บ ให้เด้งไปหน้าสร้างรายการทันที
@app.get("/")
def read_root():
    return RedirectResponse(url="/static/CreateTransection-01.html")

# บอก FastAPI ว่าไฟล์ HTML อยู่ในโฟลเดอร์ static นะ
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
