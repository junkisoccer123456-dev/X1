---
description: 参考投稿を分析して構文だけをライブラリに保存する（投稿生成はしない）
argument-hint: （参考投稿の本文を貼り付け）
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls:*), Bash(cat:*), Bash(date:*)
---

# 構文分析のみ実行

> パス表記について：このドキュメント内の `x-post-system/...` は、
> `x-post-system` フォルダを直接開いている場合は接頭辞 `x-post-system/` を外したパスを指す。


ユーザー入力： $ARGUMENTS

`x-post-system/CLAUDE.md` のルールに従い、**投稿は作らずに構文分析だけ** を行う。
参考投稿のストックを貯めたいときに使うコマンド。

1. 参考投稿が無ければ「本文を貼り付けてください」と聞いて止まる。
2. CLAUDE.md「2. 参考投稿の扱い方」の全観点で分析する。
3. CLAUDE.md「3. 構文分析のフォーマット」の5項目で出力する。
4. `x-post-system/structures/` の既存構文と照合し、重複なら新規作成せず既存を使う
   （差分があれば `## バリエーション` に追記）。
5. 新規の場合のみ `structures/{構文名}.md` を作成する。
6. 参考投稿の原文を `x-post-system/references/{YYYY-MM-DD}-{構文名}.md` に保存する。
7. 最後に「保存先パス」と「この構文が使えそうなアカウント」を1〜2行で伝える。
