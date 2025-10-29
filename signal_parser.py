# signal_parser.py

import os, json, re, logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "config.json"

try:
    import google.generativeai as genai
    _HAS_GEMINI = True
except Exception:
    _HAS_GEMINI = False

def _load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _validate_struct(data):
    if not isinstance(data, dict):
        return None
    pair_raw = str(data.get("pair", "")).upper().replace(" ", "")
    m = re.match(r"^([A-Z]{2,10})/(USDT|USDC)$", pair_raw)
    if not m:
        return None
    pair = f"{m.group(1)}/{m.group(2)}"
    try:
        entry = float(data.get("entry"))
    except Exception:
        return None
    raw_targets = data.get("targets", [])
    if not isinstance(raw_targets, list) or not raw_targets:
        return None
    targets = []
    for t in raw_targets:
        try:
            v = float(t)
            if v > 0:
                targets.append(v)
        except Exception:
            continue
    targets = targets[:5]
    if not targets:
        return None
    try:
        stop_loss = float(data.get("stop_loss"))
    except Exception:
        return None
    side = (str(data.get("side") or "").lower() or None)
    if side not in ("long", "short"):
        side = None
    lev = data.get("leverage")
    try:
        leverage = int(lev) if lev is not None else None
    except Exception:
        leverage = None
    market = (str(data.get("market") or "").lower() or None)
    if market not in ("spot", "futures"):
        market = None
    return { "pair": pair, "entry": entry, "targets": targets, "stop_loss": stop_loss,
             "side": side, "leverage": leverage, "market": market }

def _regex_parse(message: str):
    try:
        pair_match = re.search(r"#?([A-Z]{2,10})/(USDT|USDC)", message, re.IGNORECASE)
        if not pair_match:
            return None
        pair = f"{pair_match.group(1).upper()}/{pair_match.group(2).upper()}"
        entry_match = re.search(r"(Entry\s+around|Entry\s+Point|Entry)\s*[:\-]?\s*([\d.]+)", message, re.IGNORECASE)
        if not entry_match:
            return None
        entry_price = float(entry_match.group(2))
        targets = []
        targets_block = re.search(r"(Targets?|TP)\s*[:\-]?\s*(.+)", message, re.IGNORECASE | re.DOTALL)
        if targets_block:
            nums = re.findall(r"[\d.]+", targets_block.group(2))
            targets = list(map(float, nums)) if nums else []
        stop_match = re.search(r"(Stop\s*Loss|SL)\s*[:\-]?\s*([\d.]+)", message, re.IGNORECASE)
        stop_loss = float(stop_match.group(2)) if stop_match else None
        if not targets or stop_loss is None:
            return None
        side = None
        if re.search(r"\bshort\b|\bsell\b", message, re.IGNORECASE): side = "short"
        elif re.search(r"\blong\b|\bbuy\b", message, re.IGNORECASE): side = "long"
        lev = None
        lev_m = re.search(r"leverage\s*[:\-]?\s*(\d+)\s*x", message, re.IGNORECASE)
        if lev_m: lev = int(lev_m.group(1))
        market = "futures" if re.search(r"futures?", message, re.IGNORECASE) or side == "short" or lev else None
        return _validate_struct({ "pair": pair, "entry": entry_price, "targets": targets,
                                  "stop_loss": stop_loss, "side": side, "leverage": lev, "market": market })
    except Exception as e:
        logging.error(f"Regex parse error: {e}")
        return None

def _gemini_parse(message: str):
    if not _HAS_GEMINI:
        return None
    cfg = _load_config()
    api_key = (cfg.get("gemini_api_key") or "").strip()
    model_name = (cfg.get("gemini_model") or "gemini-1.5-flash").strip()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        system = (
            "Extract a crypto trading signal into strict JSON with keys: "
            "pair, entry, targets, stop_loss, side, leverage, market. "
            "Return ONLY JSON."
        )
        resp = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": system + "\n\nText:\n" + message}]}],
            generation_config={"temperature": 0.0, "response_mime_type": "application/json"},
        )
        raw = getattr(resp, "text", "") or ""
        if not raw.strip(): return None
        return _validate_struct(json.loads(raw))
    except Exception as e:
        logging.error(f"Gemini parsing error: {e}")
        return None

def parse_signal(message: str):
    data = _gemini_parse(message)
    if data:
        logging.info(f"Signal parsed via Gemini: {data}")
        return data
    data = _regex_parse(message)
    if data:
        logging.info(f"Signal parsed via regex: {data}")
        return data
    logging.warning("No valid signal could be parsed.")
    return False
