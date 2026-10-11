import json
import logging
from typing import Dict, Any, Tuple, Optional
import requests

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """あなたは日本株式市場に精通した、簡潔で客観的な金融アナリストです。
大引け後（EOD）のデータ（日経平均・TOPIX Core30・TOPIX 100の各指数、ウォッチリストの個別銘柄、金価格（田中貴金属の店頭価格＋国際価格）、原油価格（国内ガソリン小売価格＋ブレント/WTI）、暗号資産（ビットコインBTC、イーサリアムETH））を受け取り、次の2つを作成してください。
1. "notification": iPhoneのロック画面に表示する短いプッシュ通知。以下の構成で明確に：
   - パート1（📊 指数）：日経平均、TOPIX Core30、TOPIX 100の終値と前日比（±ポイント、±%）。
   - パート2（👀 銘柄）：ウォッチリストがあれば、各銘柄の終値（円）と前日比%。なければ省略。
   - パート3（🥇 金）：田中貴金属の小売/買取価格（円/g）と前日比、国際価格（USD/oz、±%）。
   - パート4（🛢️ 原油）：ブレント、WTI（USD/バレル、±%）と、レギュラー・ハイオク・軽油の全国平均価格（円/L）。
   - パート5（🪙 暗号資産）：BTC、ETHの価格（円、±%）。
   データがないパートは省略。最後に核心を突く一文のコメントで締める。全体で最大400文字。
2. "report_markdown": 記録用のMarkdown形式の詳細レポート：
   - 本日の相場概況（指数の動き、売買高の平均比など）。
   - TOPIX Core30・TOPIX 100（大型株）の動向と注目セクター。
   - 金、原油、暗号資産（BTC、ETH）の動きとマクロ環境。
   - トレンドの見通しと、翌営業日に向けた短期的な着眼点。

与えられたデータにない数値は作らないこと。出力はすべて日本語。
出力形式は必ず次の構造の有効なJSONとすること：
{
  "notification": "通知に表示する短いテキスト",
  "report_markdown": "Markdown形式の詳細レポート"
}
このJSONブロック以外のテキストは一切含めないこと。
"""


def _signed(d: Dict[str, Any]) -> str:
    return f"{d.get('change', 0):+,.2f} / {d.get('change_pct', 0):+.2f}%"


class MarketAgentBrain:
    def __init__(self, api_key: Optional[str], model: str = "gemini-flash-lite-latest"):
        self.api_key = api_key
        self.model = model

    def analyze(self, market_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Takes structured market data, prompts Gemini, and returns (short_notification, full_markdown).
        """
        if not self.api_key:
            return self._generate_fallback_summary(market_data, note="[GEMINI_API_KEY 未設定]")

        user_content = (
            f"以下は本日（{market_data.get('date', '本日')}）の日本株式市場のデータです：\n\n"
            f"{json.dumps(market_data, ensure_ascii=False, indent=2)}\n\n"
            f"分析し、指示どおりのJSON形式で返してください。"
        )

        # Fallback candidates list in case of temporary demand spikes (503/404)
        candidates = [self.model, "gemini-flash-lite-latest", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
        last_error = ""
        for model_name in dict.fromkeys(candidates):
            try:
                return self._call_gemini_rest(user_content, model_name=model_name)
            except Exception as e:
                logger.debug(f"Gemini call failed with {model_name}: {e}")
                last_error = str(e)

        # If all fail, use deterministic fallback
        return self._generate_fallback_summary(
            market_data,
            note=f"[Gemini呼び出しエラー: {last_error[:100]}]"
        )

    def _call_gemini_rest(self, user_prompt: str, model_name: str) -> Tuple[str, str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3
            }
        }
        # Key goes in a header so it never shows up in error messages or logs
        res = requests.post(url, json=payload, headers={"x-goog-api-key": self.api_key}, timeout=60)
        res.raise_for_status()
        raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

        # Clean any accidental markdown code fence
        clean_text = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        data = json.loads(clean_text)
        return data.get("notification", ""), data.get("report_markdown", "")

    def _generate_fallback_summary(self, market_data: Dict[str, Any], note: str = "") -> Tuple[str, str]:
        """
        Deterministic rule-based summary when LLM is unavailable or skipped.
        """
        date_str = market_data.get("date", "本日")
        indices = market_data.get("indices", {})
        watchlist = market_data.get("watchlist", {})

        notif_lines = [f"📊 マーケット {date_str}:"]
        for d in indices.values():
            notif_lines.append(f"• {d['name']}: {d['close']:,.2f} ({_signed(d)})")

        if watchlist:
            notif_lines.append("\n👀 銘柄:")
            for ticker, d in watchlist.items():
                notif_lines.append(f"• {d['name']} ({ticker}): {d['close']:,.1f}円 ({d['change_pct']:+.2f}%)")

        gold = market_data.get("gold") or {}
        tanaka, xau = gold.get("tanaka"), gold.get("world")
        if tanaka or xau:
            notif_lines.append("\n🥇 金:")
            if tanaka:
                notif_lines.append(
                    f"• 田中貴金属: 小売 {tanaka['retail']:,.0f} / 買取 {tanaka['buyback']:,.0f} 円/g "
                    f"({tanaka['retail_change']:+,.0f}円)"
                )
            if xau:
                notif_lines.append(f"• 国際価格: ${xau['close']:,.1f}/oz ({xau['change_pct']:+.2f}%)")

        oil = market_data.get("oil") or {}
        world_oil = {k: v for k, v in (oil.get("world") or {}).items() if v}
        retail = oil.get("retail") or []
        if world_oil or retail:
            notif_lines.append("\n🛢️ 原油:")
            for name, d in world_oil.items():
                notif_lines.append(f"• {name}: ${d['close']:,.2f} ({d['change_pct']:+.2f}%)")
            for f in retail:
                notif_lines.append(f"• {f['name']}: {f['price']:,.1f}円/L")

        crypto = market_data.get("crypto") or {}
        if crypto:
            notif_lines.append("\n🪙 暗号資産:")
            for coin, d in crypto.items():
                notif_lines.append(f"• {coin}: {d['close']:,.0f}円 ({d['change_pct']:+.2f}%)")

        if note:
            notif_lines.append(f"({note})")
        short_notif = "\n".join(notif_lines)

        report_lines = [
            f"# 日本株マーケットレポート（{date_str}）",
            "",
            "## 1. 主要指数",
            "| 指数 | 終値 | 前日比 | 騰落率 | 出来高 |",
            "| :--- | :---: | :---: | :---: | :---: |",
        ]
        for d in indices.values():
            vol = f"{d['volume']:,}" if d.get("volume") else "-"
            report_lines.append(
                f"| **{d['name']}** | {d['close']:,.2f} | {d['change']:+,.2f} | {d['change_pct']:+.2f}% | {vol} |"
            )

        if watchlist:
            report_lines.extend([
                "",
                "## 2. ウォッチリスト",
                "| 銘柄 | 終値（円） | 前日比 | 騰落率 | 出来高 |",
                "| :--- | :---: | :---: | :---: | :---: |",
            ])
            for ticker, d in watchlist.items():
                report_lines.append(
                    f"| **{d['name']}** ({ticker}) | {d['close']:,.1f} | {d['change']:+,.1f} | "
                    f"{d['change_pct']:+.2f}% | {d.get('volume', 0):,} |"
                )

        if tanaka or xau:
            report_lines.extend(["", "## 3. 金価格", "| 種類 | 価格 | 前日比 |", "| :--- | :---: | :---: |"])
            if tanaka:
                report_lines.append(f"| **田中貴金属 小売** | {tanaka['retail']:,.0f} 円/g | {tanaka['retail_change']:+,.0f} |")
                report_lines.append(f"| **田中貴金属 買取** | {tanaka['buyback']:,.0f} 円/g | {tanaka['buyback_change']:+,.0f} |")
            if xau:
                report_lines.append(f"| **国際価格 (XAU)** | ${xau['close']:,.2f}/oz | {_signed(xau)} |")

        if world_oil or retail:
            report_lines.extend(["", "## 4. 原油・ガソリン価格"])
            if world_oil:
                report_lines.extend(["| 原油 | 価格（USD/バレル） | 前日比 |", "| :--- | :---: | :---: |"])
                for name, d in world_oil.items():
                    report_lines.append(f"| **{name}** | ${d['close']:,.2f} | {_signed(d)} |")
            if retail:
                report_lines.extend(["", "| ガソリン（全国平均） | 価格（円/L） |", "| :--- | :---: |"])
                for f in retail:
                    report_lines.append(f"| {f['name']} | {f['price']:,.1f} |")

        if crypto:
            report_lines.extend(["", "## 5. 暗号資産", "| 通貨 | 価格（円） | 前日比 |", "| :--- | :---: | :---: |"])
            for coin, d in crypto.items():
                report_lines.append(f"| **{coin}** | {d['close']:,.0f} | {d['change']:+,.0f} ({d['change_pct']:+.2f}%) |")

        if note:
            report_lines.extend(["", f"> [!NOTE]\n> {note}"])

        full_md = "\n".join(report_lines)
        return short_notif, full_md
