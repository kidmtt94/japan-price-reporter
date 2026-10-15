# 📈 日本株マーケット自動レポート — 完全無料

毎日 **17:00（月〜金）** に、**日本株マーケットの通知を iPhone に自動送信**します。  
**AI（Gemini）** が分析し、GitHub 上で**完全無料**で動きます。

👉 **[毎日のレポート実例を見る](https://kidmtt94.github.io/japan-price-reporter/reports/)**

---

## ✨ 機能 — すべて無料

| 機能 | 費用 |
|---|---|
| 🤖 Gemini 2.5 Flash によるマーケット分析 | **無料**（Google AI Studio） |
| ⏰ GitHub Actions で毎日 17:00 に自動実行 | **無料**（GitHub） |
| 📱 Bark で iPhone にプッシュ通知 | **無料**（Bark アプリ） |
| 📊 日経平均・TOPIX Core30・TOPIX 100 と個別銘柄 | **無料** |
| 🥇 金価格（田中貴金属の店頭価格 + 国際価格） | **無料** |
| 🛢️ ガソリン全国平均価格 + 原油（ブレント/WTI） | **無料** |
| 🪙 暗号資産 ビットコイン（BTC）・イーサリアム（ETH） | **無料** |

データ取得元（すべて API キー不要）：Yahoo Finance、日本取引所グループ（JPX）、田中貴金属工業、e燃費。

> **無料で使い続けるために：** リポジトリは **Public** のままにしてください（Public リポジトリの GitHub Actions は無制限で無料）。Gemini API キーは、**請求先アカウントを紐付けていない** Google AI Studio の無料枠のものを使ってください。

---

## 🚀 セットアップ — たった4ステップ

### ステップ1 — このリポジトリを自分の GitHub アカウントに Fork する

> GitHub Actions は**あなた**のアカウントで動くため、自分の GitHub にこのリポジトリのコピーが必要です。

1. GitHub でこのリポジトリのページを開く
2. 右上の **「Fork」** ボタンを押す
3. **「Create fork」** を押す — 完了！コードとワークフローが揃った自分用リポジトリができます

---

### ステップ2 — API キーを2つ取得する

**🤖 Gemini API キー**（AI によるマーケット分析用）：
1. [Google AI Studio](https://aistudio.google.com/app/apikey) を開く
2. Google アカウントでログイン
3. **「Create API Key」** を押して、作成されたキーをコピー

**📱 Bark キー**（iPhone で通知を受け取る用）：
1. iPhone の App Store で **「Bark」** を検索してインストール
2. Bark を開くと、ホーム画面に自分のキーが表示されます
3. `https://api.day.app/` の後ろの文字列をコピー — これが Bark キーです

---

### ステップ3 — キーを GitHub Secrets に登録する

> キーを安全に保管する場所で、**あなた以外は見ることができません**。

1. 自分の GitHub リポジトリを開く
2. **Settings**（リポジトリ右上）を押す
3. **Secrets and variables → Actions** を選ぶ
4. **「New repository secret」** を押して、次の2つを順番に追加：

| Secret 名 | 値 |
|---|---|
| `GEMINI_API_KEY` | Gemini API キーを貼り付け |
| `BARK_KEY` | Bark キーを貼り付け |

---

### ステップ4 — ウォッチする銘柄をカスタマイズ

[`.github/workflows/daily-report.yml`](.github/workflows/daily-report.yml) を開き、`WATCHLIST` の行を探します：

```yaml
env:
  WATCHLIST: "8306,7203,9984"
```

初期設定は時価総額上位3社です：**三菱UFJ（8306）・トヨタ自動車（7203）・ソフトバンクグループ（9984）**。

**お好みで変更：** 東証の証券コードをカンマ区切りで指定します。

```yaml
# 例：ソニーグループ、日立、任天堂をウォッチ
env:
  WATCHLIST: "6758,6501,7974"
```

指数を変えたい場合（初期値は `N225,CORE30,TOPIX100`）は、`python main.py` の行に `--symbols` を追加します。指定できるのは `N225`・`TOPIX`・`CORE30`・`TOPIX100` です。

変更したら **commit & push** するだけ — GitHub がすぐに反映します。

---

## ⏰ 自動実行スケジュール

**月〜金の JST 17:00 ごろ**に自動で実行されます（東証の大引け 15:30 の後）。セットアップ後は何もする必要はありません。

> **注意：** GitHub Actions は分単位の正確さを保証しません。通知は設定時刻より **5〜15分** ほど遅れることがありますが、正常な動作です。  
> また、祝日は東証が休場のため、株価は直近の取引日のデータになります（通知タイトルに取引日が表示されます）。

**手動で試す**には：リポジトリ → **Actions** → **Daily Japan Market Report** → **Run workflow**。

---

## 💻 ローカルで試す

```bash
poetry install
poetry run python main.py --watchlist "8306,7203,9984" --dry-run --skip-llm
```

`--dry-run` は通知を送らず画面に表示するだけ、`--skip-llm` は Gemini を使わずテンプレートで出力します。キーは `.env.example` を `.env` にコピーして設定できます。

---

> ⚠️ 本ツールは情報提供のみを目的としており、投資助言ではありません。
