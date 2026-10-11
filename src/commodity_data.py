"""
Fetch daily commodity prices: gold (Tanaka Kikinzoku + world), oil (JP retail fuel + world crude)
and crypto (BTC, ETH in JPY).
All sources are free and require no API key.
"""
import re
import html
import json
import logging
from typing import Dict, Any, List, Optional

import requests

from src.market_data import HEADERS, TIMEOUT, fetch_yahoo

logger = logging.getLogger(__name__)

# Yahoo Finance tickers for world prices & crypto
WORLD_TICKERS = {
    "XAU": "GC=F",      # Gold futures (USD/oz)
    "BRENT": "BZ=F",    # Brent crude (USD/barrel)
    "WTI": "CL=F",      # WTI crude (USD/barrel)
    "BTC": "BTC-JPY",   # Bitcoin (JPY)
    "ETH": "ETH-JPY",   # Ethereum (JPY)
}


def _yen(s: str) -> float:
    """Parse '23,311 円' / '+206 円' into a number."""
    return float(re.search(r"[-+]?\d[\d,]*", s).group(0).replace(",", ""))


# ---------------------------------------------------------------------------
# Gold
# ---------------------------------------------------------------------------
def parse_tanaka_gold(page: str) -> Optional[Dict[str, Any]]:
    """Pick the 金 row: [金, 小売価格, 小売前日比, 買取価格, 買取前日比] (JPY per gram, tax included)."""
    for row in re.findall(r"<tr.*?</tr>", page, flags=re.S | re.I):
        cells = [
            html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
            for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, flags=re.S | re.I)
        ]
        if len(cells) >= 5 and cells[0] == "金":
            return {
                "unit": "円/g",
                "retail": _yen(cells[1]),
                "retail_change": _yen(cells[2]),
                "buyback": _yen(cells[3]),
                "buyback_change": _yen(cells[4]),
            }
    return None


def fetch_tanaka_gold() -> Optional[Dict[str, Any]]:
    try:
        res = requests.get("https://gold.tanaka.co.jp/commodity/souba/d-gold.php", headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()
        res.encoding = "utf-8"
        return parse_tanaka_gold(res.text)
    except Exception as e:
        logger.error(f"Error fetching Tanaka gold price: {e}")
        return None


def fetch_gold() -> Dict[str, Any]:
    return {
        "tanaka": fetch_tanaka_gold(),
        "world": fetch_yahoo(WORLD_TICKERS["XAU"]),  # USD/oz
    }


# ---------------------------------------------------------------------------
# Oil
# ---------------------------------------------------------------------------
def parse_enenpi_fuel(page: str) -> List[Dict[str, Any]]:
    """National average pump prices (レギュラー, ハイオク, 軽油) embedded in the page as JSON."""
    m = re.search(r"realtime_data\s*=\s*(\{.*?\})\s*;", page, flags=re.S)
    if not m:
        return []
    prices = json.loads(m.group(1))["prices"]
    return [
        {"name": v["label"], "price": float(v["value"])}
        for k, v in sorted(prices.items())
        if k.isdigit()
    ]


def fetch_retail_fuel() -> List[Dict[str, Any]]:
    try:
        res = requests.get("https://e-nenpi.com/gs/price_graph", headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()
        res.encoding = "utf-8"
        return parse_enenpi_fuel(res.text)
    except Exception as e:
        logger.error(f"Error fetching retail fuel price: {e}")
        return []


def fetch_oil() -> Dict[str, Any]:
    return {
        "retail": fetch_retail_fuel(),  # 円/L
        "world": {
            "BRENT": fetch_yahoo(WORLD_TICKERS["BRENT"]),  # USD/barrel
            "WTI": fetch_yahoo(WORLD_TICKERS["WTI"]),
        },
    }


# ---------------------------------------------------------------------------
# Crypto (BTC & ETH)
# ---------------------------------------------------------------------------
def fetch_crypto() -> Dict[str, Any]:
    """Fetch BTC and ETH prices in JPY."""
    data = {coin: fetch_yahoo(WORLD_TICKERS[coin]) for coin in ("BTC", "ETH")}
    return {coin: d for coin, d in data.items() if d}
