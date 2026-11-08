#!/usr/bin/env python3
"""アカウントカードを受け渡し用の1ファイル（Markdown）にまとめる。

使い方:
    python3 x-post-system/scripts/make_accounts_bundle.py
    python3 x-post-system/scripts/make_accounts_bundle.py -o /path/bundle.md

中身:
    1. 要点早見表（accounts/README.md をそのまま収録）
    2. 記入済みカード4本の全文
    3. 未記入カードとテンプレート（受け取り側が新しいアカウントを作れるように）
    4. チェックサム表

make_bundle.py と同じ方式。実ファイルから組み立てるので行が落ちない。
"""
import argparse
import hashlib
import os
import subprocess
import sys
from datetime import date

SUMMARY = "x-post-system/accounts/README.md"

FILLED = [
    "x-post-system/accounts/haru.md",
    "x-post-system/accounts/kei.md",
    "x-post-system/accounts/tamura.md",
    "x-post-system/accounts/nori.md",
]

BLANK = [
    "x-post-system/accounts/_TEMPLATE.md",
    "x-post-system/accounts/kouta.md",
    "x-post-system/accounts/imai.md",
]

FENCE = "`" * 6

HEADER = """# X投稿システム ｜ アカウントカード受け渡し用バンドル

アカウントごとの詳細（プロフィール・発信スタンス・文体・専用の出力ルール）を
1ファイルにまとめたものです。
**このファイルをそのままClaudeに渡して「このバンドルを展開して」と言ってください。**

- 生成日：{today}
- 元リポジトリ：{repo}
- 元コミット：{commit}
- 記入済み：**haru / kei / tamura / nori**（4アカウント）
- 未記入：kouta / imai

---

## 受け取ったClaudeへの指示

下の各セクションは `### FILE: パス` の見出しと、その中身のコードブロックで構成されています。
**見出しのパスどおりに、中身をそのまま書き出してください。**

- カードは `x-post-system/accounts/` に置く
- **カード本体が正**。早見表（`accounts/README.md`）は読む側のための要約なので、
  食い違ったらカード本体に従う
- 各カードの `## 13. このアカウント専用の出力ルール` は、
  `x-post-system/CLAUDE.md` の既定ルールより**優先する**
  （ただし絵文字だけは CLAUDE.md 7 が最優先：参考投稿の記号をそのまま再現する）
- `_TEMPLATE.md` は新しいアカウントを追加するときの雛形
- 末尾の「チェックサム」で、落ちた行が無いか確認する

## このバンドルだけでは足りないもの

アカウントカードは「誰が、誰に、どう発信するか」だけを持っています。
投稿を生成するには別途これが必要です。

- `x-post-system/CLAUDE.md`（ルール本体）と `/x-post` コマンド
- スキル `x-post-ops`（実行の作法・QAスクリプト）
- → どちらも `x-post-ops-bundle.md` に入っています

---

## 読む順番

| # | セクション | 中身 |
|---|---|---|
| 1 | 要点早見表 | 4アカウントの比較表と、1アカウントずつの要点 |
| 2 | 記入済みカード | haru / kei / tamura / nori の全文 |
| 3 | 未記入カードと雛形 | kouta / imai / _TEMPLATE |

---
"""


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def section(root, rel):
    t = read(root, rel)
    if FENCE in t:
        raise SystemExit(f"{rel} に6連バッククォートがある。FENCE を長くすること")
    return f"### FILE: {rel}\n\n{FENCE}markdown\n{t.rstrip(chr(10))}\n{FENCE}\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out",
                    default=os.path.join(root, "x-post-accounts-bundle.md"))
    a = ap.parse_args()

    def git(*args):
        try:
            return subprocess.check_output(["git", "-C", root, *args],
                                           text=True,
                                           stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "(不明)"

    allfiles = [SUMMARY] + FILLED + BLANK
    missing = [p for p in allfiles if not os.path.exists(os.path.join(root, p))]
    if missing:
        raise SystemExit("見つからないファイル: " + ", ".join(missing))

    out = [HEADER.format(today=date.today().isoformat(),
                         repo=git("remote", "get-url", "origin"),
                         commit=git("rev-parse", "--short", "HEAD"))]

    out.append("\n## 1. 要点早見表\n")
    out.append(section(root, SUMMARY))

    out.append("\n---\n\n## 2. 記入済みカード（全文）\n")
    for rel in FILLED:
        out.append(section(root, rel))

    out.append("\n---\n\n## 3. 未記入カードと雛形\n")
    out.append("kouta と imai はテンプレートのままです。"
               "投稿生成の指示が来たら、推測で埋めずに不足項目を質問して止まります。\n")
    for rel in BLANK:
        out.append(section(root, rel))

    out.append("\n---\n\n## チェックサム\n")
    out.append("展開後、各ファイルが欠けていないか確認するための一覧です。\n")
    out.append("| パス | 行数 | 文字数 | SHA-256（先頭12桁） |")
    out.append("|---|---|---|---|")
    for rel in allfiles:
        t = read(root, rel)
        h = hashlib.sha256(t.encode("utf-8")).hexdigest()[:12]
        out.append(f"| `{rel}` | {t.count(chr(10)) + 1} | {len(t)} | `{h}` |")
    out.append("")

    text = "\n".join(out)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"書き出しました: {a.out}")
    print(f"早見表1本 ＋ 記入済み{len(FILLED)}本 ＋ 未記入・雛形{len(BLANK)}本")
    print(f"{len(text)} 文字 / {len(text.encode('utf-8'))} bytes "
          f"/ {text.count(chr(10)) + 1} 行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
