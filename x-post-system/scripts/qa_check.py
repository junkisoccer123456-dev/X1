#!/usr/bin/env python3
"""保存した投稿ファイルの品質チェック（文字化け・記号・文字数・テーマ重複）。

使い方:
    python3 scripts/qa_check.py outputs/kei/2026-11-04_*.md

    # 参考投稿に ⚫︎ や ❶ などの記号がある構文は、その記号を許可する
    python3 scripts/qa_check.py outputs/kei/*.md --allow-symbols "⚫︎❶❷"

    # アスタリスク強調を使わないアカウント（haru / nori / tamura / kei）
    python3 scripts/qa_check.py outputs/kei/*.md --no-asterisk

何を見ているか:
    1. 他言語の混入   … キリル/ハングル/アラビア/タイ文字（生成事故で実際に何度も出た）
    2. 絵文字・記号   … 参考投稿に無い記号が本文に紛れていないか
    3. 英単語         … 日本語で書くべき箇所が英語になっていないか（design／market など）
    4. アスタリスク   … **強調** を禁止しているアカウント向け
    5. 本文の文字数   … 参考投稿の分量から大きく外れていないか
    6. テーマ重複     … 同じ実行の中でテーマが重複していないか
    7. 見出しの行頭   … 行頭 "投稿" はカウント用。見出しに使うと本数が狂う

終了コード: 問題が1件でもあれば 1、無ければ 0。
"""
import argparse
import glob
import re
import sys
import unicodedata

# 投稿本文を取り出す（"投稿01｜テーマ" の次の ━ 行から、次の ━ 行まで）
BODY_RE = re.compile(r"(?m)^投稿\d+｜.*\n━+\n([\s\S]*?)(?=\n━|\Z)")
THEME_RE = re.compile(r"(?m)^投稿\d+｜(.+)$")

# 日本語でも英語でもない文字（過去に実際に混入したスクリプト）
FOREIGN_RE = re.compile(r"[Ѐ-ӿ가-힯؀-ۿ฀-๿]")
# 絵文字・装飾記号。丸数字 ①〜⑳ は Xでよく使うので対象外にしてある
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿❶-❿]")
LATIN_RE = re.compile(r"[A-Za-z]{2,}")

# 日本語の投稿に出てきても自然な英字（固有名詞・略語・フレームワーク名）
LATIN_OK = {
    "on",  # 1on1
    "JTC", "SaaS", "IT", "AI", "ChatGPT", "Excel", "PowerPoint", "Word",
    "OK", "NG", "CS", "HR", "PM", "PdM", "SE", "KPI", "MVP", "CEO", "CTO",
    "STAR", "PREP", "BEAF", "SCQA", "Before", "After", "Situation", "Task",
    "Action", "Result", "Point", "Reason", "Example", "Background",
    "Experience", "Affinity", "Future", "Why", "Question", "Complication",
    "Answer", "X", "Git", "GitHub", "Docker", "Linux", "SQL", "Python",
}


def norm_theme(s):
    """テーマ名を比較用に正規化する（記号と空白を落とす）。"""
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s　（）()・／/×、。「」【】＋+]", "", s)


def check(paths, allow_symbols, no_asterisk, maxlen, minlen):
    issues = []
    themes = {}  # 正規化テーマ -> [(path, no)]
    allowed = set(allow_symbols)

    for path in paths:
        text = open(path, encoding="utf-8").read()
        bodies = BODY_RE.findall(text)
        theme_names = THEME_RE.findall(text)
        print(f"\n## {path}")
        print(f"   投稿数: {len(bodies)}  テーマ数: {len(theme_names)}")
        if len(bodies) != len(theme_names):
            issues.append(f"{path}: 見出しと本文の数が合わない "
                          f"(見出し{len(theme_names)} / 本文{len(bodies)})")
        if len(bodies) != 10:
            issues.append(f"{path}: 投稿が10本ではない（{len(bodies)}本）")

        # ヘッダ（最初の ━ より前）に行頭「投稿」があると本数カウントが狂う
        head = text.split("━", 1)[0]
        if re.search(r"(?m)^投稿", head):
            issues.append(f"{path}: ヘッダの行頭に「投稿」がある（カウントが狂う）")

        for i, (theme, body) in enumerate(zip(theme_names, bodies), 1):
            tag = f"{path} 投稿{i:02d}"
            for m in set(FOREIGN_RE.findall(body)):
                issues.append(f"{tag}: 他言語の文字が混入 {m!r}")
            for m in set(EMOJI_RE.findall(body)):
                if m not in allowed:
                    issues.append(f"{tag}: 参考投稿に無い記号 {m!r}"
                                  f"（意図した記号なら --allow-symbols に入れる）")
            for m in set(LATIN_RE.findall(body)):
                if m not in LATIN_OK:
                    issues.append(f"{tag}: 英単語が残っている {m!r}"
                                  f"（日本語に直すか LATIN_OK に追加）")
            if no_asterisk and "**" in body:
                issues.append(f"{tag}: ** による強調は禁止")
            n = len(body)
            if maxlen and n > maxlen:
                issues.append(f"{tag}: 本文{n}字（上限{maxlen}字を超過）")
            if minlen and n < minlen:
                issues.append(f"{tag}: 本文{n}字（下限{minlen}字を下回る）")

            key = norm_theme(theme)
            themes.setdefault(key, []).append((tag, theme))

        lengths = [len(b) for b in bodies]
        if lengths:
            print(f"   本文の長さ: {min(lengths)}〜{max(lengths)}字")

    print(f"\n## 実行内のテーマ重複（CLAUDE.md 1.5）")
    dup = {k: v for k, v in themes.items() if len(v) > 1}
    if dup:
        for k, v in dup.items():
            issues.append("テーマ重複: " + " / ".join(f"{t} 「{name}」" for t, name in v))
    print("   重複: なし" if not dup else f"   重複: {len(dup)}件")

    print(f"\n{'=' * 50}")
    if issues:
        print(f"問題 {len(issues)}件")
        for s in issues:
            print(" - " + s)
    else:
        print("問題なし")
    return 1 if issues else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="チェックする投稿Markdown")
    ap.add_argument("--allow-symbols", default="",
                    help="参考投稿で使われている記号（例 '⚫︎❶❷🥇'）")
    ap.add_argument("--no-asterisk", action="store_true",
                    help="** 強調を禁止しているアカウント")
    ap.add_argument("--maxlen", type=int, default=0, help="本文の文字数上限")
    ap.add_argument("--minlen", type=int, default=0, help="本文の文字数下限")
    a = ap.parse_args()
    paths = []
    for p in a.paths:
        paths.extend(sorted(glob.glob(p)) or [p])
    sys.exit(check(paths, a.allow_symbols, a.no_asterisk, a.maxlen, a.minlen))


if __name__ == "__main__":
    main()
