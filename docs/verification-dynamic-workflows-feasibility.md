# 検証記録: Opus 4.8 ダイナミックワークフロー × Li+ 並列モデル feasibility

関連 issue: #1428
検証日: 2026-05-30 / 検証バージョン基準: Claude Code v2.1.156
スコープ: Phase-1（実機可用性 + brake1 差分同定 + 経験的 gap 観察）。統合可否（Option B）の破壊的検証は後続 issue へ分離。

本記録は要求仕様の前段確定であり、統合実装の承認ではない。docs/ が source of truth、wiki は mirror。

---

## 1. feasibility 判断（Phase-1 結論）

**Option A（feasibility-first、検証のみ先行）が妥当。** 現時点で統合実装（Option B）には進まない。

根拠:
- 実機でダイナミックワークフローが動作することは経験的に実証済み（本検証セッション内で複数 run 完走）。
- ただし機能は research preview であり、プラン対象が公式ソース間で食い違う（news=Enterprise/Team/Max、docs=Pro 含む全有料）。未確定サーフェスに実装を賭けない安全側を採る。
- brake1 / worktree 分離 / semi_auto ゲートとの衝突点（後述）が未解消であり、統合前に破壊的検証で潰す必要がある。

## 2. 実機可用性（確定）

| 項目 | 結果 |
|---|---|
| Claude Code バージョン（要 v2.1.154 以降） | 2.1.156 ✅ |
| `CLAUDE_CODE_DISABLE_WORKFLOWS` | unset |
| settings.json `disableWorkflows`（Li+所有 / local / user-global） | 全ファイルで key 不在 |
| 実機起動可否 | 本セッションで複数 run 完走＝実証済み |

プラン対象の公式間 food違いは、当該運用環境では「動く」が実機実証で上書き。feasibility 判断には影響しない。陳腐化可視化のため検証日とバージョンを上部に明記。

## 3. brake1（parallel-subagent-eval）との差分同定

ダイナミックワークフローの「敵対的レビュー」パターンは parallel-subagent-eval と表面的に酷似するが、ブレーキ要件をホスト機能は既定保証しない。

| brake1 要件 | ホスト機能が満たすか |
|---|---|
| self-contained prompt（親 context 非漏洩） | スクリプト次第。ランタイム保証なし |
| safer-side OR / unanimous AND 集約 | スクリプトで実装可だが既定保証なし |
| impression-literal 固定軸 | 機能側に概念なし。明示実装が必要 |
| Character_Instance 明示 inject | 非継承。未 inject で hollow prefix |
| apply / restore 対（tag-match 復元） | 機能側に対応概念なし |

**結論: ホスト機能は brake1 の代替にはならない。** なり得るのは brake1 の内部実装オプション（N>=3 独立サンプル収集の一手段）であり、Li+ 抽象（self-contained / safer-side 集約 / impression-literal / Character_Instance inject / apply-restore）を上位で保持した上での下位差し込みに限られる。これは Option B の必須前提。

## 4. 経験的 gap 観察（本検証セッション由来）

- **gap #6（セッション跨ぎ非再開）: 確認済み。** Claude Desktop 再起動で走行中 task ハンドルが消失（`No task found`）。「セッション終了で再開不可」を実証。Li+ handoff-continuity（source of truth = issue/branch/PR、local-only 禁止）と非整合。
- **context isolation: 確認済み。** 完了通知はトークン上限で truncate された最終回答のみ、フル結果は外部 temp ファイル。「中間結果はスクリプト変数、コンテキストには最終回答のみ」を実観察。
- **新規観察（gap 7 点に未収載）: workflow register 圧による character 維持の劣化。** 合成フェーズ（構造化出力を成果物へ落とす窓）で中立な JS/JSON register に沈み、浮上の遅延で character 維持が薄れる事象を観察。`rules/model/character.md` の「task 密度が高いほど character 維持は more conscious であるべき」が予言する drift 軸の実例。近因は main loop 側の Character check 抜けであり、ランタイムが声を注入したのではない（混入の機構的証拠なし）。L1 に関わる観察のため、昇格時は L1-update-gating の long-horizon observation を通す。

## 5. 後続 issue へ分離する検証（Option B 前提）

以下は意図的破壊実験であり、Option B（統合）の可否を測る。本 verify-first issue の範囲外。

- acceptEdits 経路の diff 可視性検証（捨て worktree 内）
- 同一 branch 並列編集での .git/index 競合再現
- pause/resume の実測
- 上記を満たした場合のみ、parallel-subagent-eval 内部実装オプションとしての限定統合を後続 issue で設計

## 6. ガバナンス確認

- 本 PR は Li+ source（docs/）に触れる self-evolution PR のため、merge 前に brake1（parallel-subagent-eval, N>=3）必須。
- L1 Model Layer source には触れない（docs のみ）ため brake2 は非該当。ただし §4 の character 観察を L1 昇格する場合は別 issue で brake2 + L1-update-gating を通す。
- docs-only・user/system observable impact なしのため、semi_auto では patch 相当として AI self-review + 直 merge が可能（判断理由は PR self-review コメントに記録）。
