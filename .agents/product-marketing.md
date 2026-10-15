# Product Marketing Context

**Document version:** v1
**Last updated:** 2026-10-15

## Product Overview
**One-liner:** 日本株・金・原油・暗号資産のマーケットまとめを、AI 分析付きで毎日 17:00 に iPhone へ — 完全無料。
**What it does:** GitHub Actions が平日 17:00 JST に Yahoo Finance・JPX・田中貴金属・e燃費からデータを取得し、Gemini が要約・分析して Bark で iPhone にプッシュ通知する。ユーザーはリポジトリを Fork してキーを2つ登録するだけ。サーバー不要。
**Product category:** 株価通知 / マーケットレポート自動化（セルフホスト型）
**Product type:** オープンソースのテンプレートリポジトリ（Fork して使う）
**Business model:** 完全無料。**無料であることは絶対条件**（有料プラン・有料 API・有料ホスティングは使わない）。

## Target Audience
**Target users:** TODO — 仮説：GitHub を触れる日本の個人投資家（エンジニア兼投資家）
**Primary use case:** 大引け後に、アプリを開かずに今日の相場を一通把握する
**Jobs to be done:**
- 証券アプリを何個も開かずに、日経・保有銘柄・金・原油・BTC を一度に確認したい
- 数字だけでなく「今日なぜ動いたか」を短く知りたい
- 無料で、広告なしで、自分の銘柄だけを見たい

## Problems & Pain Points
**Core problem:** 相場情報が複数アプリ・サイトに分散していて、毎日チェックするのが面倒
**Why alternatives fall short:**
- 証券会社アプリ：口座が必要、通知は価格だけで解説がない
- 有料ニュース・AI サービス：月額課金
- 自作スクリプト：サーバー代・保守が必要
**Emotional tension:** TODO（ユーザーの生の声を集める）

## Competitive Landscape
**Direct:** TODO — 他の OSS 株価通知ボット（competitor-profiling で調査）
**Secondary:** 証券会社アプリの通知、Yahoo!ファイナンスのアラート、株探 — 解説がない／銘柄横断で見づらい
**Indirect:** X で投資アカウントを追う、日経新聞 — 時間がかかる、自分の銘柄に絞れない

## Differentiation
**Key differentiators:**
- 完全無料（GitHub Actions + Gemini 無料枠 + Bark）、API キー不要のデータ源
- サーバー不要：Fork して 4 ステップで動く
- 株だけでなく金（田中貴金属の店頭価格）・ガソリン・原油・暗号資産まで 1 通に
- 数字の羅列ではなく AI による短い解説
**Why customers choose us:** TODO（ユーザーから確認）

## Objections
| Objection | Response |
|-----------|----------|
| GitHub が難しそう | 4 ステップの手順、画面操作だけで完結 — TODO: スクリーンショット追加 |
| Android で使えない | 現状 iPhone (Bark) のみ — 対応予定なら記載 |
| 本当にずっと無料？ | Public リポジトリ + 請求先なしの Gemini キーなら課金されない |

**Anti-persona:** リアルタイム売買シグナルが欲しいデイトレーダー（1 日 1 回の通知のため）。投資助言を求める人。

## Switching Dynamics
**Push:** 毎日複数アプリを開く手間、有料サービスの月額
**Pull:** 無料、放置で毎日届く、AI の解説
**Habit:** 慣れた証券アプリ
**Anxiety:** セットアップの難しさ、API キーの扱い、知らないうちに課金されないか

## Customer Language
**How they describe the problem:** TODO（X・5ch・Yahoo!掲示板から収集）
**Words to use:** 完全無料、放置で毎日届く、サーバー不要、4ステップ
**Words to avoid:** 投資助言・必ず儲かる系の表現（本ツールは情報提供のみ）

## Brand Voice
**Tone:** 親しみやすく、簡潔
**Style:** 初心者にもわかる手順重視、絵文字を適度に使う（README のスタイル）
**Personality:** 気軽、誠実、実用的

## Proof Points
**Metrics:** TODO（GitHub スター数・Fork 数）
**Testimonials:** TODO

## Goals
**Business goal:** TODO — 仮説：ポートフォリオ／デモとして GitHub スターと Fork を増やす
**Conversion action:** Fork してセットアップ完了
**Current metrics:** TODO

## Changelog
*Newest first. One line per revision: what changed and why.*
- v1 (2026-10-15) — Initial context auto-drafted from README and workflow; free-forever set as hard constraint.
