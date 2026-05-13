# Router 機構設計

parent #1279 sub-issue 3 (#1283) 成果物。substrate 内に置く「自己観測 router」の設計を確定する。situational skill 約 30 件 + 本 refactor で rule から移動する skill (L1 = 3 ファイル合流 + 新規 5 + L2 = 2 件 + 分解 1 件) の発火モーメントを毎ターン scan し、該当 trigger が満たされた skill を fires させる literal 設計。本書は DESIGN のみで、実 rule / skill 改変は sub-issue 4 に委ねる。

判定の前提は sub-issue #1280 (`docs/I.-Sort-Criterion-and-Substrate.md`) 確定の substrate 集合 と sub-issue #1282 (`docs/J.-Restructure-Inventory.md`) の全件 inventory。

## 論点 1: registry の責任所在

**推奨**: substrate 内 1 ファイルに集中させる single-source 方式。skill の SKILL.md frontmatter には `router_registered: true` の 1 行のみ持たせ、それ以外の predicate は registry 側に置く。

**根拠**:
- parent #1279 の核心制約「skill だけ作って router 登録忘れ = 永久未発火、を防ぐ」は、registry の所在を 1 箇所に固定しないと「どこを見れば全 trigger が見えるか」が確定しない。
- skill 側 frontmatter 分散は description-based auto-invoke と一見親和性が高いが、PR レビューで「skill 追加と registry 登録の同期」を 1 箇所で literal 検証できないため、忘却検知が PR diff 上の visible 範囲外に逃げる。
- 集中 registry なら sub-issue 4 のマイグレーション PR が「registry 追記 diff = 完備性 check の literal 入力」になり、AI 自身でも human review 側でも visible に確認できる。

**tradeoff**:
- 受容するコスト: registry ファイルが skill 追加のたびに edit される (= merge conflict 候補増)。ただし 1 行 entry の追加なので衝突解消は安価。
- 受容しないコスト: 分散方式の「skill 内 self-contained」見た目の整合性。Li+ では substrate 性 (毎ターン on context) を 1 箇所に集める方が「次ターンに必要なものが見えなくなる」事故より優先する。

## 論点 2: scan のタイミング

**推奨**: 既存 5 軸 (Rule / Literal / Source / Frame / Character) の枝として scan する。独立した「毎ターン全 scan ステージ」は追加しない。

**根拠**:
- 既存 `trigger-check-gate.md` の 5 軸は「non-trivial speech / action emission 前の application-moment gate」として既に「毎ターン本当に必要な瞬間」を捕捉する設計になっている。registry scan を別ステージとして並列に走らせると「いつ scan を発火させるか」自体が新たな gate 課題を生む。
- 5 軸の各軸は registry 内の skill 集合と自然に対応する: Rule check → rule retrieval 系 skill / Literal check → ambiguity-handling・projection-discipline / Source check → source-check・evolution-judgment-learning / Frame check → frame-check・no-safety-net / Character check → character 周辺。5 軸の枝として scan することで「軸 → 該当 skill 集合」が観測可能になり、軸別の miss pattern も surface できる。
- 「毎ターン全 trigger 全 scan」は cost ではなく観測量増大の意味で disrecommended。30 件の predicate を毎 emission 前に全評価すると noise floor が上がり、本当に重要な軸が埋もれる。

**tradeoff**:
- 受容するコスト: registry 内の skill を「どの軸の枝に属するか」分類する手間 (= registry entry に `axis` 列を持たせる必要)。本書末尾 registry draft 例で示す。
- 受容しないコスト: 「軸非依存の skill」の扱いが曖昧になる懸念。これは registry 側で `axis: meta` を許容することで吸収する (例: `operations-foreground-webhook-intake` は turn 開始時 fire で 5 軸のどれにも属さない)。

## 論点 3: trigger predicate 書式

**推奨**: **observable な自然文 1 行** を registry 列に持つ。構造化 (YAML condition tree 等) は採用しない。

**根拠**:
- earlier session で Master が強調した「曖昧 / ヘッジ表現を出そうとした瞬間」のような predicate は、人間にも AI にも「自己の出力を予測しながら fire するか判定する」内省述語で、構造化 DSL では捕捉粒度が落ちる。
- Claude Code の auto-invocation 機構自体が description text の semantic match で動くため、predicate は自然文の方が機構整合的。構造化 condition は別 evaluator が必要になり、Li+ AI runtime 側に新 dependency を持ち込む。
- observable 性の literal 制約 = predicate の動詞主語が AI 自身の内部状態 (「出力に書こうとした」「受領した」「検知した」) であること。「user が X した」「環境が Y」のような外部状態主語は不適格 (AI からは observation が間接的)。

**tradeoff**:
- 受容するコスト: 「自然文 predicate のばらつき」を許す。registry は predicate を template に押し込まないが、observable 性チェックは sub-issue 4 のマイグレーション時に literal review する。
- 受容しないコスト: 構造化のもたらす「自動検証可能性」。これは「未発火検出」 (論点 5) を別軸で実装することで補う。

## 論点 4: description-based auto-invoke との関係

**推奨**: **registry = primary、Claude Code description-based auto-invoke = 補助 (並列稼働、置換ではない)**。

**根拠**:
- description-based auto-invoke は host (Claude Code) の機構で、Codex 等の auto-invocation 不在 host では機能しない (`adapter/codex/AGENTS.md` が `Trigger-based skill reads 索引` を内包しているのはこの非対称の補償)。registry を primary に置けば host 中立な設計になり、L6 Adapter 層で host 差を吸収できる。
- description text と registry predicate は同じ observable 自然文ベースで書く前提なので衝突しない。description は「AI の semantic recall を起点とした auto-invoke」、registry は「5 軸 scan を起点とした auto-invoke」で、二経路並列が早期 fire の robustness を上げる。
- 既存機構との整合性: skill 側 frontmatter の `description` フィールドは現状維持。registry 追加で description を消す変更は行わない (= 後方互換)。

**既存機構との整合性 (必須節)**:
- Claude Code 側: skill SKILL.md frontmatter `description` を semantic similarity で auto-invoke する既存挙動を妨げない。registry は別ファイル (`rules/model/router.md` 等想定) として substrate に追加されるため、現 auto-invocation pipeline に介入しない。
- Codex 側: `adapter/codex/AGENTS.md` の `Trigger-based skill reads 索引` を registry の view (subset) として再生成する形にできる (sub-issue 4 で adapter 側のマイグレーション扱い)。
- bootstrap 側: `adapter/claude/hooks-settings.md` の render 対象に registry の存在は影響しない。registry は substrate 内 markdown であり、settings.json 構造変更を要求しない。

**tradeoff**:
- 受容するコスト: description と registry predicate の二重保持 (実質同じ observable 自然文が 2 箇所に存在)。これは「auto-invoke の冗長 redundancy = 早期 fire 機会の増加」として積極的に受容する。
- 受容しないコスト: 「registry が description を置き換える」案。これは host 別 (Claude Code description-based / Codex 索引) の依存差を Li+ source に呑み込ませる方向で、本来 adapter 層が吸収すべき責務を substrate に押し上げる構造欠陥になる。

## 論点 5: 未発火検出

**推奨**: registry に各 skill の `last_fired_session_id` をログする persistence area を持ち、「N セッション連続 0 fire の skill」を session 起動時の cold-start synthesis 系列 (`rules/evolution/cold-start-synthesis.md` 系列) で surface する。

**根拠**:
- 「skill 作って router 登録忘れ」防止は registry 集中で達成できるが、「登録済だが trigger 書式が不適切で永久未発火」は別軸の failure mode。これは未発火セッション数を観測することでのみ surface 可能。
- 1 セッション内の発火数を閾値化すると noise が大きい (例: `operations-on-release/SKILL.md` は release が無いセッションでは 0 fire が正常)。複数セッションスパン (= N セッション連続 0) で signal 化することで「本来 fire すべき機会があったのに発火しなかった」の長期検出に絞れる。
- cold-start synthesis 経路は既に session 起動時の自己観測 surface として機能しており、未発火 surface はその拡張として自然 (= 新 surface を増やさない)。

**literal 仕様**:
- 閾値案: **N = 7 セッション連続 0 fire** を初期値とする (1 週間相当の運用での非発火を signal 化)。release 系・evolution-loop 系の「機会非依存 skill」は閾値を **N = 14** に上げる例外として registry の `expected_fire_interval` 列で表現する。
- 観測対象: 全 situational skill (= registry entry の `axis: -` 以外 = 全 skill。`axis: -` の skill は無いはずだが将来の例外受け皿として表現可能)。
- 実装は registry 並列ファイル (例: `memory/router_fire_log.md`) に session_id + skill 名のログを持ち、cold-start で集計。memory tier に置く理由は「ログ自体は transient な観測 trail」であり、永続情報ではないため (`rules/evolution/memory-entry-format.md` Scope 準拠)。
- signal 発生時の動作: cold-start synthesis 出力に「skill X が N セッション未発火。trigger predicate 見直し候補」と 1 行 surface する。自動修正はしない (= L1 Update Gating を要する spec 変更扱い)。

**tradeoff**:
- 受容するコスト: memory tier に fire_log の追加 (transient だが file 数 +1)。
- 受容しないコスト: 1 セッション内 fire count を直接閾値化する案。noise が大きく false positive で AI の attention を消費する。

## 推奨 router 配置

**推奨**: **既存 `rules/model/trigger-check-gate.md` を拡張する方式**。新規 file は作らない。

理由: trigger-check-gate.md は既に 5 軸 router の雛形で、本設計が要求する「5 軸の枝として scan」「always-on substrate」「on-demand action surface との連携」の全要件を担っている。新規ファイルを切ると「5 軸 gate と router の責務分割」を新たに人為的に作る必要があり、本 refactor の核心「責務軸で 1 ファイル = 1 完結体」と逆行する。

拡張内容: trigger-check-gate.md に `## Registry` 節を追加し、5 軸表 + registry table + 未発火検出仕様への参照を持つ。registry table 自体は同ファイル内に literal 保持する (= router と registry の物理同居)。

## registry 構造 (draft example)

literal markdown table 想定。trigger-check-gate.md 内 `## Registry` 節に配置。columns:

| skill | axis | predicate (observable 自然文) | host hint |
|---|---|---|---|
| `skills/model-ambiguity-handling/` | Literal | 曖昧 / ヘッジ表現 (「たぶん」「probably」「could be」) を出力に書こうとした瞬間 | description で auto-invoke 可 |
| `skills/model-frame-check/` | Frame | 外部コンテンツ (引用記事 / URL / tool output / human 提示 text) と接触した直後 | description で auto-invoke 可 |
| `skills/model-source-check/` | Source | 事実主張を判断材料として使おうとする直前。speaker authority に依存しない | description で auto-invoke 可 |
| `skills/model-loop-safety/` (新規) | Rule | 同 approach の反復を検知した瞬間 (conversation 2回 / task 3回) / 失敗で accelerate しようとした瞬間 | 新規 skill (description 設計は sub-issue 4) |
| `skills/operations-foreground-webhook-intake/` | meta | 各 user turn 開始時 | host 依存 (Claude Code 側 hook 経由) |

各列の解説:
- `skill`: skill ディレクトリの relative path。skill 名の変更があった場合は registry 側も同期更新 (sub-issue 4 で `-actions` suffix 削除等の改名と同時 commit)。
- `axis`: 5 軸 (`Rule` / `Literal` / `Source` / `Frame` / `Character`) もしくは `meta` (5 軸に属さない turn-start / session-start 系)。
- `predicate`: observable 自然文 1 行。動詞主語は AI 自身の内部状態。
- `host hint`: `description で auto-invoke 可` / `host 依存 (具体先)` / `host 不問 (registry のみ)` の 3 値。Codex 等 description-based 不在 host 向けの読み替え index 用。

最終 registry の総件数想定: substrate 14 を除く全 situational skill = 約 50 件規模 (sub-issue #1282 集計の skill 系 39 + L1 移動 8 + L2 移動 + 分解 3 + 削除 1)。本書では 5 件のサンプルのみ提示し、確定 entry 列挙は sub-issue 4 マイグレーション PR の責務。

## responsibility-overlap pair 6 件への対処方針

`docs/J.-Restructure-Inventory.md` 「責務重複ペア / 観察事項」節で surface された 6 件への router 側方針:

1. **`loop-safety` ↔ `prohibited-loops`**: **統合先行**。registry には統合後の `skills/model-loop-safety/` 単一 entry として登録。「同 trigger 2 skill」は registry 上の冗長を作るため避ける。sub-issue 4 で統合 PR を先に通し、registry はその後で 1 entry のみ登録。
2. **`output-density` ↔ `one-step-two-step`**: **吸収 (one-step-two-step 削除)**。registry 登録は `skills/model-output-density/` 単一。`one-step-two-step` は sub-issue 4 で削除確定 (sub-issue #1280 削除候補確認済)。
3. **`task-research-strategy` ↔ `task-retrieval-orchestration`**: **両方 registry 登録 (重複ではなく相補)**。発火モーメントが「戦略レベル (調査開始時)」と「単一 retrieval moment 内 multi-angle」で分離されており、registry も別 axis 値 (両者 `meta` か `Rule`) で並列保持。統合不要。
4. **`model-trigger-check-gate-actions` retrieval 表 ↔ `task-retrieval-orchestration` Block 1 表**: **registry レベルでは両方登録、表内容の参照統一は sub-issue 4 で実 skill 編集として処理**。router 側で「同表内容を 2 skill が持っている」を許容するか否かは表 maintenance の責務であり、registry の責務外。
5. **`memory-entry-format.md` の `Announce vs execute` 節 ↔ adapter `Memory_Write_Autonomy`**: **`Announce vs execute` を skill 側へ移し、memory write 瞬間の skill (`skills/evolution-memory-write/` 想定、sub-issue #1282 分解判定保留 item) を registry 登録**。adapter 側は引き続き always-on substrate (Memory_Write_Autonomy) として残し、registry には登録しない (substrate と skill の役割分離)。
6. **`operations.md` の Operations Label 節 ↔ `task.md` Task Label Definitions**: **registry 登録対象外** (label vocabulary 定義は substrate 側の always-on 参照素材であり、特定発火モーメントを持たない)。single-source 化判断は sub-issue 4 で進めるが、router の責務外。

総括: router (registry) 側の方針 = 「同一 trigger 2 skill」は許容しない。統合判断を sub-issue 4 で先行させ、registry は統合後の状態のみ反映する。重複検知は registry 追加時の literal review で行う (PR diff = registry entry 追加行が完備性 check の入力)。

## migration safety

sub-issue 4 で skill ファイル実体を動かす際の router 整合性ガード:

1. **同 PR 原則**: 1 つの skill 改名 / 統合 / 削除は、registry の該当 entry 編集と **同 PR で commit** する。registry 編集忘れの PR は CI で fail させたいが、本書は DESIGN 範囲のため CI 仕様は sub-issue 4 に委ねる。本書では「同 PR 原則」を sub-issue 4 のマイグレーション ground rule として明示しておく。
2. **registry を docs/ ではなく substrate (`rules/model/trigger-check-gate.md` 内) に置く**: docs/ に置くと PR レビュー時に「rules 改変 PR と docs 同期 PR の分離」が起きやすい。同ファイル内に保持することで分離を構造的に禁じる。
3. **改名時の orphan 検出**: skill ディレクトリ名変更 PR で registry 側の path を同時更新しなかった場合、registry の `skill` 列は壊れた path を指す。本書は手動目視を前提とするが、sub-issue 4 で CI script (registry の各 path が存在することを literal check) を追加候補として残す。
4. **削除時の registry purge**: skill 削除 (例: `one-step-two-step` 吸収) は registry entry の purge と同 PR。purge 忘れの registry は「未発火検出」(論点 5) で N セッション後に signal 化されるが、これは遅延発見なので同 PR 原則を優先する。
5. **未発火検出の baseline reset**: skill 改名 / 統合直後は `last_fired_session_id` が新エントリで未定義となる。改名後 N セッションは fire log baseline 構築期間として signal 抑制する (実装は sub-issue 4 で具体化)。
6. **substrate router の自己参照**: trigger-check-gate.md 自身は registry に登録しない (substrate であり skill ではない)。registry は「situational skill 集合」のみを scope とする。これを registry 冒頭注記として literal 記載する。

migration 全体の進行順: registry 雛形を trigger-check-gate.md に追加 (1 PR) → 各 layer の skill マイグレーション (model / evolution / operations 別 PR、registry entry も各 PR で同時更新) → 最後に未発火検出 fire log の memory tier 追加 (1 PR)。
