#!/usr/bin/env python3
"""x-post-ops スキルを受け渡し用の1ファイル（Markdown）にまとめる。

使い方:
    python3 x-post-system/scripts/make_bundle.py            # リポジトリ直下に書き出す
    python3 x-post-system/scripts/make_bundle.py -o /path/bundle.md

なぜスクリプトにするか:
    中身を手で書き写すと行が落ちる。実ファイルから組み立てれば落ちない。
    スキルを更新したら、このスクリプトを再実行するだけでバンドルも最新になる。

出力されたファイルは、別の環境のClaudeにそのまま渡せば展開できる。
各ファイルは6連バッククォートで囲む（中身に3連が入っているため）。
"""
import argparse
import hashlib
import os
import subprocess
import sys
from datetime import date

# リポジトリ直下からの相対パス。復元先もこのパスになる。
SKILL_FILES = [
    ".claude/skills/x-post-ops/SKILL.md",
    ".claude/skills/x-post-ops/references/qa.md",
    ".claude/skills/x-post-ops/references/spreadsheet.md",
    ".claude/skills/x-post-ops/references/accounts.md",
    ".claude/skills/x-post-ops/references/numbers.md",
    ".claude/skills/x-post-ops/references/structures.md",
    "x-post-system/scripts/md_to_csv.py",
    "x-post-system/scripts/qa_check.py",
    "x-post-system/scripts/past_themes.py",
    "x-post-system/scripts/split_csv.py",
]

APPENDIX_FILES = [
    "x-post-system/CLAUDE.md",
    ".claude/commands/x-post.md",
    ".claude/commands/x-structure.md",
    ".claude/commands/x-account.md",
]

FENCE = "`" * 6

LANG = {".md": "markdown", ".py": "python"}

HEADER = """# x-post-ops ｜ 受け渡し用バンドル

X投稿生成システムの「実行の作法」スキルを、1ファイルにまとめたものです。
**このファイルをそのままClaudeに渡して「このバンドルを展開して」と言ってください。**

- 生成日：{today}
- 元リポジトリ：{repo}
- 元コミット：{commit}

---

## 受け取ったClaudeへの指示

下の各セクションは `### FILE: パス` の見出しと、その中身のコードブロックで構成されています。
**見出しのパスどおりに、中身をそのまま書き出してください。**

1. 「本体」の10ファイルを作る（これがスキル本体）
2. 作業フォルダを直接開いて使う場合は、`.claude/skills/x-post-ops/` を
   そのフォルダの中にも同じ内容でコピーする（どちらを開いても効くようにするため）
3. `x-post-system/scripts/*.py` に実行権限は不要（`python3 スクリプト名` で呼ぶ）
4. 末尾の「チェックサム」で、落ちた行が無いか確認する
5. 「付録」は、受け取った側が同じリポジトリを持っていない場合だけ展開する
   （スキルが前提にしているルール本体とコマンド）

スキルを使うには、`x-post-system/` に次のフォルダが必要です。
無ければ空で作ってください。
`accounts/` `structures/` `outputs/` `references/` `data/` `scripts/`

---

## 含まれるファイル

### 本体（スキル本体。これだけで作法と検査スクリプトが揃う）

| パス | 行数 | 中身 |
|---|---|---|
{skill_table}

### 付録（渡す先が同じリポジトリを持っていない場合のみ必要）

| パス | 行数 | 中身 |
|---|---|---|
{appendix_table}

---
"""

DESC = {
    ".claude/skills/x-post-ops/SKILL.md":
        "スキル本体。実行チェックリスト12工程と絶対に外せない6つ",
    ".claude/skills/x-post-ops/references/qa.md":
        "QAの7項目と、過去に実際に起きた文字混入事故",
    ".claude/skills/x-post-ops/references/spreadsheet.md":
        "シートを分ける理由と手順（行欠落事故の記録）",
    ".claude/skills/x-post-ops/references/accounts.md":
        "アカウント別の落とし穴",
    ".claude/skills/x-post-ops/references/numbers.md":
        "数値を入れるときの判断基準",
    ".claude/skills/x-post-ops/references/structures.md":
        "構文ファイルの書き方・バリエーションの追記位置",
    "x-post-system/scripts/md_to_csv.py":
        "投稿Markdown → スプレッドシート用CSV",
    "x-post-system/scripts/qa_check.py":
        "品質チェック（文字化け・記号・文字数・テーマ重複）",
    "x-post-system/scripts/past_themes.py":
        "使用履歴から過去テーマを集めて重複照合",
    "x-post-system/scripts/split_csv.py":
        "CSVをシート1枚ぶんずつに分割",
    "x-post-system/CLAUDE.md":
        "ルール本体（何を守るか）。スキルより優先する",
    ".claude/commands/x-post.md":
        "/x-post の手順（STEP 0〜8）",
    ".claude/commands/x-structure.md":
        "/x-structure の手順（構文分析のみ）",
    ".claude/commands/x-account.md":
        "/x-account の手順（カルテ記入サポート）",
}


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def table(root, files):
    rows = []
    for rel in files:
        t = read(root, rel)
        rows.append(f"| `{rel}` | {t.count(chr(10)) + 1} | {DESC.get(rel, '')} |")
    return "\n".join(rows)


def section(root, rel):
    t = read(root, rel)
    lang = LANG.get(os.path.splitext(rel)[1], "")
    if FENCE in t:
        raise SystemExit(f"{rel} に6連バッククォートがある。FENCE を長くすること")
    return f"### FILE: {rel}\n\n{FENCE}{lang}\n{t.rstrip(chr(10))}\n{FENCE}\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))  # x-post-system/scripts -> リポジトリ直下
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=os.path.join(root, "x-post-ops-bundle.md"))
    a = ap.parse_args()

    try:
        commit = subprocess.check_output(
            ["git", "-C", root, "rev-parse", "--short", "HEAD"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        commit = "(不明)"
    try:
        repo = subprocess.check_output(
            ["git", "-C", root, "remote", "get-url", "origin"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        repo = "(不明)"

    missing = [p for p in SKILL_FILES + APPENDIX_FILES
               if not os.path.exists(os.path.join(root, p))]
    if missing:
        raise SystemExit("見つからないファイル: " + ", ".join(missing))

    out = [HEADER.format(
        today=date.today().isoformat(), repo=repo, commit=commit,
        skill_table=table(root, SKILL_FILES),
        appendix_table=table(root, APPENDIX_FILES))]

    out.append("\n## 本体\n")
    for rel in SKILL_FILES:
        out.append(section(root, rel))
    out.append("\n---\n\n## 付録\n")
    out.append("渡す先が同じリポジトリを持っていない場合だけ展開してください。\n")
    for rel in APPENDIX_FILES:
        out.append(section(root, rel))

    out.append("\n---\n\n## チェックサム\n")
    out.append("展開後、各ファイルが欠けていないか確認するための一覧です。\n")
    out.append("| パス | 行数 | 文字数 | SHA-256（先頭12桁） |")
    out.append("|---|---|---|---|")
    for rel in SKILL_FILES + APPENDIX_FILES:
        t = read(root, rel)
        h = hashlib.sha256(t.encode("utf-8")).hexdigest()[:12]
        out.append(f"| `{rel}` | {t.count(chr(10)) + 1} | {len(t)} | `{h}` |")
    out.append("")

    text = "\n".join(out)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"書き出しました: {a.out}")
    print(f"ファイル {len(SKILL_FILES)}本（本体）＋ {len(APPENDIX_FILES)}本（付録）")
    print(f"{len(text)} 文字 / {len(text.encode('utf-8'))} bytes "
          f"/ {text.count(chr(10)) + 1} 行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
