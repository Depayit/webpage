import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

# --- 1. Init App ---
app = FastAPI(title="Depayit MVP - API Only")

# Setup CORS - ปรับให้ปลอดภัยขึ้นเมื่อใช้งานจริง
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # ในอนาคตควรเปลี่ยนเป็น ["https://depayit.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Mock Database ---
# ข้อมูลจะหายไปเมื่อ Restart Server (ควรเปลี่ยนเป็น SQLite ในภายหลัง)
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

@app.get("/api/health")
def health_check():
    return {"status": "online", "timestamp": datetime.now()}

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
    return {"status": "PAID", "message": "Payment Simulated"}

# [POST] อัปเดตการส่งของ
@app.post("/api/transactions/{tx_id}/shipment")
def update_shipping(tx_id: str, data: ShippingUpdate):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="Not found")
    
    # ใช้ model_dump() แทน dict() สำหรับ Pydantic v2
    fake_db[tx_id].update({
        "status": "SHIPPED",
        "shipping_info": data.model_dump(),
        "auto_release_at": "48 hours from now"
    })
    
    return {"status": "SHIPPED", "message": "Shipping Updated"}

# --- 5. Static Files ---
# หมายเหตุ: เราจะไม่ทำ Redirect ที่ "/" เพื่อให้ Nginx ส่งไฟล์ index.html ให้เอง
# แต่ยังคง mount /static ไว้เผื่อกรณีต้องการเรียกไฟล์ผ่าน API ตรงๆ
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
