#!/usr/bin/env python3
"""投稿MarkdownをスプレッドシートにインポートできるCSVへ変換する。

使い方:
    # 1ファイル（同じ場所に .csv を書き出す）
    python3 scripts/md_to_csv.py outputs/tamura/2026-09-22_xxx_01.md

    # 複数ファイルを1つのCSVにまとめる
    python3 scripts/md_to_csv.py outputs/tamura/a.md outputs/tamura/b.md -o まとめ.csv

出力ルール:
    1投稿 = 1行が基本。ただしリプが複数ある投稿は、リプごとに行を分ける。
    「種別」列が 本文 / リプ① / リプ② … となり、「テキスト」列にその行の文章が入る。
    成績（impressions など）は本文の行にだけ記入する想定。
"""
import csv, io, os, re, sys

SEP = "━" * 18
# 【リプ】【リプ①】【リプ1】【リプ2】などをすべて拾う
REPLY_RE = re.compile(r"(?m)^【リプ([^】]*)】[ \t]*")
# 【A｜数値・有益型】のようなパターン見出しを拾う
PATTERN_RE = re.compile(r"(?m)^【([ABC])｜[^】]*】[ \t]*")

FIELDS = [
    "No", "テーマ", "種別", "テキスト",
    "date", "account", "structure", "status", "post_url",
    "impressions", "likes", "bookmarks", "reposts", "profile_visits", "note",
]


def split_patterns(body):
    """A/B/Cパターンで書かれた投稿を [(種別, 本文), ...] に分ける。無ければ None。"""
    marks = list(PATTERN_RE.finditer(body))
    if not marks:
        return None
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        out.append(("パターン" + m.group(1), body[m.end(): end].strip()))
    return out


def split_replies(body):
    """本文と [(ラベル, 本文), ...] のリプ一覧に分ける。"""
    marks = list(REPLY_RE.finditer(body))
    if not marks:
        return body.strip(), []
    main = body[: marks[0].start()].strip()
    replies = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        label = "リプ" + (m.group(1).strip() or str(i + 1))
        text = body[m.end(): end].strip()
        replies.append((label, text))
    return main, replies


def parse(path):
    text = io.open(path, encoding="utf-8").read()

    meta = {}
    m = re.match(r"(?s)^---\n(.*?)\n---\n", text)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.split("#")[0].strip()

    base = {
        "date": meta.get("date", ""),
        "account": meta.get("account", ""),
        "structure": meta.get("structure", ""),
        "status": meta.get("status", "draft"),
        "post_url": "",
        "impressions": "", "likes": "", "bookmarks": "",
        "reposts": "", "profile_visits": "", "note": "",
    }

    rows = []
    for block in re.finditer(
        r"(?m)^%s\n投稿(\d+)｜(.+?)\n%s\n(.*?)(?=^%s\n投稿|\Z)" % (SEP, SEP, SEP),
        text, re.S,
    ):
        no, theme, body = block.group(1), block.group(2).strip(), block.group(3)
        body = re.split(r"(?m)^---\s*$", body)[0]      # 末尾の注意メモを除去
        patterns = split_patterns(body)
        if patterns:
            for label, ptext in patterns:
                rows.append(dict(base, No=no, テーマ=theme, 種別=label, テキスト=ptext))
            continue

        main, replies = split_replies(body)

        row = dict(base, No=no, テーマ=theme, 種別="本文", テキスト=main)
        rows.append(row)

        # リプが2つ以上ある投稿は行を分ける。1つだけなら同じ行の続きにせず1行追加で統一
        for label, rtext in replies:
            rows.append(dict(
                base, No=no, テーマ=theme, 種別=label, テキスト=rtext,
                status=base["status"],
            ))
    return rows


def main():
    args = sys.argv[1:]
    out = None
    if "-o" in args:
        i = args.index("-o")
        out = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args:
        print("使い方: python3 scripts/md_to_csv.py <投稿ファイル.md> [...] [-o 出力.csv]")
        sys.exit(1)

    rows = []
    for src in args:
        found = parse(src)
        if not found:
            print("投稿が見つかりませんでした:", src)
            sys.exit(1)
        rows.extend(found)

    dst = out or (os.path.splitext(args[0])[0] + ".csv")
    # BOM付きUTF-8。Excelでもスプレッドシートでも文字化けしない
    with io.open(dst, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    posts = len({(r["structure"], r["No"], r["テーマ"]) for r in rows})
    print("テーマ%d件 / %d行を書き出しました -> %s" % (posts, len(rows), dst))


if __name__ == "__main__":
    main()
