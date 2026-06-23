from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import csv
import io
import re
import requests
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime

app = FastAPI(title="TradeMirror API")
class AnalyzeUrlRequest(BaseModel):
    file_url: str
    
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

def clean_line(line: str) -> str:
    return line.strip().strip(";").strip()

def to_float(value):
    try:
        if value is None or value == "" or value == "--":
            return 0.0
        return float(str(value).replace(",", ""))
    except:
        return 0.0

def base_asset(symbol: str):
    if not symbol:
        return "UNKNOWN"
    return symbol.split()[0].upper()

def option_side(symbol: str):
    parts = symbol.split()
    if parts and parts[-1] in ["C", "P"]:
        return parts[-1]
    return "UNKNOWN"

def parse_csv_rows(text: str):
    rows = []
    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        try:
            parsed = next(csv.reader([line]))
            rows.append(parsed)
        except:
            continue
    return rows

def parse_ibkr(text: str):
    rows = parse_csv_rows(text)
    orders = []
    closed_trades = []

    starting_capital = 0
    ending_capital = 0
    commissions_total = 0
    period_return = None

    for row in rows:
        if len(row) < 2:
            continue

        section = row[0].strip()
        row_type = row[1].strip()

        if section == "Valor liquidativo" and row_type == "Data":
            if len(row) >= 7 and row[2] == "Total":
                starting_capital = to_float(row[3])
                ending_capital = to_float(row[6])

        if section == "Cambio en NAV" and row_type == "Data":
            if len(row) >= 4 and row[2] == "Comisiones":
                commissions_total = abs(to_float(row[3]))

        if section == "Valor liquidativo" and row_type == "Data":
            if len(row) >= 3 and "%" in row[2]:
                period_return = row[2]

        if section == "Operaciones" and row_type == "Data" and len(row) >= 15:
            discriminator = row[2].strip()
            if discriminator != "Order":
                continue

            symbol = row[5].strip()
            datetime_text = row[6].strip()

            date = None
            time = None
            try:
                dt = datetime.strptime(datetime_text, "%Y-%m-%d, %H:%M:%S")
                date = dt.date().isoformat()
                time = dt.time().isoformat()
            except:
                date = datetime_text

            quantity = to_float(row[7])
            trade_price = to_float(row[8])
            transaction_value = to_float(row[10])
            commission = to_float(row[11])
            realized_pnl = to_float(row[13])
            mtm_pnl = to_float(row[14]) if len(row) > 14 else 0
            code = row[15].strip() if len(row) > 15 else ""

            orders.append({
                "symbol": symbol,
                "asset_base": base_asset(symbol),
                "option_side": option_side(symbol),
                "date": date,
                "time": time,
                "quantity": quantity,
                "price": trade_price,
                "transaction_value": transaction_value,
                "commission": commission,
                "realized_pnl": realized_pnl,
                "mtm_pnl": mtm_pnl,
                "code": code
            })

        if section == "Operaciones" and row_type == "SubTotal" and len(row) >= 15:
            symbol = row[5].strip()
            transaction_pnl = to_float(row[10])
            commission = to_float(row[11])
            realized_pnl = to_float(row[13])

            closed_trades.append({
                "symbol": symbol,
                "asset_base": base_asset(symbol),
                "option_side": option_side(symbol),
                "transaction_pnl": transaction_pnl,
                "commission": commission,
                "realized_pnl": realized_pnl
            })

    return {
        "orders": orders,
        "closed_trades": closed_trades,
        "starting_capital": starting_capital,
        "ending_capital": ending_capital,
        "commissions_total": commissions_total,
        "period_return": period_return
    }

def calculate_metrics(parsed):
    trades = parsed["closed_trades"]

    total_trades = len(trades)
    winners = [t for t in trades if t["realized_pnl"] > 0]
    losers = [t for t in trades if t["realized_pnl"] < 0]

    net_pnl = sum(t["realized_pnl"] for t in trades)
    gross_profit = sum(t["realized_pnl"] for t in winners)
    gross_loss = abs(sum(t["realized_pnl"] for t in losers))

    win_rate = (len(winners) / total_trades * 100) if total_trades else 0
    profit_factor = gross_profit / gross_loss if gross_loss else None

    by_asset = defaultdict(float)
    by_symbol = defaultdict(float)
    by_side = defaultdict(float)

    for t in trades:
        by_asset[t["asset_base"]] += t["realized_pnl"]
        by_symbol[t["symbol"]] += t["realized_pnl"]
        by_side[t["option_side"]] += t["realized_pnl"]

    best_asset = max(by_asset.items(), key=lambda x: x[1]) if by_asset else (None, 0)
    worst_asset = min(by_asset.items(), key=lambda x: x[1]) if by_asset else (None, 0)

    best_trade = max(trades, key=lambda x: x["realized_pnl"]) if trades else None
    worst_trade = min(trades, key=lambda x: x["realized_pnl"]) if trades else None

    avg_winner = gross_profit / len(winners) if winners else 0
    avg_loser = -gross_loss / len(losers) if losers else 0

    return {
        "total_trades": total_trades,
        "orders_count": len(parsed["orders"]),
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate": round(win_rate, 2),
        "net_pnl": round(net_pnl, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor else None,
        "average_winner": round(avg_winner, 2),
        "average_loser": round(avg_loser, 2),
        "best_asset": best_asset[0],
        "best_asset_pnl": round(best_asset[1], 2),
        "worst_asset": worst_asset[0],
        "worst_asset_pnl": round(worst_asset[1], 2),
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "starting_capital": round(parsed["starting_capital"], 2),
        "ending_capital": round(parsed["ending_capital"], 2),
        "commissions_total": round(parsed["commissions_total"], 2),
        "period_return": parsed["period_return"],
        "asset_breakdown": {k: round(v, 2) for k, v in by_asset.items()},
        "symbol_breakdown": {k: round(v, 2) for k, v in by_symbol.items()},
        "side_breakdown": {k: round(v, 2) for k, v in by_side.items()},
    }

def detect_broker(text: str):
    if "Interactive Brokers" in text or "Operaciones" in text or "Trades" in text:
        return "IBKR"
    return "UNKNOWN"

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8-sig", errors="ignore")

    broker = detect_broker(text)

    if broker == "IBKR":
        parsed = parse_ibkr(text)
        metrics = calculate_metrics(parsed)
    else:
        parsed = {"orders": [], "closed_trades": []}
        metrics = {}

    return {
        "status": "success",
        "broker": broker,
        "filename": file.filename,
        "metrics": metrics,
        "sample_orders": parsed["orders"][:5],
        "sample_closed_trades": parsed["closed_trades"][:5]
    }
@app.post("/analyze-url")
async def analyze_url(payload: AnalyzeUrlRequest):
    file_url = payload.file_url

    if file_url.startswith("//"):
        file_url = "https:" + file_url

    response = requests.get(file_url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8-sig", errors="ignore")

    broker = detect_broker(text)

    if broker == "IBKR":
        parsed = parse_ibkr(text)
        metrics = calculate_metrics(parsed)
    else:
        parsed = {"orders": [], "closed_trades": []}
        metrics = {}

    filename = file_url.split("/")[-1]

    return {
        "status": "success",
        "broker": broker,
        "filename": filename,
        "metrics": metrics,
        "sample_orders": parsed["orders"][:5],
        "sample_closed_trades": parsed["closed_trades"][:5]
    }
