"""
Fetch Japanese market data: indices and stocks.
All sources are free and require no API key.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
TIMEOUT = 20

# Yahoo Finance has no TOPIX sub-indices, so those come from JPX's own quote service.
INDEX_SOURCES = {
    "N225": ("yahoo", "^N225"),
    "TOPIX": ("jpx", "151"),
    "CORE30": ("jpx", "171"),
    "TOPIX100": ("jpx", "173"),
}

JP_NAMES = {
    "N225": "日経平均",
    "TOPIX": "TOPIX",
    "CORE30": "TOPIX Core30",
    "TOPIX100": "TOPIX 100",
    "8306": "三菱UFJ",
    "7203": "トヨタ自動車",
    "9984": "ソフトバンクG",
}


def _num(s: Any) -> float:
    return float(str(s).replace(",", "").replace("+", ""))


def fetch_yahoo(yahoo_symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch the latest daily quote for any Yahoo Finance symbol."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(yahoo_symbol)}?range=10d&interval=1d"
        res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()
        result = res.json()["chart"]["result"][0]
        meta, q = result["meta"], result["indicators"]["quote"][0]
        days = [i for i, c in enumerate(q["close"]) if c is not None]
        if not days:
            return None
        last = days[-1]

        close = float(meta.get("regularMarketPrice") or q["close"][last])
        prev_close = float(q["close"][days[-2]]) if len(days) > 1 else close
        change = close - prev_close
        volumes = [q["volume"][i] or 0 for i in days[-5:]]
        # Session date in the exchange's own timezone
        date = datetime.fromtimestamp(meta["regularMarketTime"] + meta["gmtoffset"], timezone.utc)

        return {
            "name": meta.get("shortName") or yahoo_symbol,
            "date": date.strftime("%Y-%m-%d"),
            "close": round(close, 2),
            "prev_close": round(prev_close, 2),
            "open": round(float(q["open"][last] or close), 2),
            "high": round(float(q["high"][last] or close), 2),
            "low": round(float(q["low"][last] or close), 2),
            "change": round(change, 2),
            "change_pct": round(change / prev_close * 100, 2) if prev_close else 0.0,
            "volume": int(volumes[-1]),
            "avg_volume_5d": int(sum(volumes) / len(volumes)),
        }
    except Exception as e:
        logger.error(f"Error fetching Yahoo data for {yahoo_symbol}: {e}")
        return None


def parse_jpx_index(payload: Dict[str, Any], qcode: str) -> Dict[str, Any]:
    d = payload["section1"]["data"][qcode]
    close, change = _num(d["DPP"]), _num(d["DYWP"])
    return {
        "name": d["NAME_DISP"],
        "date": d["ZXD"].replace("/", "-"),
        "close": close,
        "prev_close": round(close - change, 2),
        "open": _num(d["DOP"]),
        "high": _num(d["DHP"]),
        "low": _num(d["DLP"]),
        "change": change,
        "change_pct": _num(d["DYRP"]),
    }


def fetch_jpx_index(qcode: str) -> Optional[Dict[str, Any]]:
    """Fetch a TOPIX-family index from JPX (20-minute delayed, final after the close)."""
    try:
        url = f"https://quote.jpx.co.jp/jpxhp/jcgi/wrap/qjsonp.aspx?F=ctl/index&qcode={qcode}"
        res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()
        return parse_jpx_index(res.json(), qcode)
    except Exception as e:
        logger.error(f"Error fetching JPX index {qcode}: {e}")
        return None


def fetch_symbol_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch an index (N225, TOPIX, CORE30, TOPIX100) or a TSE stock by its code (e.g. 7203).
    """
    source, code = INDEX_SOURCES.get(symbol, ("yahoo", f"{symbol}.T"))
    data = fetch_jpx_index(code) if source == "jpx" else fetch_yahoo(code)
    if data:
        data["symbol"] = symbol
        data["name"] = JP_NAMES.get(symbol, data["name"])
    return data


def fetch_market_snapshot(indices: List[str], watchlist: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Collects market snapshot for all requested indices and watchlist tickers.
    """
    indices_data = {}
    watchlist_data = {}
    latest_date = datetime.now().strftime("%Y-%m-%d")

    for sym in indices:
        data = fetch_symbol_data(sym)
        if data:
            indices_data[sym] = data
            latest_date = data["date"]

    for ticker in watchlist or []:
        data = fetch_symbol_data(ticker)
        if data:
            watchlist_data[ticker] = data

    return {
        "date": latest_date,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "indices": indices_data,
        "watchlist": watchlist_data,
    }
