# release rule と semi_auto mode の dogfood：2026-04-20 セッション知見

## 背景

2026-04-20、liplus-language 自身で新 release rule (#1087 / #1093) + semi_auto mode (#1088) + merge strategy 緩和 (#1084) + parent auto-close spec (#1085) + tag channel (#1086) を dogfood 形式で整備した。セッション全体で 6 本の spec PR を serial で通し、途中で複数の GitHub 実挙動と Li+ spec の乖離を empirical に確認した。本記録は次セッション以降の AI が同じ blind spot を踏まないためのもの。

## 発見と empirical 検証

### 1. GitHub の Latest 判定は anchor 依存

| 場所 | 誤った前提 | 実態 |
|---|---|---|
| `#1087` spec「default = state なし (prerelease=false, latest=false)」 | `--latest=false` で単独に state なし release を作れる | anchor (make_latest=true 固定 release) が存在しない場合、GitHub は legacy pick で新 release を Latest 化、`--latest=false` は無効化される |

**empirical 検証 (v1.13.0 anchor 固定下、使い捨て test release):**

| gh 呼び出し | make_latest | 結果 |
|---|---|---|
| `--latest=false` | `"false"` | state なし、v1.13.0 anchor 維持 ✅ |
| `--latest` (bare、値なし) | `"true"` | test release が Latest、anchor demote |
| flag 省略 (default) | `"legacy"` | semver+date auto pick で test release が Latest 化 |
| `--prerelease --latest=false` | — | prerelease=true、Latest 不適格 (combo として有効) |

修正: `#1093` で Latest anchor requirement と canonical command (`gh release create {tag} --target main --title {version} --generate-notes --latest=false`) を明文化。初回 dogfood (v1.14.2 release) で anchor 維持が literal に確認された。

### 2. PR author の self review assignment 制約

| 場所 | 誤った前提 | 実態 |
|---|---|---|
| `#1088` PR #1095 の Master review | `gh pr edit --add-reviewer` で PR author 自身を reviewer に指名可能 | GitHub は PR author の self-assignment を silent rejection (API は成功応答だが reviewRequests は空のまま) |

**empirical 検証 (PR #1095):**

| approach | 結果 |
|---|---|
| `gh pr edit 1095 --add-reviewer liplus-lin-lay` | silent failure (`reviewRequests=[]`) |
| `gh pr review 1095 --comment --body "..."` | ✅ `state: COMMENTED` で formal review record 成立 |

修正: `#1088` の [PR Review] に「Self-review formal record (all modes, mandatory)」節を追加。`gh pr review --comment` が PR author 自己レビュー記録の唯一の手段と literal に明記。

### 3. sub-issue 意味論の再定義 (#1085)

| 誤った運用 | 正しい意味論 |
|---|---|
| sub-issue ごとに個別 PR を切る (atomic に独立 merge) | sub-issue は parent の atomic deliverable の decomposition 単位。独立 ship 可なら sibling issue に格上げすべき。`#919` の single parent PR flow が canonical |

当日の github-webhook-mcp v0.11.0 (OAuth device flow 移行) で #198 parent + #199-#202 sub-issue 構造を per-sub-issue PR で実装した結果、最初の PR merge で linked branch 経由の parent auto-close 事故を踏んだ。`#1085` で classification litmus (「独立 ship 可か？」) と single parent PR flow を `[Sub-issue Rules]` に codify。

### 4. AI self-review の全 mode 必須化 (#1088)

| 修正前 | 修正後 |
|---|---|
| trigger mode で PR review は human 任せ、AI self-review は任意扱い | trigger / semi_auto / auto の全 mode で AI self-review を必須化。semi_auto では type (patch/minor/major) 連動で human check を上乗せ |

構造的 unlock の一部として `.github/CODEOWNERS` を撤去、Layer 2 (release state gate = #1087 `latest=human flip`) のみで catastrophic damage を防止する defense-in-depth に移行。

### 5. CODEOWNERS 撤去は unlock の trade-off であって自由追加ではない

| 場所 | 誤った前提 | 実態 |
|---|---|---|
| 初期の `#1085` safeguard 案 (β path-gradient CODEOWNERS) | CODEOWNERS の段階追加で catastrophic damage を構造的に塞げる | CODEOWNERS は semi_auto 採用時に「人間 review 不要の patch auto-merge」を実現するため**撤去せざるを得ない**。maintain vs unlock の trade-off |

Master 判断「複雑さは人間側にも AI 側にも error surface を作る」で (β) 却下、(α) 全撤去 + release gate backstop の 2 層 defense に集約。

## 判断ルール

**spec / 推論 が GitHub / 外部システムの API 挙動を claim する時は、実機で call した literal 結果を empirical 検証する。** `b.-spec-vs-implementation-order.md` の再演：今回も gh CLI flag の挙動、release state の auto 判定、PR review assignment 制約などを推論で断定せず、使い捨て test release / test PR で確認した。

- Spec 記述時、実挙動と乖離した箇所は decision log に empirical 検証結果ごと残す
- 「できるはず」の推論は次 session で容易に忘れる。literal 検証結果を spec 本文 or decision log に固定する
- `(b)` は「外部システム依存箇所」の一般ルール、本記録 `(c)` は「GitHub release/PR 挙動」の具体適用。両者補完関係

## 適用範囲

- 本記録は 2026-04-20 cycle の liplus-language release rule + semi_auto mode dogfood で発見した挙動の snapshot
- GitHub API 挙動は将来変わる可能性があるため、同種の claim を spec に追加する際は再検証する
- USER_REPOSITORY (npm 絡み) への semi_auto 展開時には CD workflow の review state 連動を別途設計要 (本セッション scope 外)

## 関連

- 事例 1 (Latest anchor): [Liplus-Project/liplus-language#1087](https://github.com/Liplus-Project/liplus-language/issues/1087), [#1093](https://github.com/Liplus-Project/liplus-language/issues/1093), PR #1089 / #1094
- 事例 2 (self-review assignment): [Liplus-Project/liplus-language#1088](https://github.com/Liplus-Project/liplus-language/issues/1088), PR #1095
- 事例 3 (sub-issue 意味論): [Liplus-Project/liplus-language#1085](https://github.com/Liplus-Project/liplus-language/issues/1085), PR #1091, 観察元 `Liplus-Project/github-webhook-mcp#198`
- 事例 4 (AI self-review 必須化): [Liplus-Project/liplus-language#1088](https://github.com/Liplus-Project/liplus-language/issues/1088), PR #1095
- 事例 5 (CODEOWNERS 撤去 trade-off): [Liplus-Project/liplus-language#1088](https://github.com/Liplus-Project/liplus-language/issues/1088) (β 却下経緯)
- 関連 decision log: `b.-spec-vs-implementation-order.md` (外部システム依存全般の判断ルール)

## メンテナンス

この判断記録は、以下の場合に削除する：

- GitHub API の Latest 判定 / review assignment / sub-issue linkage 挙動が本記録と根本的に変わり、実態が記述と乖離した時
- spec (`skills/operations-on-release/SKILL.md` [Release state rule] / `skills/operations-on-pr-review/SKILL.md` / `skills/operations-on-sub-issue/SKILL.md`、旧 `operations/Li+github.md` 内 [Release state rule] / [PR Review] / [Sub-issue Rules]) が本記録の全発見を体系的に吸収し、個別参照の必要がなくなった時
- 同種の blind spot が 6 ヶ月以上観測されず、記録の参照が途絶えた時
