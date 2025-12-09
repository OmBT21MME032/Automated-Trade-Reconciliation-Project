import pandas as pd
import numpy as np
import random

# --- CONFIGURATION ---
NUM_TRADES = 500
OUTPUT_INTERNAL = 'internal_ledger.csv'
OUTPUT_BANK = 'bank_statement.csv'

# Setup
random.seed(42)
tickers = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN', 'BHARTIARTL']
sides = ['BUY', 'SELL']
currencies = ['INR', 'USD']

print(f"Generating {NUM_TRADES} trade records...")

# --- GENERATE INTERNAL LEDGER (The "Truth") ---
internal_data = []
for i in range(1001, 1001 + NUM_TRADES):
    trade_id = f"TRD-{i}"
    ticker = random.choice(tickers)
    side = random.choice(sides)
    qty = random.randrange(10, 1000, 10) # Multiples of 10
    price = round(random.uniform(500, 3500), 2)
    currency = random.choice(currencies)
    
    internal_data.append([trade_id, ticker, side, qty, price, currency])

df_internal = pd.DataFrame(internal_data, columns=['Trade_ID', 'Ticker', 'Side', 'Qty', 'Price', 'Currency'])
df_internal.to_csv(OUTPUT_INTERNAL, index=False)

# --- GENERATE BANK STATEMENT (With Errors) ---
# We copy internal data but introduce 4 types of "Breaks" (Errors)
bank_data = []

for row in internal_data:
    trade_id, ticker, side, qty, price, currency = row
    
    # Randomly introduce errors (15% chance of an error)
    chance = random.random()
    
    if chance < 0.05:
        # TYPE 1: MISSING IN BANK (Trade failed downstream)
        continue 
        
    elif chance < 0.10:
        # TYPE 2: PRICE MISMATCH (Bank has different price)
        # Add random noise to price
        price = round(price * random.uniform(0.95, 1.05), 2)
        
    elif chance < 0.15:
        # TYPE 3: QUANTITY MISMATCH (Partial fill)
        qty = qty - 10 
        
    # TYPE 4: Currency/Ticker mismatch (Rare) - let's skip for simplicity
    
    bank_data.append([trade_id, ticker, side, qty, price, currency])

# Add some "Zombie Trades" (Present in Bank but missing Internally)
for i in range(5):
    trade_id = f"BANK-ONLY-{i}"
    bank_data.append([trade_id, "UNKNOWN", "BUY", 100, 1000.00, "INR"])

df_bank = pd.DataFrame(bank_data, columns=['Trade_ID', 'Ticker', 'Side', 'Qty', 'Price', 'Currency'])
df_bank.to_csv(OUTPUT_BANK, index=False)

print("✅ generated: 'internal_ledger.csv' & 'bank_statement.csv'")