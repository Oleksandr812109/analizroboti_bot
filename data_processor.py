import pandas as pd
from datetime import datetime

def process_orders(orders):
    """
    Приймає список userTrades (orders) з Binance Futures API.
    Повертає DataFrame лише з закритими угодами (realizedPnl != 0) для експорту в Excel.
    """
    processed = []

    for order in orders:
        realized_pnl = safe_float(order.get("realizedPnl"))
        # Пропускати всі угоди, де немає реалізованого PnL (ще не закриті)
        if realized_pnl is None or realized_pnl == 0:
            continue

        dt_open = ts_to_str(order.get("time"))
        symbol = order.get("symbol")
        side = order.get("side")
        price = safe_float(order.get("price"))

        # LONG/SHORT логіка: якщо SELL з realizedPnl, то це закриття LONG, якщо BUY — закриття SHORT
        direction = "SHORT" if side == "BUY" else "LONG"

        stop_loss = None
        take_profit = None

        # Вважаємо, що дата закриття = дата цієї trade
        close_time = dt_open

        processed.append({
            "Дата / Час": dt_open,
            "Валютна пара": symbol,
            "Тип ордера (LONG / SHORT)": direction,
            "Ціна входу": price,
            "Стоп-лос": stop_loss,
            "Тейк-профіт": take_profit,
            "Час закриття ордера": close_time,
            "Реалізований PnL": realized_pnl,
        })

    columns = [
        "Дата / Час",
        "Валютна пара",
        "Тип ордера (LONG / SHORT)",
        "Ціна входу",
        "Стоп-лос",
        "Тейк-профіт",
        "Час закриття ордера",
        "Реалізований PnL",
    ]
    df = pd.DataFrame(processed, columns=columns)
    return df

def ts_to_str(timestamp):
    """
    Перетворює мілісекундний таймстамп Binance у строку дати/часу UTC.
    """
    if not timestamp:
        return ""
    if isinstance(timestamp, str):
        try:
            timestamp = float(timestamp)
        except Exception:
            return ""
    try:
        return datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""

def safe_float(val):
    """
    Безпечне перетворення у float.
    """
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
