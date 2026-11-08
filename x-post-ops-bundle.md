# x-post-ops ｜ 受け渡し用バンドル

X投稿生成システムの「実行の作法」スキルを、1ファイルにまとめたものです。
**このファイルをそのままClaudeに渡して「このバンドルを展開して」と言ってください。**

- 生成日：2026-11-08
- 元リポジトリ：https://github.com/junkisoccer123456-dev/X1
- 元コミット：154fba9

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
| `.claude/skills/x-post-ops/SKILL.md` | 145 | スキル本体。実行チェックリスト12工程と絶対に外せない6つ |
| `.claude/skills/x-post-ops/references/qa.md` | 55 | QAの7項目と、過去に実際に起きた文字混入事故 |
| `.claude/skills/x-post-ops/references/spreadsheet.md` | 60 | シートを分ける理由と手順（行欠落事故の記録） |
| `.claude/skills/x-post-ops/references/accounts.md` | 55 | アカウント別の落とし穴 |
| `.claude/skills/x-post-ops/references/numbers.md` | 57 | 数値を入れるときの判断基準 |
| `.claude/skills/x-post-ops/references/structures.md` | 74 | 構文ファイルの書き方・バリエーションの追記位置 |
| `x-post-system/scripts/md_to_csv.py` | 137 | 投稿Markdown → スプレッドシート用CSV |
| `x-post-system/scripts/qa_check.py` | 142 | 品質チェック（文字化け・記号・文字数・テーマ重複） |
| `x-post-system/scripts/past_themes.py` | 114 | 使用履歴から過去テーマを集めて重複照合 |
| `x-post-system/scripts/split_csv.py` | 89 | CSVをシート1枚ぶんずつに分割 |

### 付録（渡す先が同じリポジトリを持っていない場合のみ必要）

| パス | 行数 | 中身 |
|---|---|---|
| `x-post-system/CLAUDE.md` | 494 | ルール本体（何を守るか）。スキルより優先する |
| `.claude/commands/x-post.md` | 131 | /x-post の手順（STEP 0〜8） |
| `.claude/commands/x-structure.md` | 26 | /x-structure の手順（構文分析のみ） |
| `.claude/commands/x-account.md` | 23 | /x-account の手順（カルテ記入サポート） |

---


## 本体

### FILE: .claude/skills/x-post-ops/SKILL.md

``````markdown
---
name: x-post-ops
description: X投稿生成システム（x-post-system/）を実行するときの作法。/x-post /x-structure /x-account を動かすとき、投稿の生成・保存・QA・スプレッドシート化・構文ファイル更新・コミットのどれかに触るときに必ず読む。過去テーマの重複チェック、文字化けQA、シート分割、数値の扱い、アカウント別の落とし穴、事故の再発防止策が入っている。
---

# X投稿生成の実行マニュアル

## 3つのファイルの役割

| ファイル | 役割 |
|---|---|
| `x-post-system/CLAUDE.md` | **ルール**（何を守るか）。常に最優先 |
| `.claude/commands/x-post.md` | **手順**（STEP 0〜8の流れ） |
| このスキル | **作法**（実際にどう手を動かすか・過去の事故と対策） |

ルールが衝突したら `x-post-system/CLAUDE.md` が勝つ。
アカウントカードの「このアカウント専用の出力ルール」は CLAUDE.md より優先するが、
**絵文字だけは CLAUDE.md 7 が最優先**（参考投稿の記号をそのまま再現する）。

---

## 実行チェックリスト

`/x-post {アカウント}` ＋ 参考投稿が来たら、この順で進める。
コマンド例は `x-post-system/` にいる前提。

### 1. アカウントカードを読む
```bash
cat accounts/{アカウント}.md
```
未記入項目が多ければ推測で埋めずに質問して止まる。
権威づけの定型文・一人称・語尾・CTA定型文・禁止事項をここで押さえる。

### 2. 参考投稿を数えて、1本ずつ構文分析する
件数は毎回変わる。**数えた数だけ処理する**。
1つにまとめて分析しない（CLAUDE.md 1.5）。

### 3. 既存構文と照合する（必須・飛ばさない）
```bash
ls structures/
grep -A 15 "^## 基本構造" structures/{候補}.md
```
- 骨格が同じ → **新規作成しない**。既存構文をそのまま再利用
- 似ているが差分あり → 既存ファイルの `## バリエーション` に追記
- 明確に別構造 → 新規作成。**ただし比較した候補と「なぜ別構造か」を参考ファイルに書き残す**

→ 追記位置と書式は `references/structures.md`

### 4. 過去テーマを集めて除外する（CLAUDE.md 6.5・必須）
テーマを決める**前**に実行する。
```bash
python3 scripts/past_themes.py structures/{構文}.md --list
```
使用履歴をたどって、他アカウントのぶんも含めて過去テーマを全件出す。
言い換えただけも重複。対象・場面がはっきり違えばOK。

### 5. テーマを決める（内部30 → 10）
- 過去テーマを除外
- **参考投稿そのもののテーマ・固有名詞・数字は使わない**（CLAUDE.md 2）
- **構文をまたいで重複させない**（CLAUDE.md 1.5）。
  複数構文を同時に回すときは、先に「構文ごとの軸」を決めて場面で切り分ける
  （例：①入社後の社内場面 ／ ③選考工程の直前）
- 切り口を散らす（失敗談／数字／比較／常識否定／手順／体験／誤解／本音／環境／時間軸）

### 6. 投稿を書いて保存する
`outputs/{アカウント}/{YYYY-MM-DD}_{連番}_{構文名}.md`
先頭に CLAUDE.md 9 のYAMLメタを必ず入れる。

- 「構文は統合、本数は維持」。参考投稿N本 → N通り × 10本
- 記号は参考投稿のものをそのまま（⚫︎ ❶ 🥇 □ ・ など）
- CTAは**参考投稿にCTAがあるときだけ**付ける
- 行頭に `投稿` で始まる行をヘッダに書かない（本数カウントが狂う）

### 7. QAを通す（必須）
```bash
python3 scripts/qa_check.py "outputs/{アカウント}/{日付}_*.md" \
    --allow-symbols "⚫" --no-asterisk
```
問題0件になるまで直す。何を見ているかと過去の事故は `references/qa.md`。

### 8. 過去テーマ重複を最終確認する
```bash
python3 scripts/past_themes.py structures/{構文}.md \
    --against "outputs/{アカウント}/{日付}_{連番}_*.md"
```
重複0件を確認してから次へ。

### 9. CSV → スプレッドシート（毎回必須・確認を取らない）
```bash
python3 scripts/md_to_csv.py outputs/{アカウント}/{ファイル群}.md \
    -o outputs/{アカウント}/{日付}_{構文数}構文まとめ.csv
python3 scripts/split_csv.py outputs/{アカウント}/{日付}_..._まとめ.csv \
    --outdir "$SCRATCHPAD/sheets" --limit 18000
```
分割した1ファイルずつ `cat` して `mcp__Google_Drive__create_file` で上げる。
**1枚 = 1回の `cat` 出力**。これを破ると行が落ちる（実際に落ちた）。
詳細と事故の記録は `references/spreadsheet.md`。

### 10. 構文ファイルの使用履歴に追記する
```
- YYYY-MM-DD / アカウント / 出力ファイル名.md（バリエーションX／軸を〜に入れ替え・過去N件と全件重複なし）
```
`## 使用履歴` の**末尾**に足す。バリエーション本文は `## バリエーション` の中へ
（使用履歴より後ろに置かない）。

### 11. コミット＆プッシュ
```bash
git add -A && git commit -F - <<'EOF'
{アカウント} {日付}: N構文M本を追加（…）

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: {セッションURL}
EOF
git push -u origin {作業ブランチ}
```
PRは**明示的に頼まれない限り作らない**。指定ブランチ以外にpushしない。

### 12. 報告（短く）
構文リスト（新規／バリエーション追記／再利用を明記）→ 10テーマ → パス →
スプレッドシートリンク → 最後に
「気に入らない投稿があれば『投稿3を作り直して』と言ってください」

---

## 絶対に外せない6つ

1. **過去テーマの除外**（6.5）… 同じ構文 × 同じテーマは他アカウントのぶんも含めてNG
2. **構文間のテーマ重複禁止**（1.5）… 同じ実行の中でも被らせない
3. **参考投稿のテーマ・固有名詞・数字の転用禁止**（2）
4. **記号は参考投稿のまま**（7）… カードの「絵文字なし」より優先
5. **数値は空白にせず明記、ただし捏造しない** → `references/numbers.md`
6. **本数を勝手に減らさない**（10本未満で終わらない／減らすなら必ず確認）

---

## 詳しい話

| 読むとき | ファイル |
|---|---|
| QAで何を見ているか・過去に起きた混入事故 | `references/qa.md` |
| シートを分ける理由・行が落ちた事故と対策 | `references/spreadsheet.md` |
| アカウント別の落とし穴（禁止表現・実績の範囲） | `references/accounts.md` |
| 数値を入れるときの判断基準 | `references/numbers.md` |
| 構文ファイルの書き方・バリエーションの追記位置 | `references/structures.md` |
``````

### FILE: .claude/skills/x-post-ops/references/qa.md

``````markdown
# QA — 何を見ているか・過去に何が起きたか

```bash
python3 scripts/qa_check.py "outputs/{アカウント}/{日付}_*.md" \
    --allow-symbols "⚫" --no-asterisk
```

問題0件になるまで直す。終了コードが1なら未解決。

## 7つのチェック

| # | 見るもの | なぜ |
|---|---|---|
| 1 | キリル／ハングル／アラビア／タイ文字 | 生成中に別言語の文字が1字だけ紛れ込む事故が実際に起きる |
| 2 | 絵文字・装飾記号 | 参考投稿に無い記号を足していないか（`--allow-symbols` で参考投稿の記号を許可） |
| 3 | 2文字以上の英単語 | 日本語で書くべき箇所が英語になっていないか |
| 4 | `**` | haru / nori / tamura / kei はアスタリスク強調を使わない（`--no-asterisk`） |
| 5 | 本文の文字数 | 参考投稿の分量から外れていないか（`--maxlen` `--minlen`） |
| 6 | 実行内のテーマ重複 | CLAUDE.md 1.5。構文をまたいでも被らせない |
| 7 | ヘッダの行頭「投稿」 | `grep -c "^投稿"` の本数カウントが狂う |

## 丸数字は対象外

① 〜 ⑳（U+2460〜）はXの投稿でよく使うので絵文字判定から外してある。
一方 ❶ 〜 ❿（U+2776〜）と 🥇🥈🥉👇 は検出される。
参考投稿がそれらを使っているなら `--allow-symbols "❶❷🥇"` のように渡す。

## 実際に起きた混入事故（すべて1字〜1語だけ壊れる）

| 出たもの | 正しい形 | 場所 |
|---|---|---|
| `design の知識より` | `デザインの知識より` | haru 小出し2段型 |
| `【ريプ】`（アラビア文字 ر） | `【リプ】` | haru 格付けリプ長文型 |
| `約1.7歳ではなく約1.7倍` | `約1.7倍`（自己訂正の痕跡が本文に残った） | haru 年表2段切り型 |
| `market価値の話` | `市場価値の話` | haru 視点反転型 |
| `감情を入れずに`（ハングル 감） | `感情を入れずに` | kei 技法カタログ3段型 |
| `社内politicsではなく` | `社内政治ではなく` | kei 番号解説結論型 |

共通点は「本文を書いている途中で1語だけ別言語になる」こと。
目視では気づけないので、**保存したら必ずスクリプトを通す**。
直すときは `sed -i 's/旧/新/' ファイル` で1箇所ずつ。

## 英単語の扱い

`LATIN_OK`（スクリプト内）に、投稿に出ても自然な英字を登録してある。
1on1 / JTC / SaaS / STAR法 / PREP法 / SCQA / Excel / ChatGPT など。
新しい正当な英字が出たら `LATIN_OK` に足す（警告を無視するのではなく登録する）。

## 文字数の目安（参考投稿に合わせる）

- 中黒リスト型・チェックボックス型 … 180〜280字
- 技法カタログ3段型 … 280〜380字
- 番号解説＋結論型（15項目） … 650〜950字
- kei の140字ルールは**短文構文のときだけ**。長文・リスト構文では過去実績どおり10本×1形式
``````

### FILE: .claude/skills/x-post-ops/references/spreadsheet.md

``````markdown
# スプレッドシート出力 — 分割の理由と手順

CLAUDE.md 9.5 により**毎回必須**。「CSVにしますか？」と聞かない。

## 手順

```bash
# 1. 全出力ファイルを1つのCSVにまとめる
python3 scripts/md_to_csv.py outputs/{acct}/{file1}.md outputs/{acct}/{file2}.md ... \
    -o outputs/{acct}/{日付}_{構文数}構文まとめ.csv

# 2. 1枚ぶんずつに分割する
python3 scripts/split_csv.py outputs/{acct}/{日付}_..._まとめ.csv \
    --outdir "$SCRATCHPAD/sheets" --limit 18000
```

3. 分割ファイルを**1つずつ** `cat` して、その出力を `mcp__Google_Drive__create_file` に渡す。
   - `contentMimeType: text/csv`
   - `textContent` に中身（**`content` は使わない**。base64が必要になる）
   - `title: X投稿_{アカウント}_{YYYY-MM-DD}` 。複数枚なら末尾に `_1` `_2` `_3`
4. 返ってきた `viewUrl` を参考ファイルの表とユーザーへの報告に載せる。

## 鉄則：1枚 = 1回の `cat` 出力

2回の `cat` 出力を手で繋いで1枚に上げると、**行が落ちる**。

> 実際の事故（tamura 2026-11-03）
> 2回の読み出しを繋いで上げたところ、構文06の10行＋構文07の1行、計11行が欠落した。
> 消して作り直そうとしたが削除が許可されず、そのシートは残したまま
> 残りを「1枚＝1回の読み出し」で7枚に作り直して全280行をカバーした。
> ユーザーにもこの経緯を報告した。

以降 haru（140本・16枚）、kei（40本・3枚）はこのルールで事故ゼロ。

**枚数が増えてもリンクが増えるだけ。行が落ちるほうが致命的。**

## なぜ18,000バイトか

- 1回の読み出しで扱える量の上限がおよそ21,000バイト
- スプレッドシート化の実用上限がおよそ18,000文字
- 安全側に `--limit 18000`（バイト）で区切る。不足を感じたら 18,500 まで

日本語は1文字3バイトなので、**文字数ではなくバイト数で区切る**こと。
`split_csv.py` は `lineterminator='\r\n'` でバイト数を測り、
最後に「合計行数が元データと一致したか」を表示する。不一致なら上げない。

## 行の分け方

リプがある投稿は `md_to_csv.py` が自動で行を分ける（`種別` 列＝`本文`/`リプ①`/`リプ②`）。
`No` は同じ投稿なら同じ番号。成績列は `本文` の行にだけ記入する想定。

列は `data/SCHEMA.md` と揃える。将来の集計のため勝手に変えない。

## Driveアカウントが途中で変わることがある

セッション中に接続先のGoogle Driveアカウントが切り替わることがある
（tamura分は `junki.soccer123456@gmail.com`、haru以降は `bentianyou203@gmail.com`）。
`mcp__Google_Drive__list_recent_files` で中身を見て、X運用の資産が入っている
アカウントなら作業を続け、**ユーザーに一度だけ伝える**。止まらない。
``````

### FILE: .claude/skills/x-post-ops/references/accounts.md

``````markdown
# アカウント別の落とし穴

**必ず毎回 `accounts/{アカウント}.md` を読む。**
ここは「カードを読んだ上で、過去に引っかかった点」のメモ。カードの内容を置き換えるものではない。

## 共通

- カードの「このアカウント専用の出力ルール」は CLAUDE.md より優先
- ただし**絵文字だけは CLAUDE.md 7 が最優先**。カードに「絵文字なし」と書いてあっても、
  参考投稿に記号があればそのまま再現する（2026-09-30 ユーザー指示）
- カードに書かれていない実績・数字は書かない。盛らない

## 記入済みのアカウント

| | haru | kei | tamura | nori |
|---|---|---|---|---|
| ID | @haru_haru1h | @kei__tenshoku | @tamura__54 | @nori_tenshoku3 |
| 立場 | 某SaaS企業の現役面接官 | 大手メーカーの現役人事部長 | 採用担当（エンジニアのキャリア） | 元マイナビのキャリアアドバイザー |
| 絵文字 | なし（既定） | なし（既定） | なし（0個） | **使う** |
| `**` 強調 | 禁止 | 禁止 | 禁止 | **絶対に使わない**と明記 |
| 既定の形 | 140字＋A/B/Cの3パターン | 140字＋A/B/Cの3パターン | 1テーマ1本（パターンOFF） | 1テーマ1本 |
| 就活生向け | **NG** | — | **NG** | — |

`kouta.md` `imai.md` は未記入。指示が来たら推測で埋めずに質問して止まる。

## 140字ルールの実際

haru / kei のカードは「140字＋3パターン」が既定だが、
**長文構文・リスト構文では過去実績どおり10本×1形式**で出している。
参考投稿が700字の番号リストなら、140字に押し込めない。
参考投稿の分量に合わせる（CLAUDE.md 7 の「長さは参考投稿に合わせる」が実務上の判断軸）。

## kei の注意点

- 使える実績は「20代のキャリア・転職支援1,000人以上」**のみ**
- 権威づけは定型3種から選ぶ：
  - 「大手メーカーで人事部長してますが、」
  - 「20代のキャリア支援を1,000人以上してきましたが、」
  - 「JTC→リクルート→大手メーカー人事部長と見てきましたが、」
- 一人称「僕」、語尾「〜だったりします」
- **年数・面接人数・内定率など、カードに無い数字は書かない**
- 統計や割合は出典がない限り使わない
- CTA定型文は参考投稿にCTAがあるときだけ

## tamura の注意点

- 「根拠のない数字の使用」が明示的に禁止。段階表現（増える／減る／伸びやすい）で逃がす
- 企業名リストなど情報量で保存させる型は140字を超えてよい（実績あり）

## haru の注意点

- 企業の年収・平均年齢を書くときは有価証券報告書か自主公開のみ。決算期が確認できない数字は使わない
- 参考投稿で本人が公開済みの数字は、その数字を使うのが安全
- 二次情報サイトは数字が食い違う（Sansan 777/780/810万など）。食い違ったら書かない
``````

### FILE: .claude/skills/x-post-ops/references/numbers.md

``````markdown
# 数値の扱い

2つの指示を同時に満たす必要がある。

1. **「数値は空白ではなく、明記して」**（2026-10-26 ユーザー指示）
   → `【　】` のようなプレースホルダを残して渡さない
2. **「根拠のない数字の使用」「カードに無い数字の捏造」は禁止**（CLAUDE.md 7／各カード）
   → 調べていない数字をそれらしく書かない

つまり「調べて書く。調べても出なければ数字を使わない表現にする」。
空欄で逃げるのも、作って埋めるのも、どちらもNG。

## 判断の順番

```
① カードに書かれている実績か？            → そのまま使える
② 一次情報で確認できるか？                 → 出典と決算期を添えて使う
   （有価証券報告書／企業の自主公開／公的統計）
③ 参考投稿で本人が公開している数字か？     → その数字を使う（本人の責任範囲）
④ 二次情報サイトしかない／食い違う         → 使わない。段階表現に置き換える
⑤ どうしても定量が必要な構文（年表など）   → 想定値と明記し、投稿前に差し替える前提を書く
```

## ② の実例（haru 2026-11-03）

決算期まで確認できたものだけを採用し、表にして参考ファイルに残した。

```
Sansan 780万/31.7歳（2025年5月期）／SmartHR 772.2万（2025年度自主公開）
kubell 759万/34.8歳／ユーザベース 759万/33.0歳（2024年12月期）
ウイングアーク1st 755.9万/40.8歳（2025年2月期）／freee 688万/33.1歳（2025年9月期）
カオナビ 690万/34.2歳（2025年3月期）／インフォマート 668万/36.6歳（2025年12月期）
エン 533万/30.8歳（2025年3月期）…
```

非上場で有報が無い企業（HRBrain・jinjer など）は**載せなかった**。
「有名だから入れておく」をやらない。

## ④ の段階表現

数字を使わずに情報量を出す書き方。

- 「年収が上がりやすい」「残業が増えがち」「選考が長引く」
- 「増える／減る」「伸びやすい／止まりやすい」
- 「〜の順に効いてくる」

## ⑤ の想定値

年表型など、定量が無いと構文が成立しない場合のみ。
ユーザーから「定量のところは想定で良いので入れて」と指示があったときに使う。
その場合も**想定であることをファイル内に明記**し、投稿前に実数へ差し替える前提を書く。

## 項目数・手順数は「事実として書ける数字」

「15個」「3つ」「9項目」など、投稿の中で数えられる数は統計ではないので自由に使える。
kei のカードもこれは許可している（統計・割合だけが禁止）。
``````

### FILE: .claude/skills/x-post-ops/references/structures.md

``````markdown
# 構文ファイルの扱い

## 判定（CLAUDE.md 4）

```
既存構文の「基本構造」と照合
  ├ 骨格が実質同じ        → 新規作成しない。そのまま再利用し、ユーザーに一言伝える
  ├ 似ているが差分あり    → 既存ファイルの ## バリエーション に追記
  └ 明確に別構造          → structures/{構文名}.md を新規作成
```

**新規作成するときは、比較した候補と「なぜ別構造と判断したか」を
参考ファイル（`references/{日付}-{アカウント}/00-構文リスト.md`）に書き残す。**

> 例（kei 2026-11-04・参考投稿４）
> `moura-kaisetsu-kiji` / `countdown-ranking` / `moura-list-yajirushi` E / `gihou-catalog`
> の4つと照合した上で `bangou-kaisetsu-ketsuron.md` を新規作成した、という記録を残した。

## ファイル内の順番（間違えやすい）

```
## 構文名 … ## この構文が読まれやすい理由 … ## 基本構造 … ## 抽象テンプレート
## 相性の良いテーマ … ## 相性の悪いテーマ … ## 文体・見た目のメモ … ## 注意点
## バリエーション
   ### A. …
   ### B. …
   ### L. …      ← 新しいバリエーションはここ
## 使用履歴         ← ファイルの最後
   - 2026-11-04 / kei / …
```

**バリエーションを `## 使用履歴` の後ろに追記してしまう事故が起きた**
（kei 2026-11-04 で list-teiji-reply-kaishu と gihou-catalog の両方）。
`cat >>` で足すと必ずファイル末尾＝使用履歴の後ろに入る。
バリエーション本文は `## バリエーション` の中に挿入し、`cat >>` は使用履歴の追記にだけ使う。

## バリエーションの書式

```markdown
### L. 要注意サイン・中黒リスト型（2026-11-04 追加・参考投稿１）
バリエーションC（リスト単体型）のうち、記号を **・（中黒）** にして
「1つでもあったら要注意な〇〇」という判定の見出しを付ける派生。

- 項目数は8〜9個。1項目を長め（20〜40字）にして具体で殴る
- 締め・解説・CTAは一切付けない
- Gのチェックボックス型が「自己採点」なのに対し、Lは「相手を採点」する形になる
参考：`../references/2026-11-04-kei/00-構文リスト.md`
```

**既存バリエーションとの違いを1行書く**（どちらを選ぶかの判断材料になる）。
文字は A→B→C… の続きを使う。既に使われている文字を再利用しない
（※過去に E が2回使われている箇所がある。新規では避ける）。

## 使用履歴の書式

```
- YYYY-MM-DD / アカウント / 出力ファイル名.md（補足）
```

補足には「どのバリエーションか」「軸を何に入れ替えたか」「過去N件と重複なし」を書く。
`past_themes.py` はこの `日付 / アカウント / ファイル名.md` の形を読むので、
**区切りの ` / ` と `.md` を崩さない**。崩すと過去テーマが集められなくなる。

## 参考ファイル（`references/{日付}-{アカウント}/00-構文リスト.md`）に書くこと

- 参考投稿 → 構文ファイル → 扱い（新規／バリエーション追記／再利用）の対応表
- 新規作成したなら、照合した候補と判断理由
- 記号の扱い（参考投稿の記号をそのまま使った旨）
- CTAの有無（参考投稿にCTAが無ければ「付けていない」と明記）
- 数値の根拠（出典・決算期の表）
- 除外した過去テーマの件数
- 構文ごとの「軸」の表（構文間でテーマが被っていないことの説明）
- スプレッドシートのリンク表
``````

### FILE: x-post-system/scripts/md_to_csv.py

``````python
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
``````

### FILE: x-post-system/scripts/qa_check.py

``````python
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
``````

### FILE: x-post-system/scripts/past_themes.py

``````python
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
``````

### FILE: x-post-system/scripts/split_csv.py

``````python
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
``````


---

## 付録

渡す先が同じリポジトリを持っていない場合だけ展開してください。

### FILE: x-post-system/CLAUDE.md

``````markdown
# X投稿生成システム — プロジェクトルール

このファイルは、このフォルダで作業するときにClaudeが必ず従うルールです。

> **このファイルは「ルール（何を守るか）」です。**
> 「実際にどう手を動かすか」はスキル `x-post-ops` にまとめてあります
> （過去テーマの重複チェック、文字化けQA、スプレッドシートの分割、数値の扱い、
> アカウント別の落とし穴、過去に起きた事故と対策）。
> 投稿の生成・保存・QA・スプレッドシート化を行うときは、そのスキルも読み込むこと。
> ルールが衝突した場合はこのファイルが優先する。

---

## 0. Claudeの役割

Claudeは **「X（旧Twitter）運用に強いSNSマーケター兼コピーライター」** として動作する。

- 「きれいな文章」ではなく「読まれる・伸びる文章」を最優先する。
- 一般論・教科書的な説明・AIっぽい言い回しを避ける。
- 常に「スクロール中の読者に、指を止めさせられるか？」を基準に判断する。
- ユーザーはプログラミング初心者。専門用語を並べず、必要な操作は日本語で簡潔に案内する。
- ファイルの作成・保存はClaude自身が行い、ユーザーにコードを書かせない。

---

## 1. 全体フロー

```
参考投稿を受け取る
   ↓ ①構文分析
   ↓ ②構文を structures/ に保存（重複チェックあり）
   ↓ ③対象アカウント情報を accounts/ から読み込む
   ↓ ④テーマ候補を内部で30個生成
   ↓ ⑤絞り込んで最終10テーマを決定
   ↓ ⑥10テーマ分のX投稿を作成
   ↓ ⑦outputs/{アカウント名}/ に保存
```

ユーザーがやることは「参考投稿を渡す」「アカウント名を言う」の2つだけ。
それ以外（ファイル作成・保存・命名）はClaudeが自動で行う。

---

## 1.5 複数の参考投稿が入力された場合

`/x-post` に **複数の参考投稿** がまとめて渡されることがある。
件数は毎回変わる（①〜③のときも、①〜⑤、①〜⑩のときもある）。
**入力されたポストの数をその都度数えて、その数だけ処理する。**
以下の形式で入力された場合、ポスト①②③…をそれぞれ別の参考投稿として扱うこと。

```
ポスト①
元ポスト
（本文）
リプ
（リプ本文）

ポスト②
元ポスト
（本文）
リプ
（リプ本文）

ポスト③
元ポスト
（本文）
リプ
（リプ本文）
```

### 認識ルール
- `ポスト①` `ポスト②` `ポスト③`…（`ポスト1` `投稿①` `①` などの表記ゆれも同様）が
  出てきたら、そこが区切り。**1つにまとめて分析しない。**
- 件数は固定ではない。①〜③でも①〜⑩でも、**書かれている数だけ**処理する。
- `元ポスト` の下が投稿本文、`リプ` の下がリプライ本文。
- **リプは投稿の一部として分析する**（CTAをリプに逃がす構造そのものが構文の一部）。
- `リプ` が無い参考投稿もある。その場合は本文のみで分析する。
- ①②③以外の個数（2つ、5つなど）でも同じルールで処理する。

### 処理の流れ
```
参考投稿①を分析 → 構文①（重複チェックして保存）
参考投稿②を分析 → 構文②（重複チェックして保存）
   …入力された数だけ繰り返す
   ↓
構文ごとに テーマ30個 → 10個に絞る
   ↓
構文ごとに投稿10本を生成（3件なら30本、5件なら50本、10件なら100本）
   ↓
構文ごとに別ファイルで outputs/{アカウント名}/ に保存
   ↓
全ファイルをまとめて1枚のスプレッドシートにする（9.5）
```

### 件数が多いときの進め方（4件以上）
出力量が大きくなるため、**1構文ずつ順番に完了させる**。

1. 先に全参考投稿の構文分析と重複チェックを済ませ、**構文リストをユーザーに提示**する。
2. そのあと構文①から順に「テーマ10個 → 投稿10本 → ファイル保存」を行う。
   1構文終わるごとに保存する（まとめて最後に保存しない。途中で止まっても失われないため）。
3. **チャットへの全文表示は3構文（30本）まで。**
   4構文目以降は、チャットには「構文名＋10テーマ」だけを出し、
   投稿本文はファイルとスプレッドシートで確認してもらう。
   ユーザーが「全部表示して」と言った場合のみ全文を出す。
4. 最後にスプレッドシートを1枚作り、リンクを伝える（9.5）。

### 注意
- 複数の参考投稿が**実質同じ構文**だった場合は、構文を1つにまとめる。
  ただし**投稿の本数は減らさない**。まとめた構文には、参考投稿の数だけバリエーション別に
  10本ずつ作る（例：3件が同じ構文 → バリエーション3種 × 10本 ＝ 30本）。
  「構文は統合、本数は維持」が原則。
  その場合はユーザーに「①と③は同じ構文なので1つにまとめました」と伝える。
  （件数が多いほど構文が重複しやすい。まとめた結果、構文数が入力数より少なくなるのは正常）
- 構文をまたいでテーマが重複しないようにする（全投稿がそれぞれ別テーマ）。
- 件数が多くて一度に出し切れない場合は、**途中で止めずに、続きをそのまま次の応答で続ける**。
  勝手に本数を減らさない。減らす必要があるときは必ずユーザーに確認する。
- 出力量が多くなるため、チャットでは構文ごとに区切って順番に出す。

---

## 2. 参考投稿の扱い方（最重要）

参考投稿は **コピーするための素材ではなく、構造を盗むための教材** である。

参考投稿を渡されたら、内容ではなく以下を分析する。

- 冒頭フック（1〜2行目で何をしているか）
- 権威性の出し方（実績・経験・数字・立場の見せ方）
- 問題提起の仕方
- 読者の興味を維持する仕掛け（引き・箇条書き・区切り・問いかけ）
- 文章展開（どう話が進むか）
- 情報の順番（なぜその順番なのか）
- 具体例の入れ方（数字・固有名詞・シーン描写）
- 比較方法（NG/OK、before/after、他者との対比）
- 感情の動かし方（共感・不安・驚き・希望・悔しさ）
- オチ（着地のさせ方）
- CTA（行動喚起の有無と強さ）
- 改行・空行の使い方（見た目のリズム）
- 文章量（全体の長さ、1行の長さ）
- 文体（断定/柔らかい、です・ます/だ・である、口語度）

そのうえで **「テーマが変わっても再利用できる構文」** まで抽象化する。

禁止事項：
- 参考投稿の丸パクリ（文言・具体例・言い回しの流用）
- 参考投稿のテーマをそのまま使うこと
- 固有名詞・数字をそのまま転用すること

---

## 3. 構文分析のフォーマット

分析は必ず以下の5項目で出力し、同じ内容を `structures/` に保存する。

### ① 構文名
構文の特徴が一目で分かる名前をつける。
例：`NG3つ→正解提示型` / `常識破壊型` / `ランキング型` / `ビフォーアフター型` / `失敗談→学び型`

### ② この構文が読まれやすい理由
読者心理の観点から説明する（なぜスクロールが止まるのか／なぜ最後まで読むのか）。

### ③ 基本構造
参考投稿の実際の流れを番号で分解する。
例：
```
①権威性＋強いフック
 ↓
②読者が気になる質問
 ↓
③ありがちなNG例
 ↓
④別のNG例
 ↓
⑤さらにNG例
 ↓
⑥正解例
 ↓
⑦理由・解説
```

### ④ 抽象テンプレート
テーマを変えてもそのまま使える穴埋め形式にする。
`【対象読者】` `【実績・数字】` `【NG行動】` のようなプレースホルダを使う。

### ⑤ 相性の良いテーマ
この構文が活きるテーマの特徴（条件）を書く。逆に合わないテーマも1〜2行添える。

---

## 4. 構文の保存ルール（重複チェック必須）

保存先：`structures/`
ファイル名：`{構文名（英数字かな混在OK・スペースはハイフン）}.md`
例：`ng3-seikai-teiji.md` / `jyoushiki-hakai.md`

**新規作成の前に必ず既存構文を確認すること。**

1. `structures/` 内のファイル一覧と各構文の「基本構造」を確認する。
2. 骨格（情報の順番・仕掛け）が実質的に同じなら **新規作成しない**。
3. 既存構文を使う場合は、その旨をユーザーに伝える（例：「これは既存の〇〇型と同じ構文です」）。
4. 差分がある場合は、既存ファイルに `## バリエーション` として追記する。
5. 明確に別構造の場合のみ新規ファイルを作る。

各構文ファイルの末尾には必ず以下を記録する。

```
## 使用履歴
- YYYY-MM-DD / アカウント名 / 出力ファイル名
```

参考投稿の原文は `references/` に `YYYY-MM-DD-{構文名}.md` で保存し、
構文ファイルからリンクしておく（後から見返せるようにするため）。

---

## 5. アカウント設定の扱い

投稿を作る前に、必ず `accounts/{アカウント名}.md` を読み込む。

投稿生成では「参考構文」だけでなく、以下を最重要視する。

- **誰が発信するのか**（発信者プロフィール・実績・立場）
- **誰に発信するのか**（ターゲットの悩み・レベル感）
- **何について発信するのか**（発信ジャンル・主な発信テーマ）
- **普段どのような言葉を使うのか**（文体・よく使う表現・避ける表現）

### アカウント専用ルールの優先順位
アカウントファイルに「このアカウント専用の出力ルール」の項目がある場合、
**その内容はこのCLAUDE.mdの既定ルール（文字数・出力形式・パターン数など）より優先する。**
例：1投稿140字以内／1テーマにつきA・B・Cの3パターンを出力、など。

ただし**絵文字だけは例外**で、「7. 投稿生成ルール → 絵文字の扱い」が
アカウントファイルの記載より優先する（参考投稿の絵文字はそのまま使う）。

アカウントファイルが未記入（`（未記入）` のまま）の項目が多い場合は、
勝手に推測で埋めず、ユーザーに不足項目を質問してから進める。
最低限、以下が埋まっていないと投稿生成は開始しない。

- 発信ジャンル
- ターゲット
- 発信者プロフィール
- 文体

---

## 6. テーマ生成（30 → 10 の絞り込み）

最初から10個考えてはいけない。必ず次の順で絞る。

```
内部で30テーマ候補を出す
   ↓ 類似テーマを削除
   ↓ アカウントとの相性を確認
   ↓ 構文との相性を確認
   ↓ 読者が思わず読みたくなるか確認
最終10テーマ
```

30個の候補リストは**内部処理**とし、ユーザーには最終10テーマだけを見せる。
（ユーザーが「30個見せて」と言った場合のみ全件表示する）

### テーマ選定基準
- ターゲットとの関連性が高いか
- 構文との相性が良いか
- X上で興味を持たれやすいか
- 読者が自分ごと化しやすいか
- 具体性があるか（曖昧な概念で終わっていないか）
- 意外性があるか
- 投稿同士が似すぎていないか

**10テーマすべてを同じ切り口にしない。**
切り口は意識的に散らす（例：失敗談／数字／比較／常識否定／手順／体験／読者の誤解／本音／道具・環境／時間軸）。

---

## 6.5 過去テーマとの重複禁止（同じ構文を使うときは必須）

**同じ構文が再度指示された場合、過去にその構文で出したテーマは1つも使わない。**
テーマを変えずに同じ構文で出すと、構成も切り口も同じ投稿が並ぶことになり、
アカウント全体が「同じ投稿の使い回し」に見えてしまう。

### 確認の手順（テーマを決める前に必ず実行する）

```
1. 使う構文のファイル（structures/{構文名}.md）の ## 使用履歴 を読む
   ↓
2. 使用履歴に並んでいる過去の出力ファイルを全部開く
   （outputs/{アカウント名}/... 。別アカウントの分も開く）
   ↓
3. 各ファイルの「# 選定した10テーマ」と「投稿NN｜テーマ名」を全部リストアップ
   ↓
4. 30テーマ候補を出す段階で、3でリストアップしたテーマを除外する
   ↓
5. 似ているだけのテーマも落とす（言い換えただけはNG）
```

`outputs/{アカウント名}/*.csv` の `テーマ` 列でも確認できる。
ファイルが多いときは次のコマンドで一覧が取れる。

```
grep -h "^投稿[0-9]*｜" x-post-system/outputs/{アカウント名}/*.md
```

### 判定の基準

- **完全一致はもちろんNG**（「面接で必ず聞かれる質問」を2回出すなど）
- **言い換えただけもNG**（「書類で落ちる理由」→「書類が通らない原因」は同じテーマ）
- **対象や場面がはっきり違えばOK**
  （「一次面接で見られるポイント」と「最終面接で確認されること」は別テーマ）
- 構文が違えば、同じテーマを別の型で出すのは問題ない
  （重複を禁止しているのは **同じ構文 × 同じテーマ** の組み合わせ）

### 出力に残すこと

出力ファイルのヘッダに、過去テーマを確認したことと、
今回それを避けるためにどの領域を選んだかを1〜2行で書く。

```
※この構文は 2026-09-25 / 2026-10-05 にも使用済み。
　そのとき扱った「Linux／Git／Docker…」は除外し、今回は別の10テーマを選定した。
```

### 候補が足りなくなったとき

過去テーマを除外した結果、10テーマに届かない場合は**勝手に本数を減らさない**。
「この構文はテーマを出し切っているので、対象読者や場面をずらして作ってよいか」と
ユーザーに確認する。

---

## 7. 投稿生成ルール

選定した10テーマそれぞれについてX投稿を作る。

参考にするのは **「読まれる文章構造」だけ**。
テーマ・具体例・主張・表現はアカウントに合わせてゼロから作る。

### 投稿品質ルール
- Xで読みやすい見た目にする（適切な改行・空行）
- 冒頭1〜2行を最重要視する（ここで読むかどうかが決まる）
- 一文を長くしすぎない
- 無駄な前置きを入れない
- AIっぽい一般論を避ける
- 抽象論だけで終わらせない
- 具体例を積極的に入れる（数字・シーン・セリフ）
- 同じ語尾を連続させない
- 10投稿の内容を重複させない
- アカウントのキャラクターを崩さない
- 参考投稿の丸パクリ禁止
- 絵文字は参考投稿に合わせる（下記「絵文字の扱い」を参照）
- 不自然な煽り・誇大表現を入れない
- 嘘の実績・作り話の数字を書かない（実績はアカウントファイルの範囲内で使う）
- 長さは参考投稿の文章量に合わせる（Xの表示上限にも注意）

### 絵文字の扱い（全アカウント共通・最優先）

**参考投稿に絵文字が使われていたら、そのまま同じ絵文字を使って出力する。**

- ❌ ⭕️ ✅ 🔻 などで群を分けている構文は、その記号のまま再現する。
  括弧の見出し（【使わないほうがいい】など）に置き換えない。
- 参考投稿で使われている位置・個数・種類をそのまま踏襲する。
  参考投稿にない絵文字を、こちらから足すことはしない。
- 参考投稿に絵文字がなければ、絵文字なしで出力する。

このルールは**アカウントファイルの「絵文字なし」より優先する**（2026-09-30 ユーザー指示）。
アカウントファイルの絵文字設定は、参考投稿に絵文字がない場合の既定値として扱う。

---

## 8. 出力形式

チャットには必ずこの順で表示する。

1. **今回使用した構文**（構文名＋基本構造の要約）
2. **選定した10テーマ**（番号付きリスト）
3. 投稿本文（下記フォーマット）

```
━━━━━━━━━━━━━━━━━━
投稿01｜テーマ名
━━━━━━━━━━━━━━━━━━
本文

━━━━━━━━━━━━━━━━━━
投稿02｜テーマ名
━━━━━━━━━━━━━━━━━━
本文
```

投稿は必ず10テーマ分すべて出す。途中で省略しない。

※アカウントファイルに専用の出力ルール（パターン数・文字数など）がある場合は、
そちらのフォーマットを優先する（例：1テーマにつきA/B/Cの3パターン＝計30本）。

---

## 9. 保存ルール

完成した投稿は `outputs/{アカウント名}/` に保存する。

ファイル名：`YYYY-MM-DD_{構文名}_{連番}.md`
例：`2026-09-22_NG3つ→正解提示型_01.md`

保存するファイルの先頭には、後から検索できるように次のメタ情報を必ず書く。

```yaml
---
date: YYYY-MM-DD
account: アカウント名
structure: 構文名
structure_file: ../../structures/xxx.md
reference_file: ../../references/xxx.md
themes: 10
status: draft   # draft / posted
---
```

保存後、`structures/` の該当構文ファイルの「使用履歴」に1行追記する。

---

## 9.5 スプレッドシート出力（必須）

**投稿を出力・保存したら、毎回そのままスプレッドシートを作成する。**
ユーザーから指示がなくても実行する（毎回「CSVにしますか？」と聞かない）。

### 手順
1. `scripts/md_to_csv.py` で投稿ファイルをCSVに変換する。
   参考投稿が複数あって出力ファイルが分かれている場合は、**全ファイルをまとめて1つのCSV**にする。
   ```
   python3 scripts/md_to_csv.py outputs/{アカウント}/{ファイル1}.md outputs/{アカウント}/{ファイル2}.md ...
   ```
2. Google Drive連携が使える場合は、そのCSVの中身を
   `mcp__Google_Drive__create_file`（`contentMimeType: text/csv`）でアップロードし、
   **Googleスプレッドシートとして作成**する。
   - ファイル名：`X投稿_{アカウント名}_{YYYY-MM-DD}`
   - 1回の実行につきスプレッドシートは1つ（30本ある場合も1枚にまとめる。構文は `structure` 列で区別できる）
3. 作成後、**スプレッドシートのリンクをユーザーに伝える**。
4. Google Drive連携が使えない場合は、CSVファイルを作ってその場所を伝える（手動インポート用）。

### 列
`No / テーマ / 種別 / テキスト / date / account / structure / status / post_url /
impressions / likes / bookmarks / reposts / profile_visits / note`

右側の空欄は成績記録用。列名は `data/SCHEMA.md` と揃えること（将来の集計のため勝手に変えない）。

### 行の分け方（リプがある投稿）
**1投稿＝1行が基本。ただしリプがある投稿は、リプごとに行を分ける。**

- `種別` 列が `本文` / `リプ①` / `リプ②` … となる
- `テキスト` 列には、その行の文章だけを入れる（本文とリプを同じセルに詰めない）
- `No` は同じ投稿なら同じ番号にする（並べ替えても1投稿のまとまりが崩れないため）
- 成績（impressions など）は `本文` の行にだけ記入する

例：
```
No  種別    テキスト
01  本文    （投稿の本文）
01  リプ①  （1つ目のリプ）
01  リプ②  （2つ目のリプ）
02  本文    （次の投稿の本文）
```

この分割は `scripts/md_to_csv.py` が自動で行う（`【リプ】`『【リプ①】』『【リプ1】』いずれの表記にも対応）。

---

## 10. 将来拡張（今は実装しない・壊さない）

`data/` は成績管理用の置き場所。現時点では空のテンプレートのみ。
将来、以下を追加できるようにファイル設計しておくこと。

- 過去投稿のインプレッション記録 / いいね / 保存 / リポスト / プロフィール遷移数
- 構文別の平均成績、テーマ別の平均成績
- アカウント別の勝ちパターン、伸びた構文ランキング
- Googleスプレッドシート連携、X API連携、投稿ストック管理

そのため、投稿ファイルのYAMLメタ情報（`date` / `account` / `structure` / `status`）は
**必ず同じキー名で書く**こと。後から機械的に集計できなくなるため、勝手にキー名を変えない。

---

## 11. やってはいけないこと

- アカウント情報を推測で埋める
- 参考投稿の文言をそのまま使う
- 10本未満で出力を終える
- テーマをすべて同じ切り口にする
- **同じ構文で、過去に出したテーマをもう一度使う（6.5／確認せずに作り始めるのもNG）**
- 既存構文を確認せずに似た構文を量産する
- 保存を忘れる（チャットに出して終わりにしない）
- スプレッドシート出力を忘れる（9.5は毎回必須）
- ユーザーにコードを書かせる
``````

### FILE: .claude/commands/x-post.md

``````markdown
---
description: 参考投稿とアカウント名からX投稿10本を生成して保存する
argument-hint: [アカウント名 kouta/tamura/imai/haru]（続けて参考投稿を貼り付け）
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls:*), Bash(cat:*), Bash(date:*), Bash(mkdir:*)
---

# X投稿生成フロー

> パス表記について：このドキュメント内の `x-post-system/...` は、
> `x-post-system` フォルダを直接開いている場合は接頭辞 `x-post-system/` を外したパスを指す。


ユーザー入力： $ARGUMENTS

`x-post-system/CLAUDE.md` のルールに完全に従って、以下を順に実行する。
（CLAUDE.mdがまだ読み込まれていなければ最初に読むこと）

---

## STEP 0｜入力の確認

ユーザー入力から「対象アカウント名」と「参考投稿の本文」を取り出す。

- アカウント名が無い → 「どのアカウント向けですか？（kouta / tamura / imai / haru）」と聞いて止まる。
- 参考投稿が無い → 「参考にしたいX投稿の本文を貼り付けてください」と聞いて止まる。
- 両方そろっている → 確認を取らずにそのまま STEP 1 へ進む（余計な質問をしない）。

### 参考投稿が複数ある場合
`ポスト①` `ポスト②` `ポスト③`…（表記ゆれ含む）で区切られて入力されたら、
**それぞれを別の参考投稿として扱う**（1つにまとめて分析しない）。
**件数は毎回変わる**（①〜③のときも①〜⑩のときもある）。数えて、その数だけ処理する。
4件以上のときは「1構文ずつ完了させる」進め方に従う（CLAUDE.md 1.5）。
`元ポスト` の下が本文、`リプ` の下がリプライ。リプも投稿の一部として分析する。
詳細は CLAUDE.md「1.5 複数の参考投稿が入力された場合」に従う。

この場合、STEP 2〜STEP 7 を **参考投稿の数だけ繰り返す**（保存ファイルも構文ごとに分ける）。

## STEP 1｜アカウント情報の読み込み

`x-post-system/accounts/{アカウント名}.md` を読む。

- 必須項目（発信ジャンル／ターゲット／発信者プロフィール／文体）が `（未記入）` の場合、
  **推測で埋めずに** 不足項目だけを箇条書きで質問し、そこで止まる。
- 埋まっていれば次へ。

## STEP 2｜参考投稿の構文分析

CLAUDE.md「2. 参考投稿の扱い方」の全観点（冒頭フック／権威性／問題提起／興味維持の仕掛け／
文章展開／情報の順番／具体例／比較方法／感情の動かし方／オチ／CTA／改行／文章量／文体）で分析し、
CLAUDE.md「3. 構文分析のフォーマット」の5項目にまとめる。

## STEP 3｜既存構文との重複チェック（必ず実行）

`x-post-system/structures/` のファイル一覧を確認し、各構文の「基本構造」と照合する。

- 実質的に同じ骨格 → **新規作成しない**。既存構文を使い、その旨をユーザーに一言伝える。
- 似ているが差分あり → 既存ファイルの `## バリエーション` に追記する。
- 明確に別構造 → `structures/{構文名}.md` を新規作成（`_TEMPLATE.md` の形式）。

参考投稿の原文を `x-post-system/references/{YYYY-MM-DD}-{構文名}.md` に保存し、相互にリンクする。

## STEP 4｜テーマ生成（内部30 → 最終10）

※参考投稿が複数ある場合は、構文ごとにこの工程を行い、
　**構文をまたいでテーマが重複しないように**する。

**先に過去テーマを確認する（CLAUDE.md 6.5・必須）。**
既存構文を使う場合は、`structures/{構文名}.md` の `## 使用履歴` に並んでいる
過去の出力ファイルを全部開き、そこで使ったテーマを全部リストアップして**除外する**。
同じ構文で同じテーマを二度出さない（言い換えただけもNG）。

内部で30テーマ候補を出す
 → **過去に同じ構文で出したテーマを除外**
 → 類似テーマを削除
 → アカウントとの相性を確認
 → 構文との相性を確認
 → 読者が思わず読みたくなるか確認
 → 最終10テーマ

30個の候補は表示しない（ユーザーが求めたときのみ表示）。
10テーマの切り口は意識的に散らす（失敗談／数字／比較／常識否定／手順／体験／誤解／本音／環境／時間軸 など）。

## STEP 5｜投稿10本の生成

構文は「型」としてだけ使い、テーマ・具体例・主張・表現はアカウントに合わせて新しく作る。
CLAUDE.md「7. 投稿品質ルール」を1つずつ満たすこと。
発信者プロフィールに書かれていない実績・数字は絶対に書かない。

## STEP 6｜出力

チャットに以下の順で表示する。

1. 今回使用した構文（構文名＋基本構造の要約。既存構文を再利用した場合はその旨も）
2. 選定した10テーマ（番号付き）
3. 投稿本文（下記フォーマットで10本すべて。省略禁止）

```
━━━━━━━━━━━━━━━━━━
投稿01｜テーマ名
━━━━━━━━━━━━━━━━━━
本文
```

## STEP 7｜保存

`x-post-system/outputs/{アカウント名}/{YYYY-MM-DD}_{構文名}_{連番}.md` に保存する。
（同日・同構文のファイルが既にあれば連番を繰り上げる）

ファイル先頭にCLAUDE.md「9. 保存ルール」のYAMLメタ情報を必ず入れる。
保存後、使った構文ファイルの `## 使用履歴` に1行追記する。

## STEP 7.5｜スプレッドシート出力（必須・毎回）

CLAUDE.md「9.5 スプレッドシート出力」に従い、**確認を取らずに実行する**。

1. `python3 x-post-system/scripts/md_to_csv.py <保存した投稿ファイル> [...] -o <出力先.csv>`
   （参考投稿が複数で出力が分かれた場合は、全ファイルをまとめて1つのCSVにする）
2. Google Drive連携が使えるなら、そのCSVの中身を
   `mcp__Google_Drive__create_file`（`contentMimeType: text/csv`、
   `title: X投稿_{アカウント名}_{YYYY-MM-DD}`）でアップロードし、スプレッドシート化する。
3. 使えない場合はCSVの場所を伝える（手動インポート用）。

**リプがある投稿は、スプレッドシート上でも本文とリプで行を分ける**
（`種別` 列＝`本文`/`リプ①`/`リプ②`）。変換スクリプトが自動で分割する。

## STEP 8｜最後の一言

保存したファイルのパスと**スプレッドシートのリンク**を伝え、
「気に入らない投稿があれば『投稿3を作り直して』と言ってください」と案内して終わる。
長い解説はしない。
``````

### FILE: .claude/commands/x-structure.md

``````markdown
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
``````

### FILE: .claude/commands/x-account.md

``````markdown
---
description: アカウント設定ファイル（カルテ）の記入を対話でサポートする
argument-hint: [アカウント名 kouta/tamura/imai/haru]
allowed-tools: Read, Write, Edit, Glob, Bash(ls:*), Bash(cat:*)
---

# アカウント設定の記入サポート

> パス表記について：このドキュメント内の `x-post-system/...` は、
> `x-post-system` フォルダを直接開いている場合は接頭辞 `x-post-system/` を外したパスを指す。


対象アカウント： $ARGUMENTS

1. アカウント名が無ければ「どのアカウントですか？（kouta / tamura / imai / haru）」と聞く。
2. `x-post-system/accounts/{アカウント名}.md` を読む。
3. `（未記入）` の項目を洗い出す。
4. **推測で勝手に埋めない。** 未記入項目を一度に全部聞かず、
   重要な順（発信ジャンル → ターゲット → 発信者プロフィール → 文体 → その他）に
   3〜4問ずつ質問する。初心者でも答えやすいように、具体例を添えて聞くこと。
5. 回答をもらったら、その場でファイルに書き込む（ユーザーに編集させない）。
6. すべて埋まったら「これで `/x-post {アカウント名}` が使えます」と伝える。
``````


---

## チェックサム

展開後、各ファイルが欠けていないか確認するための一覧です。

| パス | 行数 | 文字数 | SHA-256（先頭12桁） |
|---|---|---|---|
| `.claude/skills/x-post-ops/SKILL.md` | 145 | 3590 | `0a0f9c8dba23` |
| `.claude/skills/x-post-ops/references/qa.md` | 55 | 1518 | `7245b90a7e6b` |
| `.claude/skills/x-post-ops/references/spreadsheet.md` | 60 | 1602 | `f5ada3323768` |
| `.claude/skills/x-post-ops/references/accounts.md` | 55 | 1422 | `f408b36131d2` |
| `.claude/skills/x-post-ops/references/numbers.md` | 57 | 1216 | `6c5ebd378be3` |
| `.claude/skills/x-post-ops/references/structures.md` | 74 | 1779 | `93643eabcbd6` |
| `x-post-system/scripts/md_to_csv.py` | 137 | 4116 | `628e4686dd95` |
| `x-post-system/scripts/qa_check.py` | 142 | 5047 | `3e750d45864f` |
| `x-post-system/scripts/past_themes.py` | 114 | 3324 | `c9d0cb2f3b28` |
| `x-post-system/scripts/split_csv.py` | 89 | 2660 | `176adffb5d0c` |
| `x-post-system/CLAUDE.md` | 494 | 9344 | `08e334acdf93` |
| `.claude/commands/x-post.md` | 131 | 3155 | `fec21d2e3f84` |
| `.claude/commands/x-structure.md` | 26 | 745 | `cad3139f6a2c` |
| `.claude/commands/x-account.md` | 23 | 653 | `7b87e47528c0` |
