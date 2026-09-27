import pandas as pd
import numpy as np
import random
import string
import itertools
from datetime import datetime, timedelta

print("Generando ecosistema de Big Data (Empresa Padre) a escala corporativa...\n")

# ==========================================
# 1. GENERAR 150 CLIENTES CORPORATIVOS
# ==========================================
prefixes = ["Elite", "Pro", "Champion", "Prime", "Titan", "Velocity", "Active", "Dynamic", "Global", "National", "Urban", "Metro", "NextGen", "Supreme", "Alpha"]
suffixes = ["Sports", "Athletics", "Gear", "Fitness", "Outdoors", "Hub", "Store", "Emporium", "Mart", "Retail"]
customer_names = [f"{p} {s}" for p in prefixes for s in suffixes] # 150 combinaciones

clientes = []
for i, name in enumerate(customer_names):
    code = 70000000 + i
    market = "India"
    platform = random.choice(["Brick & Mortar", "E-Commerce", "Wholesale"])
    channel = random.choice(["Retailer", "Direct", "Distributor"])
    clientes.append([code, name, market, platform, channel])

df_cust = pd.DataFrame(clientes, columns=["customer_code", "customer", "market", "platform", "channel"])

# Inyectar suciedad en clientes
df_cust['customer'] = df_cust['customer'].apply(lambda x: f"  {x} " if random.random() > 0.8 else x)
df_cust.loc[df_cust.sample(frac=0.08).index, 'channel'] = np.nan 
df_cust['platform'] = df_cust['platform'].apply(lambda x: str(x).lower() if random.random() > 0.7 else x)
df_cust = pd.concat([df_cust, df_cust.sample(5)], ignore_index=True) # 5 Duplicados exactos
df_cust.to_csv("dirty_dim_customers.csv", index=False)
print(f"✅ dirty_dim_customers.csv creado ({len(df_cust)} clientes).")

# ==========================================
# 2. GENERAR 400 PRODUCTOS
# ==========================================
divisions = ['Archery', 'Badminton', 'Basketball', 'Boxing', 'Camping', 'Cricket', 'Cycling', 'Football', 'Tennis', 'Swimming', 'Running', 'Yoga']
categories = ['Equipment', 'Apparel', 'Accessories', 'Footwear', 'Training', 'Safety', 'Hydration', 'Recovery']
variants = ['Standard', 'Pro', 'Elite', 'Basic', 'Large', 'Medium', 'Small', 'Universal', 'Kids']

productos = []
for _ in range(400):
    div = random.choice(divisions)
    prefix = div[:4].upper()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"{prefix}{suffix}"
    cat = random.choice(categories)
    prod_name = f"{div} {cat} Series"
    var = random.choice(variants)
    productos.append([code, div, cat, prod_name, var])

df_prod = pd.DataFrame(productos, columns=["product_code", "division", "category", "product", "variant"])

# Inyectar suciedad en productos
df_prod.loc[df_prod.sample(frac=0.05).index, 'division'] = np.nan 
df_prod['category'] = df_prod['category'].replace({'Equipment': 'Equipmnt', 'Accessories': 'Accesories'}) 
df_prod = pd.concat([df_prod, df_prod.sample(15)], ignore_index=True) 
df_prod.to_csv("dirty_dim_products.csv", index=False)
print(f"✅ dirty_dim_products.csv creado ({len(df_prod)} productos).")

# ==========================================
# 3. GENERAR PRECIOS (2024 y 2025)
# ==========================================
precios = []
for code in df_prod['product_code'].unique():
    base_price = random.randint(500, 8000)
    precios.append([code, base_price, 2024])
    precios.append([code, base_price + random.randint(100, 800), 2025]) # Ajuste inflacionario

df_price = pd.DataFrame(precios, columns=["product_code", "price_inr", "year"])

# Inyectar suciedad en precios
idx_neg = df_price.sample(frac=0.04).index
df_price.loc[idx_neg, 'price_inr'] = df_price.loc[idx_neg, 'price_inr'] * -1 
df_price.loc[df_price.sample(frac=0.02).index, 'price_inr'] = 0 
df_price.to_csv("dirty_dim_gross_price.csv", index=False)
print(f"✅ dirty_dim_gross_price.csv creado ({len(df_price)} registros de precios).")

# ==========================================
# 4. GENERAR 300,000 ÓRDENES HISTÓRICAS (Ene 2024 - Nov 2025)
# ==========================================
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 11, 30)
days_between = (end_date - start_date).days

clientes_ids = df_cust['customer_code'].dropna().unique()
productos_ids = df_prod['product_code'].dropna().unique()

print("\nProcesando 300,000 registros históricos (esto puede tomar unos segundos)...")
fechas_base = [start_date + timedelta(days=random.randint(0, days_between)) for _ in range(300000)]
fechas_str = [f.strftime('%d/%m/%Y') if random.random() > 0.85 else f.strftime('%Y-%m-%d') for f in fechas_base]
prod_sample = random.choices(productos_ids, k=300000)
cust_sample = random.choices(clientes_ids, k=300000)
qty_sample = [random.randint(1, 150) for _ in range(300000)]

df_fact_full = pd.DataFrame({'date': fechas_str, 'product_code': prod_sample, 'customer_code': cust_sample, 'sold_quantity': qty_sample})

# Inyectar suciedad masiva en histórico
df_fact_full.loc[df_fact_full.sample(frac=0.02).index, 'sold_quantity'] *= -1 # 2% Negativos
df_fact_full.loc[df_fact_full.sample(frac=0.01).index, 'sold_quantity'] = np.nan # 1% Nulos
df_fact_full.loc[df_fact_full.sample(frac=0.005).index, 'product_code'] = "P_INVALIDO" # 0.5% Código Falso
df_fact_full = pd.concat([df_fact_full, df_fact_full.sample(2000)], ignore_index=True) # 2000 Duplicados

df_fact_full.to_csv("dirty_fact_orders_full.csv", index=False)
print(f"✅ dirty_fact_orders_full.csv creado ({len(df_fact_full)} órdenes históricas masivas).")

# ==========================================
# 5. GENERAR 31 ARCHIVOS INCREMENTALES (Diciembre 2025)
# ==========================================
print("\nGenerando carga diaria incremental (Diciembre 2025)...")
incremental_start = datetime(2025, 12, 1)

for i in range(31):
    current_date = incremental_start + timedelta(days=i)
    num_trans = random.randint(1000, 1500) # Volumen gigante: 1000 a 1500 ventas por día
    
    fechas_dia = [current_date.strftime('%d/%m/%Y') if random.random() > 0.85 else current_date.strftime('%Y-%m-%d') for _ in range(num_trans)]
    prod_dia = random.choices(productos_ids, k=num_trans)
    cust_dia = random.choices(clientes_ids, k=num_trans)
    qty_dia = [random.randint(1, 100) * (-1 if random.random() > 0.98 else 1) for _ in range(num_trans)]
    
    df_daily = pd.DataFrame({'date': fechas_dia, 'product_code': prod_dia, 'customer_code': cust_dia, 'sold_quantity': qty_dia})
    df_daily.to_csv(f"parent_orders_{current_date.strftime('%Y%m%d')}.csv", index=False)

print("✅ 31 archivos diarios incrementales creados (1,000+ órdenes por día).")
print("\n¡Ecosistema Big Data de Atlon generado con éxito!")