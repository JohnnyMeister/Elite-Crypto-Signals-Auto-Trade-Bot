# trader.py

import logging, json, os
from typing import List, Tuple
from binance.client import Client
from binance.exceptions import BinanceAPIException
from telegram_alert import send_telegram_message, send_telegram_error

logging.basicConfig(level=logging.INFO)
CONFIG_FILE = "config.json"

# ---------------- Config ----------------
def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("config.json not found. Create it first.")
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

def get_binance_client(cfg, test_mode: bool = False):
    if test_mode:
        return None
    return Client(cfg["binance_api_key"], cfg["binance_api_secret"])

# --------------- Spot helpers ---------------
def symbol_exists_spot(symbol: str, client) -> bool:
    try:
        info = client.get_exchange_info()
        return symbol.upper() in [s["symbol"] for s in info["symbols"]]
    except Exception as e:
        logging.error(f"Failed to check spot symbol: {e}")
        return False

def get_usdt_free_spot(client) -> float:
    acct = client.get_account()
    for b in acct["balances"]:
        if b["asset"].upper() == "USDT":
            return float(b["free"])
    return 0.0

# ------------- Futures helpers -------------
def symbol_exists_futures(symbol: str, client) -> bool:
    try:
        info = client.futures_exchange_info()
        return symbol.upper() in [s["symbol"] for s in info["symbols"]]
    except Exception as e:
        logging.error(f"Failed to check futures symbol: {e}")
        return False

def get_usdt_free_futures(client) -> float:
    bal = client.futures_account_balance()
    for b in bal:
        if b.get("asset", "").upper() == "USDT":
            return float(b.get("balance", 0.0))
    return 0.0

def futures_change_leverage(client, symbol: str, leverage: int):
    return client.futures_change_leverage(symbol=symbol, leverage=max(1, int(leverage)))

def futures_last_price(client, symbol: str) -> float:
    t = client.futures_symbol_ticker(symbol=symbol)
    return float(t["price"])

# ------------- Targets & sizing -------------
def load_target_selection(cfg: dict):
    sel = cfg.get("target_selection")
    if isinstance(sel, dict):
        return { "T1": bool(sel.get("T1", True)), "T2": bool(sel.get("T2", True)),
                 "T3": bool(sel.get("T3", False)), "T4": bool(sel.get("T4", False)) }
    return { "T1": bool(cfg.get("buy_T1", True)), "T2": bool(cfg.get("buy_T2", True)),
             "T3": bool(cfg.get("buy_T3", False)), "T4": bool(cfg.get("buy_T4", False)) }

def apply_selection(targets: List[float], selection: dict) -> Tuple[List[float], List[float]]:
    base = [0.30, 0.30, 0.20, 0.20]
    chosen, w = [], []
    for i in range(min(4, len(targets))):
        if selection.get(f"T{i+1}", False):
            chosen.append(targets[i])
            w.append(base[i])
    if not chosen:
        return [], []
    s = sum(w)
    return chosen, [x/s for x in w]

def split_quantities(total_qty: float, weights: List[float]) -> List[float]:
    per, acc = [], 0.0
    for i, w in enumerate(weights):
        if i < len(weights) - 1:
            q = round(total_qty * w, 6)
            per.append(q); acc += q
        else:
            per.append(round(max(total_qty - acc, 0.0), 6))
    return per

# ------------- Spot path -------------
def execute_spot(cfg, symbol: str, entry_price: float, sel_targets: List[float], stop_loss: float,
                 test_mode: bool, sel_weights: List[float]) -> str:
    try:
        client = get_binance_client(cfg, test_mode)
        if test_mode:
            usdt_free = 1000.0; avg_price = entry_price
        else:
            if not symbol_exists_spot(symbol, client):
                msg = f"Spot symbol not found: {symbol}"
                logging.error(msg); send_telegram_error(msg, cfg); return msg
            usdt_free = get_usdt_free_spot(client)
            avg_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
        if usdt_free <= 0:
            msg = "Insufficient USDT balance on Spot."
            logging.error(msg); send_telegram_error(msg, cfg); return msg
        quote_amount = round(usdt_free * 0.15, 2)
        if quote_amount <= 0:
            msg = "Computed Spot allocation (15%) is zero."
            logging.error(msg); send_telegram_error(msg, cfg); return msg
        qty_total = round(quote_amount / avg_price, 6)
        if test_mode:
            plan = (f"[TEST][SPOT] BUY {symbol}: {quote_amount} USDT @ ~{avg_price} -> qty≈{qty_total} | "
                    f"TPs={sel_targets} | SL={stop_loss} | weights={sel_weights}")
            logging.info(plan); return plan
        buy_order = client.order_market_buy(symbol=symbol, quoteOrderQty=str(quote_amount))
        filled_qty = 0.0
        if "executedQty" in buy_order:
            try: filled_qty = float(buy_order.get("executedQty", 0.0))
            except Exception: filled_qty = 0.0
        if filled_qty <= 0:
            for fill in buy_order.get("fills", []): filled_qty += float(fill.get("qty", 0.0))
        if filled_qty <= 0: filled_qty = qty_total
        per_qty = split_quantities(filled_qty, sel_weights)
        oco_ids = []
        for i, (tp, q) in enumerate(zip(sel_targets, per_qty), start=1):
            if q <= 0: continue
            oco = client.create_oco_order(
                symbol=symbol, side="SELL", quantity=str(q), price=str(tp),
                stopPrice=str(stop_loss), stopLimitPrice=str(stop_loss), stopLimitTimeInForce="GTC",
            )
            oco_ids.append(oco.get("orderListId"))
        note = f"[SPOT] Buy {symbol} OK | qty={filled_qty} | TPs={sel_targets} | SL={stop_loss} | OCOs={oco_ids}"
        send_telegram_message(note, cfg)
        return f"[REAL][SPOT] Buy OK, {len(oco_ids)} OCOs created."
    except BinanceAPIException as e:
        err = f"Spot Binance API error: {e}"
        logging.error(err); send_telegram_error(err, cfg); return err
    except Exception as e:
        err = f"Spot unexpected error: {e}"
        logging.error(err); send_telegram_error(err, cfg); return err

# ------------- Futures path -------------
def execute_futures(cfg, symbol: str, side: str, leverage: int,
                    sel_targets: List[float], stop_loss: float,
                    test_mode: bool, sel_weights: List[float]) -> str:
    try:
        client = get_binance_client(cfg, test_mode)
        working_type = cfg.get("futures_working_type", "MARK_PRICE")
        if test_mode:
            usdt_free = 1000.0; price = 100.0
        else:
            if not symbol_exists_futures(symbol, client):
                msg = f"Futures symbol not found: {symbol}"
                logging.error(msg); send_telegram_error(msg, cfg); return msg
            lev = int(leverage or cfg.get("futures_default_leverage", 5))
            try:
                futures_change_leverage(client, symbol, lev)
            except Exception as e:
                send_telegram_error(f"Failed to set leverage {lev}x on {symbol}: {e}", cfg); return f"{e}"
            price = futures_last_price(client, symbol)
            usdt_free = get_usdt_free_futures(client)
        if usdt_free <= 0:
            msg = "Insufficient USDT balance on Futures."
            logging.error(msg); send_telegram_error(msg, cfg); return msg
        lev = int(leverage or cfg.get("futures_default_leverage", 5))
        margin = round(usdt_free * 0.15, 2)
        if margin <= 0:
            msg = "Computed Futures margin (15%) is zero."
            logging.error(msg); send_telegram_error(msg, cfg); return msg
        notional = margin * lev
        qty_total = round(notional / price, 3)
        entry_side = "BUY" if side == "long" else "SELL"
        close_side = "SELL" if side == "long" else "BUY"
        if test_mode:
            plan = (f"[TEST][FUTURES] {entry_side} {symbol}: margin={margin} USDT, lev={lev}, px~{price} -> qty≈{qty_total} | "
                    f"TPs={sel_targets} | SL={stop_loss} | weights={sel_weights} | workingType={working_type}")
            logging.info(plan); return plan
        entry = client.futures_create_order(symbol=symbol, side=entry_side, type="MARKET", quantity=str(qty_total))
        per_qty = split_quantities(qty_total, sel_weights)
        tp_ids = []
        for i, (tp, q) in enumerate(zip(sel_targets, per_qty), start=1):
            if q <= 0: continue
            tp_order = client.futures_create_order(
                symbol=symbol, side=close_side, type="TAKE_PROFIT", timeInForce="GTC",
                price=str(tp), stopPrice=str(tp), quantity=str(q), reduceOnly=True,
                workingType=working_type,
            )
            tp_ids.append(tp_order.get("orderId"))
        sl_order = client.futures_create_order(
            symbol=symbol, side=close_side, type="STOP_MARKET",
            stopPrice=str(stop_loss), reduceOnly=True, closePosition=True,
            workingType=working_type,
        )
        note = f"[FUTURES] {entry_side} {symbol} OK | qty={qty_total} | TPs={sel_targets} | SL={stop_loss} | TP IDs={tp_ids}"
        send_telegram_message(note, cfg)
        return f"[REAL][FUTURES] Entry OK, {len(tp_ids)} TP orders + 1 SL created."
    except BinanceAPIException as e:
        err = f"Futures Binance API error: {e}"
        logging.error(err); send_telegram_error(err, cfg); return err
    except Exception as e:
        err = f"Futures unexpected error: {e}"
        logging.error(err); send_telegram_error(err, cfg); return err

# ------------- Public -------------
def execute_trade(
    pair: str,
    entry_price: float,
    targets: List[float] = None,
    stop_loss: float = None,
    side: str = None,
    leverage: int = None,
    market: str = None
):
    cfg = load_config()
    test_mode = cfg.get("test_mode", True)
    if not targets or stop_loss is None:
        msg = f"Incomplete signal for {pair}: missing targets or stop loss."
        logging.warning(msg); 
        if not test_mode: send_telegram_error(msg, cfg)
        return msg
    selection = load_target_selection(cfg)
    sel_targets, sel_weights = apply_selection(targets, selection)
    if not sel_targets:
        msg = f"No targets selected for {pair} (check target_selection in config)."
        logging.warning(msg); 
        if not test_mode: send_telegram_error(msg, cfg)
        return msg

    # Auto selection logic
    symbol = pair.replace("/", "").upper()
    requested = (market or cfg.get("trade_mode", "auto")).strip().lower()
    side_norm = (side or "long").strip().lower()
    try:
        client = get_binance_client(cfg, test_mode)
        spot_ok = futures_ok = True
        if not test_mode and client:
            spot_ok = symbol_exists_spot(symbol, client)
            futures_ok = symbol_exists_futures(symbol, client)
    except Exception:
        spot_ok = futures_ok = True

    def run_spot():
        return execute_spot(cfg, symbol, entry_price, sel_targets, stop_loss, test_mode, sel_weights)
    def run_futs():
        return execute_futures(cfg, symbol, side_norm, leverage, sel_targets, stop_loss, test_mode, sel_weights)

    # Priority: explicit market -> auto inference
    if requested == "spot":
        if spot_ok:
            return run_spot()
        msg = f"Spot symbol not found: {symbol}."
        if futures_ok:
            send_telegram_message(msg + " Switching to Futures automatically.", cfg)
            return run_futs()
        send_telegram_error(msg + " Also not on Futures.", cfg)
        return msg
    if requested == "futures":
        if futures_ok:
            return run_futs()
        msg = f"Futures symbol not found: {symbol}."
        if spot_ok and side_norm != "short":
            send_telegram_message(msg + " Switching to Spot automatically.", cfg)
            return run_spot()
        send_telegram_error(msg + " Also not on Spot or side incompatible.", cfg)
        return msg

    # Auto mode
    if side_norm == "short" or leverage:
        if futures_ok:
            return run_futs()
        send_telegram_error(f"Auto selected Futures but symbol not found: {symbol}.", cfg)
        return f"Futures symbol not found: {symbol}"
    # default long spot
    if spot_ok:
        return run_spot()
    if futures_ok:
        send_telegram_message("Auto switching to Futures (Spot not available).", cfg)
        return run_futs()
    msg = f"Symbol {symbol} not listed on Spot or Futures."
    send_telegram_error(msg, cfg)
    return msg
