#!/usr/bin/env python3
"""CSVをスプレッドシート1枚ぶんずつに分割する（転記ミス防止のため）。

なぜ必要か:
    CSVの中身をスプレッドシートに上げるとき、中身を1回読み出した内容を
    そのまま貼る。1回の読み出しで扱える量を超えると行が落ちる事故が起きる。
    そこで「1枚 = 1回の読み出しで収まる量」に区切ってから上げる。

使い方:
    python3 scripts/split_csv.py outputs/kei/2026-11-04_4構文まとめ.csv \
        --outdir /tmp/.../ks --limit 18000

    → outdir に sheet1.txt, sheet2.txt … を書き出し、各枚の行数・文字数・
      バイト数と、先頭／末尾のテーマを表示する。

各ファイルはヘッダ行付きの完全なCSVなので、そのまま1枚のシートにできる。
"""
import argparse
import csv
import io
import os
import sys

FIELDS_NOTE = "ヘッダ行は各ファイルの先頭に必ず入る"


def write_sheet(path, header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    text = buf.getvalue()
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--outdir", required=True, help="分割ファイルの書き出し先")
    ap.add_argument("--limit", type=int, default=18000,
                    help="1枚あたりの上限バイト数（既定 18000）")
    a = ap.parse_args()

    with open(a.csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        print("空のCSV")
        return 1
    header, data = rows[0], rows[1:]
    hdr_bytes = len(write_sheet(os.devnull, header, []).encode("utf-8"))

    os.makedirs(a.outdir, exist_ok=True)
    sheets, cur, cur_bytes = [], [], hdr_bytes
    for r in data:
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\r\n").writerow(r)
        n = len(buf.getvalue().encode("utf-8"))
        if cur and cur_bytes + n > a.limit:
            sheets.append(cur)
            cur, cur_bytes = [], hdr_bytes
        cur.append(r)
        cur_bytes += n
    if cur:
        sheets.append(cur)

    print(f"CSV: {a.csv_path}")
    print(f"データ行 {len(data)}  → シート {len(sheets)}枚（上限 {a.limit} bytes）\n")
    total = 0
    for i, s in enumerate(sheets, 1):
        path = os.path.join(a.outdir, f"sheet{i}.txt")
        text = write_sheet(path, header, s)
        total += len(s)
        first = f"{s[0][0]} {s[0][1]}" if len(s[0]) > 1 else s[0][0]
        last = f"{s[-1][0]} {s[-1][1]}" if len(s[-1]) > 1 else s[-1][0]
        print(f"sheet{i}  rows={len(s):>3}  chars={len(text):>6}  "
              f"bytes={len(text.encode('utf-8')):>6}")
        print(f"         [{first}] .. [{last}]")
        print(f"         {path}")
    print(f"\n合計 {total}行（元データ {len(data)}行）"
          f"{'  ← 一致' if total == len(data) else '  ← 不一致。確認が必要'}")
    return 0 if total == len(data) else 1


if __name__ == "__main__":
    sys.exit(main())
