import json
import time
import random
from datetime import datetime
from faker import Faker

# Türkçe veriler üretmek için Faker'ı ayarlıyoruz
fake = Faker('tr_TR')

def generate_order():
    """Rastgele bir e-ticaret/lojistik sipariş olayı oluşturur."""
    
    order_data = {
        "order_id": fake.uuid4(),
        "customer_name": fake.name(),
        "city_id": str(random.randint(1, 5)), # map_cities.json ile eşleşecek
        "status_id": str(random.choice([100, 101, 102, 103, 104])), # map_statuses.json ile eşleşecek
        "order_value": round(random.uniform(50.0, 2500.0), 2),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return order_data

if __name__ == "__main__":
    print("🚀 Sentetik sipariş verisi üretimi başlıyor... (Durdurmak için CTRL+C)")
    time.sleep(2)
    
    try:
        while True:
            # Veriyi üret
            order = generate_order()
            
            # JSON formatına çevir ve konsola yazdır
            print(json.dumps(order, ensure_ascii=False))
            
            # Saniyede bir veri üretsin (Gerçekçilik için rastgele bir bekleme süresi de koyabiliriz)
            time.sleep(random.uniform(0.5, 2.0)) 
            
    except KeyboardInterrupt:
        print("\n🛑 Veri akışı durduruldu.")