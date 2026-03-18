
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3
import os

# Initialize FastAPI app
app = FastAPI()

# Set up templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = 'database.db'

# Ensure the database is created
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE wallets (
        user_id TEXT,
        wallet_address TEXT PRIMARY KEY,
        created_at TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE transactions (
        transaction_id TEXT PRIMARY KEY,
        wallet_address TEXT,
        amount REAL,
        timestamp TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE analytics (
        wallet_address TEXT PRIMARY KEY,
        total_transactions INTEGER,
        total_value REAL
    )
    ''')
    # Insert mock data
    cursor.execute("INSERT INTO wallets VALUES ('user1', '0xABC123', ?)", (datetime.now().isoformat(),))
    cursor.execute("INSERT INTO transactions VALUES ('tx1', '0xABC123', 100.0, ?)", (datetime.now().isoformat(),))
    cursor.execute("INSERT INTO analytics VALUES ('0xABC123', 1, 100.0)")
    conn.commit()
    conn.close()

# Data models
class Wallet(BaseModel):
    user_id: str
    wallet_address: str
    created_at: datetime

class Transaction(BaseModel):
    transaction_id: str
    wallet_address: str
    amount: float
    timestamp: datetime

class Analytics(BaseModel):
    wallet_address: str
    total_transactions: int
    total_value: float

# API Endpoints
@app.get("/api/wallets", response_model=List[Wallet])
async def get_wallets():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wallets")
    wallets = cursor.fetchall()
    conn.close()
    return [Wallet(user_id=w[0], wallet_address=w[1], created_at=w[2]) for w in wallets]

@app.post("/api/wallets")
async def add_wallet(wallet: Wallet):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO wallets VALUES (?, ?, ?)", (wallet.user_id, wallet.wallet_address, wallet.created_at.isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Wallet already exists")
    finally:
        conn.close()
    return {"message": "Wallet added successfully"}

@app.get("/api/transactions", response_model=List[Transaction])
async def get_transactions(wallet_address: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE wallet_address = ?", (wallet_address,))
    transactions = cursor.fetchall()
    conn.close()
    return [Transaction(transaction_id=t[0], wallet_address=t[1], amount=t[2], timestamp=t[3]) for t in transactions]

@app.get("/api/analytics", response_model=Analytics)
async def get_analytics(wallet_address: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analytics WHERE wallet_address = ?", (wallet_address,))
    analytics = cursor.fetchone()
    conn.close()
    if analytics:
        return Analytics(wallet_address=analytics[0], total_transactions=analytics[1], total_value=analytics[2])
    else:
        raise HTTPException(status_code=404, detail="Analytics not found")

# HTML Endpoints
@app.get("/", response_class=HTMLResponse)
async def read_home(request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/wallets", response_class=HTMLResponse)
async def read_wallets(request):
    return templates.TemplateResponse("wallets.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def read_about(request):
    return templates.TemplateResponse("about.html", {"request": request})
