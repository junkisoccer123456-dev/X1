#!/usr/bin/env python3
"""投稿MarkdownをスプレッドシートにインポートできるCSVへ変換する。

使い方:
    python3 scripts/md_to_csv.py outputs/tamura/2026-09-22_xxx_01.md

同じ場所に .csv を書き出す。列は data/SCHEMA.md の成績記録と揃えてあるので、
後から数値を書き足せばそのまま成績管理表になる。
"""
import csv, io, os, re, sys

SEP = "━" * 18


def parse(path):
    text = io.open(path, encoding="utf-8").read()

    meta = {}
    m = re.match(r"(?s)^---\n(.*?)\n---\n", text)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.split("#")[0].strip()

    rows = []
    # 「区切り線 / 投稿NN｜テーマ / 区切り線 / 本文」のブロックを拾う
    for block in re.finditer(
        r"(?m)^%s\n投稿(\d+)｜(.+?)\n%s\n(.*?)(?=^%s\n投稿|\Z)" % (SEP, SEP, SEP),
        text, re.S,
    ):
        no, theme, body = block.group(1), block.group(2).strip(), block.group(3)
        body = re.split(r"(?m)^---\s*$", body)[0]          # 末尾の注意メモを除去
        main, _, reply = body.partition("【リプ】")
        rows.append({
            "No": no,
            "テーマ": theme,
            "本文": main.strip(),
            "リプ": reply.strip(),
            "date": meta.get("date", ""),
            "account": meta.get("account", ""),
            "structure": meta.get("structure", ""),
            "status": meta.get("status", "draft"),
            "post_url": "",
            "impressions": "", "likes": "", "bookmarks": "",
            "reposts": "", "profile_visits": "", "note": "",
        })
    return rows


def main():
    if len(sys.argv) < 2:
        print("使い方: python3 scripts/md_to_csv.py <投稿ファイル.md>")
        sys.exit(1)
    src = sys.argv[1]
    rows = parse(src)
    if not rows:
        print("投稿が見つかりませんでした:", src)
        sys.exit(1)
    dst = os.path.splitext(src)[0] + ".csv"
    # BOM付きUTF-8。Excelでもスプレッドシートでも文字化けしない
    with io.open(dst, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("%d件を書き出しました -> %s" % (len(rows), dst))


if __name__ == "__main__":
    main()
