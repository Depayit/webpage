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

# Setup CORS (เผื่ออนาคตแยก Server หน้าบ้าน-หลังบ้าน)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Mock Database (ใช้ตัวแปรเก็บแทน DB จริงไปก่อน) ---
fake_db = {}

# --- 3. Data Models (ตระกร้าสำหรับรับข้อมูล) ---
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

# --- 4. API Endpoints (สมองกลไก) ---

# [POST] สร้างรายการใหม่ (จากหน้า 1)
@app.post("/api/transactions")
def create_transaction(data: TransactionCreate):
    # สร้าง ID และ PIN แบบสุ่ม
    tx_id = f"TX-{random.randint(1000, 9999)}-{random.randint(10,99)}X"
    pin = f"{random.randint(100000, 999999)}"
    
    # บันทึกลลง Database จำลอง
    fake_db[tx_id] = {
        "id": tx_id,
        "pin": pin,
        "product": data.product_name,
        "amount": data.price,
        "phone": data.phone_number,
        "desc": data.description,
        "status": "CREATED", # สถานะเริ่มต้น
        "created_at": datetime.now().isoformat()
    }
    
    print(f"✅ Created: {tx_id} | PIN: {pin}") # ปริ้นท์ดูใน Terminal
    return {"message": "Success", "tx_id": tx_id, "pin": pin}

# [GET] ดึงข้อมูลรายการ (ใช้ในหน้า Link, Pay, Check)
@app.get("/api/transactions/{tx_id}")
def get_transaction(tx_id: str):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้")
    return fake_db[tx_id]

# [POST] จำลองการจ่ายเงิน (ใช้ในหน้า 3 Buyer Payment)
@app.post("/api/transactions/{tx_id}/pay")
def simulate_payment(tx_id: str):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="Not found")
    
    fake_db[tx_id]["status"] = "PAID"
    fake_db[tx_id]["paid_at"] = datetime.now().isoformat()
    
    print(f"💰 Paid: {tx_id}")
    return {"status": "PAID", "message": "Payment Simulated"}

# [POST] อัปเดตการส่งของ (จากหน้า 4 Seller Shipping)
@app.post("/api/transactions/{tx_id}/shipment")
def update_shipping(tx_id: str, data: ShippingUpdate):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="Not found")
    
    fake_db[tx_id].update({
        "status": "SHIPPED",
        "shipping_info": data.dict(),
        "auto_release_at": "48 hours from now"
    })
    
    print(f"🚚 Shipped: {tx_id}")
    return {"status": "SHIPPED", "message": "Shipping Updated"}

# --- 5. Frontend Serving (ส่วนที่ทำให้เปิดเว็บได้) ---

# ถ้าเข้าเว็บมาเปล่าๆ (Root) ให้เด้งไปหน้าสร้างรายการ
@app.get("/")
def read_root():
    return RedirectResponse(url="/static/CreateTransection-01.html")

# บอกให้ Python รู้ว่าไฟล์ HTML อยู่ในโฟลเดอร์ชื่อ 'static'
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# --- Run Server (ถ้ากดรันไฟล์นี้โดยตรง) ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
