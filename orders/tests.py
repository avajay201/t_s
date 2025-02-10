import razorpay
import time

RAZORPAY_KEY_ID = "rzp_test_US5QPaXrbvS5lj"
RAZORPAY_SECRET = "ZaILMq9xceGyJuvrLvTbMtGD"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))

current_time = int(time.time())

expiry_time = current_time + (64800 * 60)  # 64800 minutes = 45 days

qr_data = {
    "type": "upi_qr",
    "name": "Ajay's Store",
    "usage": "single_use",
    "fixed_amount": True,
    "payment_amount": 300,
    "description": "Pay any amount to Ajay's Store",
    "close_by": expiry_time,
    "notes": {
        "purpose": "Random payment"
    }
}

try:
    qr_code = client.qrcode.create(qr_data)
    print("QR Code Created:", qr_code)
except razorpay.errors.BadRequestError as e:
    print("Error:", e)