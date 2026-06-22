from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import csv
import io
import re
from collections import defaultdict

app = FastAPI(title="TradeMirror API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "TradeMirror API Online"}

@app.get("/health")
def health():
    return {"status": "ok"}

def detect_broker(text: str):
    if "Interactive Brokers" in text or "Operaciones" in text or "Trades" in text:
        return "IBKR"
    return "UNKNOWN"

def extract_base_asset(symbol: str):
    if not symbol:
        return "UNKNOWN"
    first = symbol.split()[0]
    return re.sub(r"[^A-Z]", "", first.upper()) or "UNKNOWN"

def parse_ibkr_csv(text: str):
    trades = []

    reader = csv.reader(io.StringIO(text))
    for row in reader:
        if len(row) < 10:
            continue

        section = row[0].strip()
        row_type = row[1].strip() if len(row) > 1 else ""
        trade_type = row[2].strip() if len(row) > 2 else ""

        is_trade = (
            section in ["Operaciones", "Trades"]
            and row_type == "Data"
            and trade_type == "Order"
        )

        if not is_trade:
            continue

        try:
            symbol = row[5].strip()
            date = row[6].strip()
            time = row[7].strip()
            quantity = float(row[8]) if row[8] else 0
            price = float(row[9]) if row[9] else 0

            pnl = None
            for value in reversed(row):
                try:
                    num = float(value)
                    if abs(num) > 0:
                        pnl = num
                        break
                except:
                    pass

            if pnl is None:
                pnl = 0

            trades.append({
                "symbol": symbol,
                "asset_base": extract_base_asset(symbol),
                "date": date,
                "time": time,
                "quantity": quantity,
                "price": price,
                "pnl": pnl,
                "raw": row
            })
        except:
            continue

    return trades

def calculate_metrics(trades):
    total_trades = len(trades)
    winners = [t for t in trades if t["pnl"] > 0]
    losers = [t for t in trades if t["pnl"] < 0]

    net_pnl = sum(t["pnl"] for t in trades)
    gross_profit = sum(t["pnl"] for t in winners)
    gross_loss = abs(sum(t["pnl"] for t in losers))

    win_rate = (len(winners) / total_trades * 100) if total_trades else 0
    profit_factor = (gross_profit / gross_loss) if gross_loss else None

    by_asset = defaultdict(float)
    for t in trades:
        by_asset[t["asset_base"]] += t["pnl"]

    best_asset = None
    worst_asset = None

    if by_asset:
        best_asset = max(by_asset.items(), key=lambda x: x[1])
        worst_asset = min(by_asset.items(), key=lambda x: x[1])

    return {
        "total_trades": total_trades,
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate": round(win_rate, 2),
        "net_pnl": round(net_pnl, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor else None,
        "best_asset": best_asset[0] if best_asset else None,
        "best_asset_pnl": round(best_asset[1], 2) if best_asset else 0,
        "worst_asset": worst_asset[0] if worst_asset else None,
        "worst_asset_pnl": round(worst_asset[1], 2) if worst_asset else 0,
        "asset_breakdown": {
            asset: round(pnl, 2) for asset, pnl in by_asset.items()
        }
    }

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    broker = detect_broker(text)

    if broker == "IBKR":
        trades = parse_ibkr_csv(text)
    else:
        trades = []

    metrics = calculate_metrics(trades)

    return {
        "status": "success",
        "broker": broker,
        "filename": file.filename,
        "metrics": metrics,
        "sample_trades": trades[:5]
    }
