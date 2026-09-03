# Hop Count Instrument

常時ロード分（`adapter/claude/CLAUDE.md` + `rules/**` + skill description）に対する削減作業の before / after を比較可能にするための計測固定面。#1564 の検証手段の実体であり、以降の削減作業（#1587 / #1588 / #1589 ほか）はすべてこの instrument を前提とする。

計測対象は **規則の適用瞬間に、必要な literal に到達するまでのファイル遷移数**。同一タグに対して同じ数値を再現する静的到達性の計数であり、実行時計測ではない。

**baseline tag = `build-2026-07-28.5`**（commit `6e616cb`）。以下の**跳躍数**はすべてこのタグ時点の実測。表中の行番号のみ、本 instrument を導入した PR（#1586-#1589）のマージ後の位置に合わせてある — 同 PR はいずれのシナリオでもツール呼び出し跳躍を変えていない。

---

## 計数規則

- **起点** = そのシナリオの適用瞬間を名指しする always-on リテラル。固定の実体は **trigger 文そのもの**（各シナリオに `anchor:` として記載）であり、併記の `file:line` はその位置の目安。行番号は当該ファイルを触る PR で更新する（行番号のずれ自体は差し替えではない）。
- **追跡対象** = 起点から、そのシナリオが必要とする literal に到達するために load-bearing な明示ポインタのみ。ソース中に書かれていない連想的な参照は数えない。
- **1跳躍** = ファイル遷移1回。同一ファイル内の節移動は跳躍ではない。
- **分類**:
  - **文脈内跳躍** = 遷移先が `rules/**` または `adapter/claude/CLAUDE.md`（常時ロード分。ツール呼び出しを要さない）
  - **ツール呼び出し跳躍** = 遷移先が `skills/*/SKILL.md` 本体 / `docs/` / hook (`adapter/*/hooks/*`) / `adapter/*/agents/*.md` / `adapter/*/hooks-settings.md`
- **非計数** = `memory/**`（workspace-local、仕様リテラルではない）、git 履歴、外部 URL、MCP ツール呼び出し（ファイル遷移ではない）。

### 合格条件

各シナリオの **ツール呼び出し跳躍が減るか据え置き**。増えた場合は、増分の理由を PR 本文で説明できない限り **regression として扱う**。

文脈内跳躍の増加は合格条件に含めない。常時ロード分の内側の重複を削ると文脈内跳躍が1つ増えるのは設計上の想定挙動であり、これを罰すると重複削除ができなくなる（#1564「主軸の確定」）。

### 再計測手順

「シナリオ集合」の各行に記録された経路を辿り直し、(1) 記録済みポインタが消えていないか、(2) 起点と目的 literal の間に新しいツール呼び出し跳躍が挿入されていないか、の2点を確認する。

**記録された経路は判断の幅を狭めるが、判断を無くしはしない。** 残る判断は次の2点に集中する。再計測者ごとにぶれるのはここなので、数値だけでなく「なぜ数えた／数えなかったか」を経路行に書き残す（各シナリオの `非計数` 行がその置き場）。

- **どのポインタが load-bearing か**（計数規則 :14）。目的 literal への到達に本当に必要な参照と、隣接して書かれているだけの連想的参照の線引きは自明ではない。実測: 本 instrument をブレーキ1（`skills/evolution-parallel-agent-eval`、N=3）に掛けたところ、3体の評価者がいずれもこの線引きを独自に判断し、うち2体が記録と異なる分割に達した。S2 / S3 の過大計上はこれで発覚した。
- **どこまでが当該シナリオの鎖か**（シナリオ間の境界）。別シナリオが既に計測している区間は、二重計上を避けるため数えない。境界の位置そのものが判断であり、記録から自動的には出てこない。

### シナリオ差し替え規則

**アンカーとなる trigger 文がソースから消えた場合のみ差し替えを許す。** それ以外の恣意的な入れ替えは before / after を無効化する。

差し替える場合は本ファイルを同一 PR で更新し、旧アンカーと新アンカーの双方を記載して、どのソース変更で消えたかを明示する。

---

## シナリオ集合（12本、固定）

| ID | 適用瞬間 | 起点 `file:line` | ツール | 文脈内 |
|---|---|---|---:|---:|
| S1 | self-evolution PR が CI green → 次に何を走らせるか | `rules/evolution/initiator-autonomy.md:60` | 3 | 0 |
| S2 | subagent 完了 → 親の次の行動 | `adapter/claude/CLAUDE.md:75` | 1 | 0 |
| S3 | webhook イベント到着 → 処理と `mark_processed` | `adapter/claude/CLAUDE.md:200` | 2 | 0 |
| S4 | sub-issue が親の本文範囲を超える | `rules/task/task.md:38` | 1 | 0 |
| S5 | L1 evaluator の判定基準そのもの | `rules/evolution/initiator-autonomy.md:69` | 1 | 0 |
| S6 | patch / minor / major の分類 | `rules/operations/release-version-rule.md:25` | 0 | 0 |
| S7 | Li+update 実行要否の判定 | `adapter/claude/CLAUDE.md:22` | 0 | 0 |
| S8 | memory 書き込み直前の persistence 判定 | `adapter/claude/CLAUDE.md:161` | 1 | 1 |
| S9 | 判断が settle した → Decision Structure entry を書く | `adapter/claude/CLAUDE.md:172` | 2 | 1 |
| S10 | drift / pattern を観測 → 昇格の閾値判定 | `rules/evolution/promotion-judgment.md:26` | 0 | 0 |
| S11 | merge 完了直後 → L1 変更の短窓観察 | `rules/operations/operations.md:120` | 1 | 1 |
| S12 | session 開始 → cold-start synthesis | `rules/evolution/cold-start-synthesis.md:11` | 2 | 1 |
| | **合計** | | **14** | **4** |

S1 / S3 / S4 / S5 / S6 / S7 のツール跳躍は #1564 実測2 の表と一致する（同一タグで再検証済）。S8-S12 は同じタグ・同じ計数規則で本 instrument 固定時に測った。

S2 のみ #1564 実測2 の記録（ツール2 / 文脈内2）と一致しない。同記録は計数規則（:14）に反する連想的参照を含む過大計上であり、本 instrument 側をツール1 / 文脈内0 に訂正した（PR #1592 のブレーキ1 で検出）。訂正は計数の誤りの是正であって、ソース側の変化ではない — 同じ数値が baseline tag でも現在でも成り立つ。S3 も同じ理由で文脈内跳躍を1つ落としたが、ツール跳躍は2のまま変わらない。

### 各シナリオの経路

各行は `起点 → 遷移先` の順。`[tool]` / `[ctx]` は分類。

**S1** — anchor: `the brakes run after CI green and before the merge gate`
- → `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition `[tool]`
- → `skills/task-subagent-delegation/SKILL.md` Rules `[tool]`
- → `skills/evolution-parallel-agent-eval/SKILL.md` Procedure `[tool]`

**S2** — anchor: `Main agent after subagent completion:`
- → `skills/task-subagent-delegation/SKILL.md`（CHANGES_REQUESTED の再委譲。同一ファイル内 `adapter/claude/CLAUDE.md:126` の明示ポインタ経由であり、節移動は跳躍に数えない）`[tool]`
- 非計数1 — 自己レビュー〜merge へ続く鎖（`rules/evolution/initiator-autonomy.md` Two-stage brake → `skills/evolution-parallel-agent-eval/SKILL.md`）: S1 が計測するため二重計上を避ける。加えてアンカー行（`:75-78`）にこの鎖を名指す明示ポインタがない — `initiator-autonomy.md` への参照は `adapter/claude/CLAUDE.md:190` / `:194` / `:196`、すなわち `Evolution_Initiator_Autonomy` ブロック内にのみ存在する。境界規則と計数規則（:14）の双方から除外。
- 非計数2 — `rules/operations/release-version-rule.md`（release の version type 確認）: `grep -c release-version-rule adapter/claude/CLAUDE.md` = 0。アンカーからの明示ポインタが存在しない連想的参照であり、計数規則（:14）により除外。
- 追記（#1808）—— baseline 以降、非計数1 が名指す節 `Two-stage brake` は `Merge brake` へ改名された。上の節名は baseline タグ時点の literal なので書き換えない。

**S3** — anchor: `Webhook intake policy and procedures:`
- → `skills/operations-foreground-webhook-intake/SKILL.md` `[tool]`
- → `adapter/claude/hooks-settings.md` `[tool]`
- 非計数 — `rules/operations/operations.md`（`mark_processed` の義務）: 鎖のどこにも明示ポインタがない。`grep -n "operations\.md"` は `skills/operations-foreground-webhook-intake/SKILL.md` / `adapter/claude/hooks-settings.md` とも0件、アンカー（`:200`）が名指すのは skill のみ。計数規則（:14）により除外。なお `mark_processed` の実務リテラル自体は baseline 時点の skill 本体（`:68`）に到達済みで、この参照は追加跳躍を要さない。
- 追記（#1762）—— baseline 以降、この鎖の到達先は `rules/operations/main-agent-procedures.md` の `## Foreground webhook notification intake` へ移り、skill 側はリダイレクトスタブになった。上の跳躍数は baseline タグ時点の実測なので書き換えない。

**S4** — anchor: `Sub-issue work exceeding parent body literal ... requires dialogue confirm`
- → `skills/operations-on-sub-issue/SKILL.md` scope-exceed dialogue confirm `[tool]`
- 追記（#1764）—— baseline 以降、この鎖の到達先は `rules/operations/main-agent-procedures.md` の `## Sub-issue rules` へ移り、skill 側はポインタになった。上の跳躍数は baseline タグ時点の実測なので書き換えない。

**S5** — anchor: `brake 2 (L1 only)`
- → `adapter/claude/agents/l1-gate-eval.md` `[tool]`
- 追記（#1808）—— baseline 以降、brake 2 は廃止され、アンカーも到達先も存在しない。上の跳躍数は baseline タグ時点の実測なので書き換えない。

**S6** — anchor: `Application-moment trigger:`
- 判定基準は同一ファイル内に完結。跳躍ゼロ。
- 同行が指す `skills/model-trigger-check-gate-actions/SKILL.md` は「読む癖」側の補助であり、分類リテラルへの到達に load-bearing ではないため計数しない。

**S7** — anchor: `Inspect the LI_PLUS_UPDATE_STATUS= marker`
- 判定リテラルが entrypoint 自身に完結。跳躍ゼロ。

**S8** — anchor: `Before each memory write, apply skills/evolution-persistence-tiering write-time trigger.`
- → `skills/evolution-persistence-tiering/SKILL.md` `[tool]`
- → `rules/evolution/memory-entry-format.md`（entry 形式・維持規律）`[ctx]`

**S9** — anchor: `When the trigger fires, invoke skills/evolution-decision-structure-write and write immediately`
- → `skills/evolution-decision-structure-write/SKILL.md` `[tool]`
- → `docs/Decision-Structure.md`（index 更新 = Procedure step 6）`[tool]`
- → `rules/evolution/memory-entry-format.md` `[ctx]`

**S10** — anchor: `A drift / pattern observation occurring at any moment`
- 閾値表（同一ファイル `:70-75`）まで同一ファイル内。跳躍ゼロ。

**S11** — anchor: `Invocation anchor: this procedure is named at the merge moment by rules/operations/main-agent-procedures.md Merge Execution`
- → `rules/operations/main-agent-procedures.md` `## Merge Execution` `[ctx]`
- → `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format（miss verdict の escalation 先）`[ctx]`

`[tool]` から `[ctx]` へ変わっているのは #1708 の移設による。旧アンカーは `skills/operations-on-merge/SKILL.md` の invoke を指していたが、この手続きの実行主体は `auto` / `semi_auto` では親であり、親は operations 系 skill を読まない。跳躍先が実行主体にとって開けない `[tool]` だったものが、常駐で保持される `[ctx]` になった。

**S12** — anchor: `Trigger = session start, after Li+config.md execution completes.`
- → `docs/Decision-Structure.md`（Action step 1）`[tool]`
- → `adapter/claude/hooks/on-session-start.sh`（Hook coordination）`[tool]`
- → `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format `[ctx]`

`Hook coordination` 段落は #1765 で同一ファイル内の H2 `## Hook Emission Contract`（冒頭に「読むのは on demand、step 3 の適用瞬間には適用しない」と明示）へ移した。跳躍数は据え置き — 同一ファイル内の節移動は跳躍ではなく（計数規則 :15）、ポインタは同じファイルから解決するため。

据え置きを選んだ判断は記録しておく（再計測手順 :31）。適用瞬間に要るのは anchor 内の Operational criterion だけで、そこが引く emit 状態（full / diff-only / marker）は「状態によらず silent」と言うためのものであり、marker 自体は emit 済みコンテキストに直接見える。この読みではツール跳躍は 1 に落ちる。それでも表を動かさないのは、表の数値が baseline tag 時点の実測だからで、後続 PR が読み替えで数値を動かすと before / after の比較面そのものが失われる。S2 / S3 の訂正は計数規則違反の是正であり、適用ステータスの読み替えとは別軸。

---

## 経路ゼロ検査

跳躍数が多いことより悪い状態＝**たどれる線がない**。該当ファイルに触れる変更のたびに以下を再実行し、いずれも非空であることを確認する。

```
grep -nE "promotion-judgment|promotion_tally|noise.floor" skills/evolution-self-eval/SKILL.md
grep -nE "self-eval|self-evaluation" rules/evolution/promotion-judgment.md
```

自己評価の記録中に根本原因の反復に気づいた瞬間から、noise floor ゲート（`rules/evolution/promotion-judgment.md`）への経路が両方向でたどれることを保証する。1本目は #1587 で新設された経路、2本目は既存の trigger 列挙（同 issue で参照を明示化）。

---

## 適用範囲外

- 「劣化がないこと」の証明はしない。本 instrument が測るのは跳躍数のみ。品質面の検証はブレーキ1（`skills/evolution-parallel-agent-eval`）が各 PR に対して別軸で掛かる。
- バイト削減量は測らない。#1564 実測1 のとおり削り代は約 32 KB であり、バイトは主軸ではない。
- 実行時のトークン消費・レイテンシは測らない。静的到達性のみ。
