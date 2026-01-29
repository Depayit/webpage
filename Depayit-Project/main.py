import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

# --- 1. Init App ---
app = FastAPI(title="Depayit MVP")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Mock Database ---
fake_db = {}

# --- 3. Data Models ---
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

# --- 4. API Endpoints ---

# [POST] สร้างรายการใหม่
@app.post("/api/transactions")
def create_transaction(data: TransactionCreate):
    tx_id = f"TX-{random.randint(1000, 9999)}-{random.randint(10,99)}X"
    pin = f"{random.randint(100000, 999999)}"
    
    fake_db[tx_id] = {
        "id": tx_id,
        "pin": pin,
        "product": data.product_name,
        "amount": data.price,
        "phone": data.phone_number,
        "desc": data.description,
        "status": "CREATED",
        "created_at": datetime.now().isoformat()
    }
    
    print(f"✅ Created: {tx_id} | PIN: {pin}")
    return {"message": "Success", "tx_id": tx_id, "pin": pin}

# [GET] ดึงข้อมูลรายการ
@app.get("/api/transactions/{tx_id}")
def get_transaction(tx_id: str):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้")
    return fake_db[tx_id]

# [POST] จำลองการจ่ายเงิน
@app.post("/api/transactions/{tx_id}/pay")
def simulate_payment(tx_id: str):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="Not found")
    
    fake_db[tx_id]["status"] = "PAID"
    fake_db[tx_id]["paid_at"] = datetime.now().isoformat()
    
    print(f"💰 Paid: {tx_id}")
    return {"status": "PAID", "message": "Payment Simulated"}

# [POST] อัปเดตการส่งของ
@app.post("/api/transactions/{tx_id}/shipment")
def update_shipping(tx_id: str, data: ShippingUpdate):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="Not found")
    
    # จุดที่มักจะ Error คือตรงนี้ครับ (ผมจัดให้ตรงแนวแล้ว)
    fake_db[tx_id].update({
        "status": "SHIPPED",
        "shipping_info": data.dict(),
        "auto_release_at": "48 hours from now"
    })
    
    print(f"🚚 Shipped: {tx_id}")
    return {"status": "SHIPPED", "message": "Shipping Updated"}

# --- 5. Frontend Serving ---

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/CreateTransection-01.html")

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# --- Run Server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)