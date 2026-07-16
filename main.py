from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import csv
import json
import os
import time
import requests

from pydantic import BaseModel
from openai import OpenAI
from collections import defaultdict
from datetime import datetime

from identity.engine import build_trading_identity
from identity.coach_context import build_coach_context
from identity.coach_engine import (
    ask_mirror_coach,
    MIRRORCOACH_SYSTEM_PROMPT,
)
from identity.mirror_law import build_monthly_metrics
from identity.mirror_law.trade_reconstructor import reconstruct_closed_trades
from identity.trade_evidence import build_trade_evidence
from identity.knowledge_builder import build_mirror_knowledge_base

app = FastAPI(title="TradeMirror API")


class AnalyzeUrlRequest(BaseModel):
    file_url: str
   
class CoachRequest(BaseModel):
    question: str
    coach_context: object

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
    
@app.get("/coach-test")
def coach_test():
    return ask_mirror_coach(
        question="Responde únicamente: MirrorCoach está conectado correctamente.",
        coach_context={
            "test_mode": True,
            "source": "Railway direct test",
            "instruction": "Esta información se utiliza únicamente para verificar la conexión."
        }
    )

@app.post("/coach")
def coach(request: CoachRequest):
    context = request.coach_context

    if isinstance(context, str):
        context_text = context.strip()

        if context_text.startswith("MTCTX|"):
            context_text = context_text[len("MTCTX|"):]

        try:
            context = json.loads(context_text)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "error_code": "invalid_coach_context",
                "answer": (
                    "MirrorCoach no pudo leer la información del reporte."
                ),
            }

    if not isinstance(context, dict):
        return {
            "status": "error",
            "error_code": "invalid_coach_context",
            "answer": (
                "MirrorCoach recibió un contexto de reporte inválido."
            ),
        }

    return ask_mirror_coach(
        question=request.question,
        coach_context=context,
    )


def clean_line(line: str) -> str:
    return line.strip().strip(";").strip()


def to_float(value):
    try:
        if value is None or value == "" or value == "--":
            return 0.0

        text = str(value).strip()

        is_parenthesized_negative = (
            text.startswith("(")
            and text.endswith(")")
        )

        cleaned_value = (
            text
            .replace(",", "")
            .replace("$", "")
            .replace("%", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
        )

        number = float(cleaned_value)

        if is_parenthesized_negative:
            number = -abs(number)

        return number

    except Exception:
        return 0.0


def base_asset(symbol: str):
    if not symbol:
        return "UNKNOWN"

    return symbol.split()[0].upper()


def option_side(symbol: str):
    if not symbol:
        return "UNKNOWN"

    parts = symbol.split()

    if parts and parts[-1] in ["C", "P"]:
        return parts[-1]

    return "UNKNOWN"


def parse_csv_rows(text: str):
    """
    Parses IBKR CSV exports.

    IBKR sometimes wraps the real CSV record inside the first field and
    appends semicolon metadata at the end of the line.

    This function unwraps that format before returning the row.
    """

    rows = []

    for raw_line in text.splitlines():

        line = clean_line(raw_line)

        if not line:
            continue

        try:
            parsed = next(csv.reader([line]))

            # Normal CSV
            if len(parsed) > 1:
                rows.append(parsed)
                continue

            # IBKR wrapped row
            first = parsed[0]

            if "," in first:
                parsed = next(csv.reader([first]))
                rows.append(parsed)
                continue

            rows.append(parsed)

        except Exception:
            continue

    return rows


def parse_ibkr(text: str):
    """
    Parses the IBKR activity statement.

    Produces two existing data collections:

    1. orders
       Individual dated order records.

    2. closed_trades
       Final subtotal records containing realized P&L.

    Mirror Law reconstructs dated closed trades later by combining
    these two collections. This parser does not calculate Mirror Law.
    """

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
            if len(row) >= 7 and row[2].strip() == "Total":
                starting_capital = to_float(row[3])
                ending_capital = to_float(row[6])

        if section == "Cambio en NAV" and row_type == "Data":
            if len(row) >= 4 and row[2].strip() == "Comisiones":
                commissions_total = abs(
                    to_float(row[3])
                )

        if section == "Valor liquidativo" and row_type == "Data":
            if len(row) >= 3 and "%" in row[2]:
                period_return = row[2].strip()

        if (
            section == "Operaciones"
            and row_type == "Data"
            and len(row) >= 15
        ):
            discriminator = row[2].strip()

            if discriminator != "Order":
                continue

            symbol = row[5].strip()
            datetime_text = row[6].strip()

            trade_date = None
            trade_time = None

            try:
                parsed_datetime = datetime.strptime(
                    datetime_text,
                    "%Y-%m-%d, %H:%M:%S",
                )

                trade_date = (
                    parsed_datetime.date().isoformat()
                )

                trade_time = (
                    parsed_datetime.time().isoformat()
                )

            except Exception:
                trade_date = datetime_text
                trade_time = None

            orders.append(
                {
                    "symbol": symbol,
                    "asset_base": base_asset(symbol),
                    "option_side": option_side(symbol),
                    "date": trade_date,
                    "time": trade_time,
                    "quantity": to_float(row[7]),
                    "price": to_float(row[8]),
                    "transaction_value": to_float(row[10]),
                    "commission": to_float(row[11]),
                    "realized_pnl": to_float(row[13]),
                    "mtm_pnl": (
                        to_float(row[14])
                        if len(row) > 14
                        else 0
                    ),
                    "code": (
                        row[15].strip()
                        if len(row) > 15
                        else ""
                    ),
                }
            )

        if (
            section == "Operaciones"
            and row_type == "SubTotal"
            and len(row) >= 15
        ):
            symbol = row[5].strip()

            closed_trades.append(
                {
                    "symbol": symbol,
                    "asset_base": base_asset(symbol),
                    "asset": base_asset(symbol),
                    "ticker": base_asset(symbol),
                    "option_side": option_side(symbol),
                    "transaction_pnl": to_float(row[10]),
                    "commission": to_float(row[11]),
                    "realized_pnl": to_float(row[13]),
                    "pnl": to_float(row[13]),
                }
            )

    return {
        "orders": orders,
        "closed_trades": closed_trades,
        "starting_capital": starting_capital,
        "ending_capital": ending_capital,
        "commissions_total": commissions_total,
        "period_return": period_return,
    }


def calculate_metrics(parsed):
    """
    Calculates the existing global report metrics.

    This function continues using closed_trades exactly as before.
    Mirror Law does not change the current Identity or Blueprint inputs.
    """

    trades = parsed.get(
        "closed_trades",
        [],
    )

    total_trades = len(trades)

    winners = [
        trade
        for trade in trades
        if trade["realized_pnl"] > 0
    ]

    losers = [
        trade
        for trade in trades
        if trade["realized_pnl"] < 0
    ]

    net_pnl = sum(
        trade["realized_pnl"]
        for trade in trades
    )

    gross_profit = sum(
        trade["realized_pnl"]
        for trade in winners
    )

    gross_loss = abs(
        sum(
            trade["realized_pnl"]
            for trade in losers
        )
    )

    win_rate = (
        len(winners) / total_trades * 100
        if total_trades
        else 0
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss
        else None
    )

    by_asset = defaultdict(float)
    by_symbol = defaultdict(float)
    by_side = defaultdict(float)

    for trade in trades:
        by_asset[
            trade["asset_base"]
        ] += trade["realized_pnl"]

        by_symbol[
            trade["symbol"]
        ] += trade["realized_pnl"]

        by_side[
            trade["option_side"]
        ] += trade["realized_pnl"]

    best_asset = (
        max(
            by_asset.items(),
            key=lambda item: item[1],
        )
        if by_asset
        else (None, 0)
    )

    worst_asset = (
        min(
            by_asset.items(),
            key=lambda item: item[1],
        )
        if by_asset
        else (None, 0)
    )

    best_trade = (
        max(
            trades,
            key=lambda trade: trade["realized_pnl"],
        )
        if trades
        else None
    )

    worst_trade = (
        min(
            trades,
            key=lambda trade: trade["realized_pnl"],
        )
        if trades
        else None
    )

    average_winner = (
        gross_profit / len(winners)
        if winners
        else 0
    )

    average_loser = (
        -gross_loss / len(losers)
        if losers
        else 0
    )

    return {
        "total_trades": total_trades,
        "orders_count": len(
            parsed.get("orders", [])
        ),
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate": round(win_rate, 2),
        "net_pnl": round(net_pnl, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": (
            round(profit_factor, 2)
            if profit_factor is not None
            else None
        ),
        "average_winner": round(
            average_winner,
            2,
        ),
        "average_loser": round(
            average_loser,
            2,
        ),
        "best_asset": best_asset[0],
        "best_asset_pnl": round(
            best_asset[1],
            2,
        ),
        "worst_asset": worst_asset[0],
        "worst_asset_pnl": round(
            worst_asset[1],
            2,
        ),
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "starting_capital": round(
            parsed.get(
                "starting_capital",
                0,
            ),
            2,
        ),
        "ending_capital": round(
            parsed.get(
                "ending_capital",
                0,
            ),
            2,
        ),
        "commissions_total": round(
            parsed.get(
                "commissions_total",
                0,
            ),
            2,
        ),
        "period_return": parsed.get(
            "period_return"
        ),
        "asset_breakdown": {
            key: round(value, 2)
            for key, value in by_asset.items()
        },
        "symbol_breakdown": {
            key: round(value, 2)
            for key, value in by_symbol.items()
        },
        "side_breakdown": {
            key: round(value, 2)
            for key, value in by_side.items()
        },
    }


def detect_broker(text: str):
    if (
        "Interactive Brokers" in text
        or "Operaciones" in text
        or "Trades" in text
    ):
        return "IBKR"

    return "UNKNOWN"


def build_mirror_law_analysis(parsed: dict):
    """
    Builds the reconstructed trading-data pipeline:

    orders + closed_trades
        -> reconstructed dated trades
        -> monthly metrics
        -> deterministic trade evidence

    This does not modify Identity or Blueprint.
    """

    reconstruction = reconstruct_closed_trades(
        orders=parsed.get(
            "orders",
            [],
        ),
        closed_trades=parsed.get(
            "closed_trades",
            [],
        ),
    )

    reconstructed_trades = reconstruction.get(
        "trades",
        [],
    )

    monthly_analysis = build_monthly_metrics(
        reconstructed_trades
    )

    trade_evidence = build_trade_evidence(
        reconstructed_trades
    )

    return {
        "months": monthly_analysis.get(
            "months",
            [],
        ),
        "total_months": monthly_analysis.get(
            "total_months",
            0,
        ),
        "valid_trades": monthly_analysis.get(
            "valid_trades",
            0,
        ),
        "ignored_trades": monthly_analysis.get(
            "ignored_trades",
            0,
        ),

        "trade_evidence": trade_evidence,

        # Historial reconstruido completo.
        # Es la fuente detallada que MirrorCoach podrá consultar.
        "reconstructed_trades": reconstructed_trades,

        "reconstruction": {
            "reconstructed_trades_count": (
                reconstruction.get(
                    "reconstructed_trades",
                    0,
                )
            ),
            "unmatched_closed_trades_count": (
                reconstruction.get(
                    "unmatched_closed_trades_count",
                    0,
                )
            ),
            "symbols_with_orders_only_count": (
                reconstruction.get(
                    "symbols_with_orders_only_count",
                    0,
                )
            ),
            "unmatched_closed_trades": (
                reconstruction.get(
                    "unmatched_closed_trades",
                    [],
                )
            ),
            "symbols_with_orders_only": (
                reconstruction.get(
                    "symbols_with_orders_only",
                    [],
                )
            ),
        },

        "sample_reconstructed_trades": (
            reconstructed_trades[:5]
        ),
    }

def build_full_analysis_response(
    broker: str,
    filename: str,
    parsed: dict,
    metrics: dict,
):
    """
    Builds the complete API response.

    Existing response objects remain available:
    - metrics
    - identity
    - blueprint
    - mirror_insight
    - evolution

    Mirror Law and Coach Context are added as separate root objects.
    """

    closed_trades = parsed.get(
        "closed_trades",
        [],
    )

    identity = (
        build_trading_identity(
            metrics,
            closed_trades,
        )
        if metrics
        else {}
    )

    blueprint = (
        identity.get(
            "blueprint",
            {},
        )
        if identity
        else {}
    )

    mirror_insight = (
        identity.get(
            "mirror_insight",
            {},
        )
        if identity
        else {}
    )

    evolution = (
        identity.get(
            "evolution",
            {},
        )
        if identity
        else {}
    )

    mirror_law = build_mirror_law_analysis(
        parsed
    )

    mirror_knowledge_base = (
        build_mirror_knowledge_base(
            metrics=metrics,
            identity_payload=identity,
            mirror_law=mirror_law,
    )
    if metrics and identity
    else {}
    )

    coach_context = (
        build_coach_context(
            metrics=metrics,
            identity_payload=identity,
            mirror_law=mirror_law,
    )
    if metrics and identity
    else {}
    )

    if coach_context and mirror_knowledge_base:
        coach_context[
            "mirror_knowledge_base"
        ] = mirror_knowledge_base

    return {
        "status": "success",
        "broker": broker,
        "filename": filename,
        "metrics": metrics,
        "identity": identity,
        "blueprint": blueprint,
        "mirror_insight": mirror_insight,
        "evolution": evolution,
        "coach_context": coach_context,
      "coach_context_json": "MTCTX|" + json.dumps(
    coach_context,
    ensure_ascii=False,
    default=str,
   ),
        "mirror_knowledge_base": mirror_knowledge_base,
        
        "mirror_law": mirror_law,
        "sample_orders": parsed.get(
            "orders",
            [],
        )[:5],
        "sample_closed_trades": parsed.get(
            "closed_trades",
            [],
        )[:5],
    }

def empty_parsed_response():
    """
    Returns a consistent empty parser structure for unknown brokers.
    """

    return {
        "orders": [],
        "closed_trades": [],
        "starting_capital": 0,
        "ending_capital": 0,
        "commissions_total": 0,
        "period_return": None,
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
):
    content = await file.read()

    text = content.decode(
        "utf-8-sig",
        errors="ignore",
    )

    broker = detect_broker(text)

    if broker == "IBKR":
        parsed = parse_ibkr(text)
        metrics = calculate_metrics(parsed)

    else:
        parsed = empty_parsed_response()
        metrics = {}

    return build_full_analysis_response(
        broker=broker,
        filename=file.filename or "uploaded_file.csv",
        parsed=parsed,
        metrics=metrics,
    )


@app.post("/analyze-url")
async def analyze_url(
    payload: AnalyzeUrlRequest,
):
    file_url = payload.file_url

    if file_url.startswith("//"):
        file_url = "https:" + file_url

    response = requests.get(
        file_url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        timeout=30,
    )

    response.raise_for_status()

    text = response.content.decode(
        "utf-8-sig",
        errors="ignore",
    )

    broker = detect_broker(text)

    if broker == "IBKR":
        parsed = parse_ibkr(text)
        metrics = calculate_metrics(parsed)

    else:
        parsed = empty_parsed_response()
        metrics = {}

    filename = (
        file_url
        .split("?")[0]
        .rstrip("/")
        .split("/")[-1]
    )

    return build_full_analysis_response(
        broker=broker,
        filename=filename,
        parsed=parsed,
        metrics=metrics,
    )

@app.post("/coach-csv-test")
async def coach_csv_test(
    file: UploadFile = File(...),
):
    """
    Prueba aislada:

    1. Recibe el CSV.
    2. Lee el contenido como texto.
    3. Envía el texto directamente a MirrorCoach.
    4. Devuelve respuesta, tokens y tiempo.

    No utiliza:
    - OpenAI Files API
    - TradingReport
    - Identity
    - Blueprint
    - Mirror Law
    - Coach Context
    """

    started_at = time.perf_counter()

    api_key = os.getenv(
        "OPENAI_API_KEY",
        "",
    ).strip()

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.5",
    ).strip()

    if not api_key:
        return {
            "status": "error",
            "error_code": "missing_api_key",
            "answer": (
                "La variable OPENAI_API_KEY "
                "no está configurada."
            ),
        }

    filename = (
        file.filename
        or "trading_history.csv"
    )

    if not filename.lower().endswith(".csv"):
        return {
            "status": "error",
            "error_code": "invalid_file_type",
            "answer": (
                "Esta prueba acepta únicamente "
                "archivos CSV."
            ),
        }

    try:
        content = await file.read()

        if not content:
            return {
                "status": "error",
                "error_code": "empty_file",
                "answer": (
                    "El archivo CSV está vacío."
                ),
            }

        # Límite provisional para la prueba.
        max_file_size = 5 * 1024 * 1024

        if len(content) > max_file_size:
            return {
                "status": "error",
                "error_code": "file_too_large",
                "file_size_bytes": len(content),
                "answer": (
                    "El archivo supera el límite "
                    "provisional de 5 MB."
                ),
            }

        csv_text = content.decode(
            "utf-8-sig",
            errors="ignore",
        ).strip()

        if not csv_text:
            return {
                "status": "error",
                "error_code": "unreadable_csv",
                "answer": (
                    "El archivo no contiene texto "
                    "que pueda analizarse."
                ),
            }

        client = OpenAI(
            api_key=api_key,
            timeout=180.0,
            max_retries=2,
        )

        user_input = f"""
MIRRORCOACH DIRECT CSV ANALYSIS

FILENAME

{filename}

TRADER QUESTION

Analiza directamente el historial de trading incluido abajo.

Esta debe ser la primera respuesta que recibe el usuario
inmediatamente después de subir su CSV a MirrorTrader.

Investiga los datos antes de responder.

Necesito:

1. La conclusión más importante que revela el historial.
2. La evidencia numérica concreta que sostiene esa conclusión.
3. La principal fortaleza demostrable.
4. La principal fuga, debilidad o riesgo demostrable.
5. Una sola acción práctica prioritaria.
6. Las limitaciones reales del archivo o de la muestra.

REGLAS OBLIGATORIAS

- Utiliza exclusivamente la información del CSV.
- No inventes operaciones, fechas, resultados o métricas.
- No inventes comportamientos psicológicos.
- No atribuyas causas que los datos no puedan demostrar.
- Diferencia hechos calculados de interpretaciones.
- Indica claramente cualquier limitación del archivo.
- Responde en español.
- La respuesta debe ser directa y personalizada.
- No des señales de compra o venta.
- No predigas la dirección del mercado.

RAW CSV CONTENT

{csv_text}
""".strip()

        response = client.responses.create(
            model=model,
            instructions=MIRRORCOACH_SYSTEM_PROMPT,
            input=user_input,
            reasoning={
                "effort": "low",
            },
            max_output_tokens=5000,
        )

        answer = str(
            response.output_text or ""
        ).strip()

        usage = getattr(
            response,
            "usage",
            None,
        )

        input_tokens = (
            getattr(
                usage,
                "input_tokens",
                0,
            )
            if usage
            else 0
        )

        output_tokens = (
            getattr(
                usage,
                "output_tokens",
                0,
            )
            if usage
            else 0
        )

        total_tokens = (
            getattr(
                usage,
                "total_tokens",
                input_tokens + output_tokens,
            )
            if usage
            else input_tokens + output_tokens
        )

        processing_seconds = round(
            time.perf_counter() - started_at,
            3,
        )

        if not answer:
            incomplete_details = getattr(
                response,
                "incomplete_details",
                None,
            )

            return {
                "status": "error",
                "error_code": "empty_model_response",
                "model": model,
                "filename": filename,
                "response_status": getattr(
                    response,
                    "status",
                    None,
                ),
                "incomplete_details": (
                    str(incomplete_details)
                    if incomplete_details
                    else None
                ),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "processing_seconds": processing_seconds,
                "answer": (
                    "OpenAI procesó la solicitud, "
                    "pero no devolvió texto visible."
                ),
            }

        return {
            "status": "success",
            "test_type": "raw_csv_text_to_mirrorcoach",
            "model": model,
            "filename": filename,
            "file_size_bytes": len(content),
            "csv_characters": len(csv_text),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "processing_seconds": processing_seconds,
            "answer": answer,
        }

    except Exception as exc:
        processing_seconds = round(
            time.perf_counter() - started_at,
            3,
        )

        print(
            "MirrorCoach raw CSV error:",
            type(exc).__name__,
            str(exc),
        )

        return {
            "status": "error",
            "error_code": "raw_csv_request_failed",
            "exception_type": type(exc).__name__,
            "error_detail": str(exc),
            "processing_seconds": processing_seconds,
            "answer": (
                "No se pudo completar la prueba "
                "directa del CSV con MirrorCoach."
            ),
        }
