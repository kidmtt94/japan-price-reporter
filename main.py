import sys
from pathlib import Path
from datetime import datetime

# Prevent encoding crashes on Windows terminal
for stream in (sys.stdout, sys.stderr):
    if stream and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

from src.config import parse_args
from src.market_data import fetch_market_snapshot
from src.commodity_data import fetch_gold, fetch_oil, fetch_crypto
from src.agent_brain import MarketAgentBrain
from src.notifier import BarkNotifier


def main():
    config = parse_args()

    print("=" * 60)
    print("🚀 JAPAN STOCK MARKET MINI SWE AGENT")
    print(f"🕒 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 指数: {', '.join(config.symbols)}")
    if config.watchlist:
        print(f"👀 ウォッチリスト: {', '.join(config.watchlist)}")
    print(f"🤖 LLM Model: {config.gemini_model if not config.skip_llm else 'SKIPPED (Template)'}")
    print(f"📱 Bark Notifier: {'ENABLED' if config.bark_key else 'NO KEY PROVIDED'} (Dry run: {config.dry_run})")
    print("=" * 60)

    # 1. Fetch Market Data
    print("\n[1/4] 📥 マーケットデータを取得中...")
    snapshot = fetch_market_snapshot(indices=config.symbols, watchlist=config.watchlist)
    if not snapshot["indices"]:
        print("[ERROR] 指数データを取得できませんでした。ネットワーク接続を確認してください。")
        sys.exit(1)

    print(f"✅ 取引日 {snapshot['date']} のデータを取得しました")
    for d in list(snapshot["indices"].values()) + list(snapshot["watchlist"].values()):
        print(f"   • {d['name']}: {d['close']:,.2f} ({d['change']:+,.2f} | {d['change_pct']:+.2f}%)")

    print("\n📥 金・原油・暗号資産の価格を取得中...")
    snapshot["gold"] = fetch_gold()
    snapshot["oil"] = fetch_oil()
    snapshot["crypto"] = fetch_crypto()
    tanaka = snapshot["gold"].get("tanaka")
    xau = snapshot["gold"].get("world")
    if tanaka:
        print(f"   • 田中貴金属: 小売 {tanaka['retail']:,.0f} / 買取 {tanaka['buyback']:,.0f} 円/g")
    if xau:
        print(f"   • 金（国際）: ${xau['close']:,.2f}/oz ({xau['change_pct']:+.2f}%)")
    for name, d in snapshot["oil"].get("world", {}).items():
        if d:
            print(f"   • 原油 {name}: ${d['close']:,.2f}/バレル ({d['change_pct']:+.2f}%)")
    for f in snapshot["oil"].get("retail", []):
        print(f"   • {f['name']}: {f['price']:,.1f}円/L")
    for coin, d in snapshot["crypto"].items():
        print(f"   • {coin}: {d['close']:,.0f}円 ({d['change_pct']:+.2f}%)")

    # 2. Analyze with Agent Brain
    print("\n[2/4] 🧠 Agent Brain で分析中...")
    brain = MarketAgentBrain(api_key=config.gemini_api_key, model=config.gemini_model)
    if config.skip_llm:
        short_notif, full_markdown = brain._generate_fallback_summary(snapshot, note="--skip-llm モード")
    else:
        short_notif, full_markdown = brain.analyze(snapshot)

    print("✅ 分析完了")

    # 3. Save Markdown Report Locally
    print("\n[3/4] 💾 詳細レポートを保存中...")
    report_dir = Path(config.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"{snapshot['date']}.md"
    report_file.write_text(full_markdown, encoding="utf-8")
    print(f"✅ 保存先: {report_file.resolve()}")

    # 4. Send Push Notification via Bark
    print("\n[4/4] 📲 Bark で iPhone に通知を送信中...")
    notifier = BarkNotifier(bark_key=config.bark_key, server_url=config.bark_server)

    # Formulate notification title with Nikkei 225 change
    nikkei = snapshot["indices"].get("N225")
    if nikkei:
        title = f"📊 日経平均 {snapshot['date']}: {nikkei['close']:,.2f} ({nikkei['change']:+,.2f})"
    else:
        title = f"📊 日本株レポート {snapshot['date']}"

    notifier.send(
        title=title,
        body=short_notif,
        group="JapanMarket",
        sound="minuet",
        is_dry_run=config.dry_run,
    )

    print("\n" + "=" * 60)
    print("🎉 完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    main()
