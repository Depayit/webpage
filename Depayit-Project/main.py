from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
import random

# Initialize App
app = FastAPI(title="Depayit MVP API")

# Setup CORS (เพื่อให้ Frontend HTML เรียก API ได้โดยไม่ติด Permission)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ใน Production ควรระบุ Domain จริง
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- 1. Data Models (Pydantic) ---
# แบบฟอร์มสำหรับรับข้อมูลจากหน้า "สร้างรายการ"
class TransactionCreate(BaseModel):
    product_name: str = Field(..., min_length=3)
    price: float = Field(..., gt=0)
    phone_number: str
    description: Optional[str] = None

# แบบฟอร์มสำหรับรับข้อมูลจากหน้า "แจ้งส่งของ"
class ShippingUpdate(BaseModel):
    courier: str
    tracking_number: str
    bank_name: str
    account_name: str
    account_number: str

# --- 2. Mock Database (ใช้ตัวแปรแทน DB จริงไปก่อน) ---
fake_db = {}

# --- 3. API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Depayit API is running 🚀"}

#[PAGE 1 Logic] สร้างรายการสินค้า
@app.post("/api/transactions")
def create_transaction(data: TransactionCreate):
    # 1. Generate IDs
    tx_id = f"TX-{random.randint(1000, 9999)}"
    # (start_span)ใน Production ต้อง Hash PIN นี้ก่อนเก็บ
    pin = f"{random.randint(100000, 999999)}" 
    
    # 2. Save to DB (In-memory)
    transaction_record = {
        "id": tx_id,
        "pin": pin,
        "product": data.product_name,
        "amount": data.price,
        "seller_phone": data.phone_number,
        "status": "CREATED", 
        "created_at": datetime.now().isoformat()
    }

# [NEW] ดึงรายละเอียดรายการ (สำหรับหน้าจ่ายเงิน และ เช็คสถานะ)
@app.get("/api/transactions/{tx_id}")
def get_transaction(tx_id: str):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้")
    return fake_db[tx_id]

# [NEW] จำลองการโอนเงินสำเร็จ (สำหรับคนซื้อกดปุ่ม "จำลองจ่ายเงิน")
@app.post("/api/transactions/{tx_id}/pay")
def simulate_payment(tx_id: str):
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้")
    
    # อัปเดตสถานะเป็น PAID
    fake_db[tx_id]["status"] = "PAID"
    fake_db[tx_id]["paid_at"] = datetime.now().isoformat()
    
    return {"message": "ชำระเงินเรียบร้อย (Simulation)", "status": "PAID"}

    fake_db[tx_id] = transaction_record
    
    # 3. Return response to Frontend
    return {
        "message": "สร้างรายการสำเร็จ",
        "tx_id": tx_id,
        "pin": pin,
        "link": f"https://depayit.com/pay/{tx_id}"
    }

# [PAGE 2 Logic] อัปเดตการจัดส่ง
@app.post("/api/transactions/{tx_id}/shipment")
def update_shipping(tx_id: str, data: ShippingUpdate):
    # 1. Check if transaction exists
    if tx_id not in fake_db:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้")
    
    # 2. Update Status & Shipping Info
    # ใน Production ต้อง Encrypt เลขบัญชีก่อนเก็บ
    fake_db[tx_id].update({
        "status": "SHIPPED",
        "courier": data.courier,
        "tracking_number": data.tracking_number,
        "seller_bank": {
            "name": data.bank_name,
            "acc_name": data.account_name,
            "acc_num": data.account_number # Sensitive Data!
        },
        "auto_release_at": "48 hours from now" # Mock logic
    })
    
    return {
        "message": "บันทึกข้อมูลจัดส่งเรียบร้อย",
        "status": "SHIPPED",
        "auto_release": "เริ่มนับถอยหลัง 48 ชม."
    }
    }
