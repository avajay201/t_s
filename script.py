import requests
import random
from datetime import datetime, timedelta

url = "http://127.0.0.1:8000/api/order/orders/"

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ5NDg0MzM4LCJpYXQiOjE3MzkxMTYzMzgsImp0aSI6ImM1OGFlYTExYzc0MTQ3YTI5Njg0ZDMwMzI5MDI3MGFhIiwidXNlcl9pZCI6Mn0.Wz9XCkyYliZzlWzovlOoewpe4LUFLQ4zUNYv7dP1blA",
    "Content-Type": "application/json"
}

n = 5

start_date = datetime(2024, 1, 1)
end_date = datetime.today()

food_item_ids = 5

def random_created_at():
    random_days = random.randint(0, (end_date - start_date).days)
    random_time = timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    random_datetime = start_date + timedelta(days=random_days) + random_time
    return random_datetime.strftime("%Y-%m-%dT%H:%M:%S")

for _ in range(395):
    data = {
        "items": [
            {
                "food_item": 1,
                "quantity": random.randint(1, 5)
            },
        ],
        "payment_method": "CASH",
        "created_at": random_created_at()
    }
    
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Order created successfully:", response.json())
    else:
        print("Failed to create order:", response.text)
