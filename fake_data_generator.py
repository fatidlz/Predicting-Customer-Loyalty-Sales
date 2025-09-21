#!/usr/bin/env python3
"""
retail_crm_data_generator.py

Generates fake CRM-style CSV datasets for a retail/coffee-like project (neutral brand):
- customers.csv
- products.csv
- transactions.csv
- redemptions.csv

Requirements:
    pip install pandas numpy

Usage:
    python retail_crm_data_generator.py

You can adjust parameters at the top of the file (number of customers, products, months, seed, etc.).
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# -------------------- CONFIG --------------------
OUT_DIR = "fake_retail_data_output"
N_CUSTOMERS = 2000
N_PRODUCTS = 50
MONTHS = 24  # how many months of history to generate
SEED = 42
INCLUDE_REDEMPTIONS = True

# distribution weights for loyalty tiers (None, Silver, Gold, Platinum)
LOYALTY_WEIGHTS = [0.4, 0.35, 0.2, 0.05]
CITIES = ["Vienna", "Graz", "Linz", "Salzburg", "Innsbruck", "Klagenfurt", "Bregenz", "Villach"]
GENDERS = ["F", "M", "Other"]

# expected lambda (approx) transactions per customer over entire period (Poisson mean)
TIER_LAMBDA_PER_PERIOD = {"Platinum": 36, "Gold": 20, "Silver": 10, "None": 4}

# -------------------- SETUP --------------------
random.seed(SEED)
np.random.seed(SEED)

os.makedirs(OUT_DIR, exist_ok=True)
now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start_date = (now - pd.DateOffset(months=MONTHS)).to_pydatetime()

# -------------------- CUSTOMERS --------------------
customer_ids = np.arange(1, N_CUSTOMERS + 1)

# join dates uniformly distributed between start_date and now
join_dates = [start_date + timedelta(days=int(random.random() * ((now - start_date).days + 1))) for _ in range(N_CUSTOMERS)]

tiers = list(np.random.choice(["None", "Silver", "Gold", "Platinum"], size=N_CUSTOMERS, p=LOYALTY_WEIGHTS))
ages = np.random.randint(18, 75, size=N_CUSTOMERS)
genders = list(np.random.choice(GENDERS, size=N_CUSTOMERS, p=[0.52, 0.47, 0.01]))
cities = list(np.random.choice(CITIES, size=N_CUSTOMERS))

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "join_date": pd.to_datetime(join_dates).strftime("%Y-%m-%d"),
    "loyalty_tier": tiers,
    "age": ages,
    "gender": genders,
    "city": cities,
    "email": [f"user{cid}@example.com" for cid in customer_ids]
})

# -------------------- PRODUCTS --------------------
product_types = ["Capsule", "Machine", "Accessory"]
flavors = ["Roma", "Arpeggio", "Livanto", "Volluto", "Cosi", "Ristretto", "Fortissio", "Indriya"]
machine_models = ["Essenza Mini", "Citiz", "Lattissima", "Vertuo", "Creatista"]
accessories = ["Milk Frother", "Tumbler", "Espresso Cup", "Cleaning Kit", "Descaler"]

products_list = []
for pid in range(1, N_PRODUCTS + 1):
    ptype = random.choices(product_types, weights=[0.7, 0.2, 0.1])[0]
    if ptype == "Capsule":
        flavor = random.choice(flavors)
        intensity = int(random.choice(list(range(1, 14))))
        # price per capsule in EUR
        price = max(0.25, round(np.random.normal(0.45, 0.08), 2))
        model_or_flavor = f"{flavor}"
    elif ptype == "Machine":
        flavor = None
        intensity = None
        price = max(49.0, round(np.random.normal(150, 60), 2))
        model_or_flavor = random.choice(machine_models)
    else:
        flavor = None
        intensity = None
        price = max(3.0, round(np.random.normal(20, 8), 2))
        model_or_flavor = random.choice(accessories)

    products_list.append({
        "product_id": pid,
        "product_type": ptype,
        "model_or_flavor": model_or_flavor,
        "flavor": flavor if flavor is not None else "",
        "intensity": intensity if intensity is not None else "",
        "price_eur": round(price, 2)
    })

products = pd.DataFrame(products_list)

# -------------------- TRANSACTIONS --------------------
transactions_rows = []
transaction_id = 1

for _, c in customers.iterrows():
    cust_id = int(c["customer_id"])
    tier = c["loyalty_tier"]
    join_dt = pd.to_datetime(c["join_date"]).to_pydatetime()
    # expected number of transactions (Poisson)
    expected = TIER_LAMBDA_PER_PERIOD.get(tier, 5)
    n_tx = np.random.poisson(lam=max(1, expected))

    # Some customers joined recently: reduce transactions for them
    days_since_join = (now - join_dt).days
    if days_since_join < 30:
        n_tx = max(0, int(n_tx * 0.2))

    for _ in range(n_tx):
        # random transaction date between join date and now
        span_days = max(1, (now - join_dt).days)
        tx_date = join_dt + timedelta(days=int(random.random() * span_days))
        prod = products.sample(1).iloc[0]
        quantity = int(np.random.choice([1, 2, 3], p=[0.85, 0.12, 0.03]))

        # make machine purchases rarer and often single quantity
        if prod.product_type == "Machine" and random.random() > 0.05:
            # most machine samples should be ignored — instead sample other product
            prod = products[products.product_type != "Machine"].sample(1).iloc[0]

        channel = random.choices(["Online", "Boutique", "App"], weights=[0.6, 0.25, 0.15])[0]
        total_amount = round(float(prod.price_eur) * quantity, 2)

        transactions_rows.append({
            "transaction_id": transaction_id,
            "customer_id": cust_id,
            "product_id": int(prod.product_id),
            "quantity": quantity,
            "transaction_date": tx_date.strftime("%Y-%m-%d"),
            "channel": channel,
            "total_amount_eur": total_amount
        })
        transaction_id += 1

transactions = pd.DataFrame(transactions_rows)
# sort and reset ids
if not transactions.empty:
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
    transactions = transactions.sort_values("transaction_date").reset_index(drop=True)
    transactions["transaction_id"] = np.arange(1, len(transactions) + 1)
    transactions["transaction_date"] = transactions["transaction_date"].dt.strftime("%Y-%m-%d")

# -------------------- LOYALTY REDEMPTIONS (OPTIONAL) --------------------
redemptions = pd.DataFrame(columns=["redemption_id", "customer_id", "redemption_date", "reward_type", "value_eur"]) if INCLUDE_REDEMPTIONS else None
if INCLUDE_REDEMPTIONS:
    redemption_rows = []
    reward_types = ["Discount", "Free Capsules", "Free Shipping", "Gift"]
    # 15% of customers redeem at least once
    n_redeemers = int(0.15 * N_CUSTOMERS)
    redeemers = customers.sample(n_redeemers, replace=False)
    rid = 1
    for _, rc in redeemers.iterrows():
        n_red = np.random.choice([1, 1, 2])  # mostly 1, sometimes 2
        join_dt = pd.to_datetime(rc["join_date"]).to_pydatetime()
        for i in range(n_red):
            span_days = max(1, (now - join_dt).days)
            red_date = join_dt + timedelta(days=int(random.random() * span_days))
            redemption_rows.append({
                "redemption_id": rid,
                "customer_id": int(rc["customer_id"]),
                "redemption_date": red_date.strftime("%Y-%m-%d"),
                "reward_type": random.choice(reward_types),
                "value_eur": round(float(np.random.choice([1.5, 3, 5, 10, 20])), 2)
            })
            rid += 1
    redemptions = pd.DataFrame(redemption_rows)

# -------------------- SAVE CSVs --------------------
customers.to_csv(os.path.join(OUT_DIR, "customers.csv"), index=False)
products.to_csv(os.path.join(OUT_DIR, "products.csv"), index=False)
transactions.to_csv(os.path.join(OUT_DIR, "transactions.csv"), index=False)
if INCLUDE_REDEMPTIONS and redemptions is not None:
    redemptions.to_csv(os.path.join(OUT_DIR, "redemptions.csv"), index=False)

print("Generated files in:", os.path.abspath(OUT_DIR))
print("- customers.csv -> rows:", len(customers))
print("- products.csv -> rows:", len(products))
print("- transactions.csv -> rows:", len(transactions))
if INCLUDE_REDEMPTIONS and redemptions is not None:
    print("- redemptions.csv -> rows:", len(redemptions))

# Optional: quick summary if run interactively
try:
    first_tx_date = transactions['transaction_date'].min() if not transactions.empty else 'N/A'
    last_tx_date = transactions['transaction_date'].max() if not transactions.empty else 'N/A'
    print(f"Transaction date range: {first_tx_date} to {last_tx_date}")
except Exception:
    pass

# End of file
