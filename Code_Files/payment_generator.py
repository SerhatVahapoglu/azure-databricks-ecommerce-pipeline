import pandas as pd
import random
import uuid
from pathlib import Path
from datetime import timedelta

random.seed(42)

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"

# Burayı daha sonra gerçek orders export dosyana göre değiştirebilirsin
ORDERS_PATH = DATA_DIR / "orders_clean.csv"
PAYMENTS_OUTPUT_PATH = DATA_DIR / "payments_generated.csv"

# -----------------------------
# CONFIG
# -----------------------------
PAYMENT_METHODS = [
    ("credit_card", 0.45),
    ("debit_card", 0.20),
    ("bank_transfer", 0.15),
    ("digital_wallet", 0.12),
    ("cash_on_delivery", 0.08),
]

BANKS = [
    "Ziraat Bankası",
    "İş Bankası",
    "Garanti BBVA",
    "Akbank",
    "Yapı Kredi",
    "QNB Finansbank",
    "VakıfBank",
    "Halkbank",
    "Enpara",
]

PAYMENT_STATUS_WEIGHTS = {
    "success": 0.78,
    "failed": 0.10,
    "pending": 0.07,
    "refunded": 0.03,
    "cancelled": 0.02,
}

CURRENCIES = ["TRY"]

# -----------------------------
# HELPERS
# -----------------------------
def weighted_choice(items):
    """
    items: [("value1", weight1), ("value2", weight2), ...]
    """
    values = [x[0] for x in items]
    weights = [x[1] for x in items]
    return random.choices(values, weights=weights, k=1)[0]


def choose_payment_method():
    return weighted_choice(PAYMENT_METHODS)


def choose_installment(method: str, order_value: float) -> int:
    """
    Nakit kapıda / havale gibi yöntemlerde taksit mantıksız olabilir.
    Kartlarda sipariş tutarına göre taksit artabilir.
    """
    if method in ["bank_transfer", "cash_on_delivery", "digital_wallet"]:
        return 1

    if order_value < 500:
        return random.choices([1, 2, 3], weights=[0.75, 0.20, 0.05], k=1)[0]
    elif order_value < 1500:
        return random.choices([1, 2, 3, 6], weights=[0.45, 0.20, 0.20, 0.15], k=1)[0]
    else:
        return random.choices([1, 2, 3, 6, 9, 12], weights=[0.25, 0.15, 0.15, 0.20, 0.10, 0.15], k=1)[0]


def choose_status_for_order(order_row, attempt_no: int, total_attempts: int) -> str:
    """
    Sipariş durumuna ve deneme sırasına göre ödeme durumunu biraz daha gerçekçi üretir.
    """
    order_status_id = str(order_row.get("status_id", "100"))

    # İptal siparişlerde ödeme daha çok cancelled / refunded / failed olur
    if order_status_id == "104":
        return random.choices(
            ["cancelled", "failed", "refunded"],
            weights=[0.45, 0.35, 0.20],
            k=1
        )[0]

    # Son denemede başarılı olma ihtimalini artır
    if attempt_no == total_attempts:
        return random.choices(
            ["success", "failed", "pending"],
            weights=[0.82, 0.10, 0.08],
            k=1
        )[0]

    # Ara denemeler daha çok fail/pending olabilir
    return random.choices(
        ["failed", "pending", "success"],
        weights=[0.55, 0.25, 0.20],
        k=1
    )[0]


def parse_datetime_safe(value):
    return pd.to_datetime(value, errors="coerce", utc=True)


def load_orders(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Orders dosyası bulunamadı: {path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".json":
        df = pd.read_json(path)
    elif suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        raise ValueError("Desteklenmeyen dosya formatı. CSV / JSON / Parquet kullan.")

    required_cols = {"order_id", "order_value"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Orders dosyasında eksik kolon(lar) var: {missing}")

    if "timestamp" in df.columns:
        df["timestamp"] = df["timestamp"].apply(parse_datetime_safe)
    elif "order_timestamp" in df.columns:
        df["timestamp"] = df["order_timestamp"].apply(parse_datetime_safe)
    else:
        df["timestamp"] = pd.Timestamp.utcnow()

    return df


def generate_payment_rows_for_order(order_row: pd.Series) -> list[dict]:
    rows = []

    order_id = str(order_row["order_id"])
    order_value = float(order_row["order_value"])
    order_ts = order_row.get("timestamp", pd.Timestamp.utcnow())

    if pd.isna(order_ts):
        order_ts = pd.Timestamp.utcnow()

    # Bazı siparişlerde tek deneme, bazılarında retry olsun
    total_attempts = random.choices(
        [1, 2, 3],
        weights=[0.72, 0.22, 0.06],
        k=1
    )[0]

    payment_method = choose_payment_method()
    installment_count = choose_installment(payment_method, order_value)

    # Bazı alanları siparişten türetelim
    city_id = str(order_row.get("city_id", ""))
    customer_name = str(order_row.get("customer_name", ""))

    success_seen = False

    for attempt_no in range(1, total_attempts + 1):
        payment_status = choose_status_for_order(order_row, attempt_no, total_attempts)

        # Eğer önceki attempt success olduysa sonraki attempt oluşturma
        if success_seen:
            break

        # Timestamp: siparişten birkaç saniye/dakika/saat sonra
        payment_ts = order_ts + timedelta(
            minutes=random.randint(1, 180),
            seconds=random.randint(0, 59)
        )

        # Tutar mantığı
        if payment_status == "success":
            paid_amount = round(order_value, 2)
            success_seen = True
        elif payment_status == "refunded":
            paid_amount = round(order_value, 2)
        elif payment_status == "pending":
            # pending'de tutar çoğu zaman sipariş tutarı kadar görünür
            paid_amount = round(order_value, 2)
        else:
            # failed/cancelled için başarısız ödeme denemesi
            # bazen eksik/uyuşmayan tutar deneyebilir
            variation = random.uniform(0.70, 1.05)
            paid_amount = round(order_value * variation, 2)

        row = {
            "payment_id": str(uuid.uuid4()),
            "order_id": order_id,
            "attempt_no": attempt_no,
            "payment_method": payment_method,
            "installment_count": installment_count,
            "payment_status": payment_status,
            "paid_amount": paid_amount,
            "currency": random.choice(CURRENCIES),
            "payment_timestamp": payment_ts.isoformat(),
            "card_bank": random.choice(BANKS) if payment_method in ["credit_card", "debit_card"] else None,
            "is_refund": 1 if payment_status == "refunded" else 0,
            "fraud_flag": 1 if (payment_status == "failed" and random.random() < 0.08) else 0,

            # Analitik/debug için faydalı ek kolonlar
            "order_value": round(order_value, 2),
            "city_id": city_id,
            "customer_name": customer_name,
        }

        rows.append(row)

    return rows


def generate_payments(orders_df: pd.DataFrame) -> pd.DataFrame:
    payment_rows = []

    for _, order_row in orders_df.iterrows():
        payment_rows.extend(generate_payment_rows_for_order(order_row))

    payments_df = pd.DataFrame(payment_rows)

    # Kolon sırası
    ordered_cols = [
        "payment_id",
        "order_id",
        "attempt_no",
        "payment_method",
        "installment_count",
        "payment_status",
        "paid_amount",
        "currency",
        "payment_timestamp",
        "card_bank",
        "is_refund",
        "fraud_flag",
        "order_value",
        "city_id",
        "customer_name",
    ]

    payments_df = payments_df[ordered_cols]
    return payments_df


def main():
    print(f"Orders okunuyor: {ORDERS_PATH}")
    orders_df = load_orders(ORDERS_PATH)

    print(f"Toplam order sayısı: {len(orders_df)}")
    payments_df = generate_payments(orders_df)

    PAYMENTS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payments_df.to_csv(PAYMENTS_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Payments üretildi: {PAYMENTS_OUTPUT_PATH}")
    print(f"Toplam payment kaydı: {len(payments_df)}")
    print("\nÖrnek kayıtlar:")
    print(payments_df.head(10))


if __name__ == "__main__":
    main()