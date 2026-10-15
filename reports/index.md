---
title: 📅 日次マーケットレポート一覧
---

# 📅 日次マーケットレポート一覧

毎営業日 17:00 JST に自動生成されたレポートです。[セットアップ方法はこちら]({{ "/" | relative_url }})

{% assign reports = site.pages | where: "dir", "/reports/" | sort: "name" | reverse %}
{% for r in reports %}{% unless r.name == "index.md" %}- [{{ r.name | remove: ".md" }}]({{ r.url | relative_url }})
{% endunless %}{% endfor %}
