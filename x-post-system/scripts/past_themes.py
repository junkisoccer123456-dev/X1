#!/usr/bin/env python3
"""構文の ## 使用履歴 をたどって、過去に使ったテーマを全部集める（CLAUDE.md 6.5）。

使い方:
    # その構文で過去に使ったテーマを一覧表示（アカウントをまたいで全部）
    python3 scripts/past_themes.py structures/list-teiji-reply-kaishu.md

    # 今回の出力と突き合わせて重複を検出する
    python3 scripts/past_themes.py structures/gihou-catalog.md \
        --against outputs/kei/2026-11-04_02_技法カタログ3段型.md

使用履歴の行は次の形で書かれている前提。
    - 2026-11-04 / kei / 2026-11-04_02_技法カタログ3段型.md（バリエーションB／…）

終了コード: 重複が1件でもあれば 1、無ければ 0。
"""
import argparse
import glob
import os
import re
import sys
import unicodedata

HIST_RE = re.compile(r"(?m)^-\s*(\S+)\s*/\s*(\S+)\s*/\s*([^（(\s]+\.md)")
THEME_RE = re.compile(r"(?m)^投稿\d+｜(.+)$")


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s　（）()・／/×、。「」【】＋+]", "", s)


def repo_root(structure_path):
    """structures/ の1つ上（x-post-system/）を返す。"""
    return os.path.dirname(os.path.dirname(os.path.abspath(structure_path)))


def collect(structure_path, skip=()):
    text = open(structure_path, encoding="utf-8").read()
    hist = text.split("## 使用履歴", 1)
    if len(hist) < 2:
        print(f"   ※ {structure_path} に ## 使用履歴 が無い（新規構文）")
        return {}, 0
    root = repo_root(structure_path)
    themes = {}
    files = 0
    for date, account, fname in HIST_RE.findall(hist[1]):
        if fname in skip:
            # 今回チェックする出力そのもの（使用履歴に追記済み）は過去扱いしない
            continue
        path = os.path.join(root, "outputs", account, fname)
        if not os.path.exists(path):
            print(f"   ※ 見つからない: {path}（使用履歴の表記を確認）")
            continue
        files += 1
        body = open(path, encoding="utf-8").read()
        for t in THEME_RE.findall(body):
            themes.setdefault(norm(t), (t, f"{date} / {account} / {fname}"))
    return themes, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("structures", nargs="+", help="structures/*.md")
    ap.add_argument("--against", nargs="*", default=[],
                    help="今回の出力Markdown（重複チェック対象）")
    ap.add_argument("--list", action="store_true", help="過去テーマを全件表示する")
    a = ap.parse_args()

    structures = []
    for p in a.structures:
        structures.extend(sorted(glob.glob(p)) or [p])
    against = []
    for p in a.against:
        against.extend(sorted(glob.glob(p)) or [p])

    skip = {os.path.basename(p) for p in against}
    past = {}
    for s in structures:
        print(f"\n## {s}")
        themes, files = collect(s, skip)
        print(f"   過去ファイル {files}本 / 過去テーマ {len(themes)}件")
        if a.list:
            for key, (t, src) in sorted(themes.items(), key=lambda x: x[1][1]):
                print(f"   - {t}  （{src}）")
        past.update(themes)

    if not against:
        print(f"\n合計 過去テーマ {len(past)}件")
        return 0

    print(f"\n## 今回の出力と突き合わせ（過去 {len(past)}件に対して）")
    dups = []
    total = 0
    for p in against:
        text = open(p, encoding="utf-8").read()
        for t in THEME_RE.findall(text):
            total += 1
            k = norm(t)
            if k in past:
                dups.append(f"{p} 「{t}」 ← {past[k][1]}")
    print(f"   今回のテーマ {total}件")
    if dups:
        print(f"   重複 {len(dups)}件")
        for d in dups:
            print("   - " + d)
    else:
        print("   重複 0件")
    return 1 if dups else 0


if __name__ == "__main__":
    sys.exit(main())
