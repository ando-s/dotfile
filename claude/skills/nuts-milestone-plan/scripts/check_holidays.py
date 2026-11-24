#!/usr/bin/env python3
"""計画の帯の開始日・終了日が、土日・祝日・休業日に当たっていないかを調べる。

使い方: python3 -I check_holidays.py <正本.html> [休業日のJSON]
  休業日のJSON は、スプレッドシートのコネクタの get_values で "休業日!A2:B80" を読んだ結果（{"values":[["2026-12-25","イベントデー"],...]}）をファイルに書いたもの。
  省略すると土日と祝日だけで調べる。

祝日はこのファイルに書いた一覧（2026-11〜2027-12）。期間を延ばすときは JP_HOLIDAYS に足す。
"""
import datetime as dt
import json
import re
import sys

JP_HOLIDAYS = {
    "2026-11-03": "文化の日", "2026-11-23": "勤労感謝の日",
    "2027-01-01": "元日", "2027-01-11": "成人の日", "2027-02-11": "建国記念の日", "2027-02-23": "天皇誕生日",
    "2027-03-21": "春分の日", "2027-03-22": "振替休日", "2027-04-29": "昭和の日",
    "2027-05-03": "憲法記念日", "2027-05-04": "みどりの日", "2027-05-05": "こどもの日",
    "2027-07-19": "海の日", "2027-08-11": "山の日", "2027-09-20": "敬老の日", "2027-09-23": "秋分の日",
    "2027-10-11": "スポーツの日", "2027-11-03": "文化の日", "2027-11-23": "勤労感謝の日",
}

src = sys.argv[1]
company = {}
if len(sys.argv) > 2:
    for row in json.load(open(sys.argv[2])).get("values", []):
        if row and re.match(r"\d{4}-\d{2}-\d{2}", row[0]):
            company[row[0]] = row[1] if len(row) > 1 else "休業日"

s = open(src, encoding="utf-8").read()
plans = re.findall(r'<template data-plan="([^"]+)".*?<script type="application/json" class="plan-data">(.*?)</script>', s, re.S)
plan_date, raw = plans[0]  # 新しい時点が先頭にある前提ではないので data-plan で選ぶ
for d_, r in plans:
    if d_ > plan_date:
        plan_date, raw = d_, r
data = json.loads(raw.replace("<\\/", "</"))


def why(ymd):
    d = dt.date.fromisoformat(ymd)
    if d.weekday() >= 5:
        return "土日"
    if ymd in JP_HOLIDAYS:
        return JP_HOLIDAYS[ymd]
    if ymd in company:
        return "休業日: " + company[ymd]
    return None


print(f"時点 {plan_date}")
hit = 0
for p in data["people"]:
    for b in p["bars"]:
        for label, ymd in (("開始", b[1]), ("終了", b[2])):
            w = why(ymd)
            if w:
                hit += 1
                print(f"  {p['who']} | {b[0]} | {label} {ymd} は {w}")
print("問題なし" if hit == 0 else f"{hit} 件")
