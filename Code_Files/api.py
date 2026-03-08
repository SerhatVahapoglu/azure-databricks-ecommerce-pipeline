import os
from fastapi import FastAPI
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
import json
from datetime import datetime, timezone
import random
from faker import Faker

app = FastAPI(title="E-Ticaret Azure Akışı")
fake = Faker("tr_TR")

CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME", "orders-topic")

producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENT_HUB_NAME
)

@app.post("/place_order")
async def place_order():
    order = {
        "order_id": fake.uuid4(),
        "customer_name": fake.name(),
        "city_id": str(random.randint(1, 5)),
        "status_id": "100",
        "order_value": round(random.uniform(100.0, 5000.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    async with producer:
        event_data_batch = await producer.create_batch()
        event_data_batch.add(EventData(json.dumps(order)))
        await producer.send_batch(event_data_batch)

    print(f"✅ Azure'a Gönderildi: {order['customer_name']}")
    return {"status": "Sipariş buluta uçtu!", "data": order}