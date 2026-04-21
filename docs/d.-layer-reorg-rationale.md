# L1-L6 レイヤー再編の意図と L5/L6 に rules/ サブディレクトリが無い理由

## 背景

2026 年初頭以降、Li+ プログラムはレイヤー構造を 3 層（core / task / operations）から 6 層（L1 Model / L2 Evolution / L3 Task / L4 Operations / L5 Notifications / L6 Adapter）へ再編した。あわせて判断記録レイヤー（`docs/a.-`, `b.-`, `c.-`）を外部記憶の一形式として追加した。

並行して `rules/**/*.md` の配置は layer 名の subdir（`rules/model/`, `rules/evolution/`, `rules/task/`, `rules/operations/`）に整理されたが、L5 Notifications と L6 Adapter には `rules/notifications/` や `rules/adapter/` が存在しない。

この不在は、ファイルの書き忘れではなく設計意図である。以下に記録する。

---

## なぜ L1-L6 に再編したのか

旧 3 層構造では「判断基準（model）」「issue 運用（task）」「Git / GitHub 運用（operations）」の 3 本立てが実体だったが、以下の責務が挟まる形で肥大化していた：

1. **自己更新ループ（observation → distill → L1 Update Gating）** — 従来は model 内部に混在していたが、runtime invariant（loop safety / accepted tradeoff 等）とは責務が異なる。独立した L2 Evolution Layer に分離した。
2. **通知意味論（inspect / claim / ack / consume / mention / cleanup）** — 旧 operations に webhook 取り込みとして部分的に存在していたが、transport（polling / push）を跨いで共通化すべき上位意味論として L5 Notifications Layer を切り出した。
3. **ホスト注入ロジック（CLAUDE.md / AGENTS.md / hooks）** — 旧 operations に Claude Code 固有の hook 記述が混入していた。これはランタイム固有の注入層であり、共有 Li+ プログラムの責務ではない。L6 Adapter Layer に分離した。

Lilayer Model はこの 6 層を「異なる surface を持つ同一プログラム」として読む。L1-L6 の番号は attachment 順序であって precedence ではない。各レイヤーは自身の責務範囲で outward behavior を安定化させる。

判断記録レイヤー（`docs/a.-` 以降、小文字接頭辞）は、これら構造変更を含む「過去の判断と根拠」を外部記憶として蓄積する第三の docs/ 用途として追加した。1-5 の要求仕様書、A-D のユーザー向けドキュメントとは独立した用途を持つ。

---

## なぜ L5 Notifications に `rules/notifications/` が無いのか

**現状：** L5 Notifications Layer の実体は `docs/5.-Notifications.md` の意味論と、github-webhook-mcp（別リポジトリ）での webhook 配信実装が担っている。`rules/notifications/` は作成されていない。

**理由：** 将来拡張のための予約席である。

現時点では通知の transport は webhook-MCP が一手に引き受けており、realtime trigger（push 受信時に特定 rule を強制再読込する等の挙動）は未実装である。rules/ に搭載するかどうかは、realtime trigger の実装方式が確定した時点で判断する。

- 意味論（inspect / claim / ack / consume / mention / cleanup の分離、前景一致のみ mention する規律）は docs/5.-Notifications.md に既に定義済み
- transport レイヤーの実装は別リポジトリ（webhook-MCP）側にある
- rules/ は「常時コンテキストに置くべき判断基準」の格納先である。現在の通知意味論は event-driven であり、常時ロードの必要がない

したがって `rules/notifications/` の不在は「搭載しないと決めた」のではなく「搭載判断を保留している」状態である。realtime trigger 実装時に再検討する。

---

## なぜ L6 Adapter に `rules/adapter/` が無いのか

**現状：** L6 Adapter Layer の実体は `adapter/claude/CLAUDE.md` + `adapter/codex/AGENTS.md` + `adapter/claude/hooks/*.sh` + `adapter/claude/hooks-settings.md` である。rules/ ではなくテンプレートと hook スクリプトで構成される。

**理由：** アダプターの本質はテンプレート駆動 + hook 駆動であって、rule 駆動ではない。

rules/ は「AI が判断時に参照する共有仕様」の格納先である。一方アダプターの責務は：

1. ホスト指示ファイル（CLAUDE.md / AGENTS.md）への Li+ 注入
2. ホストランタイム（Claude Code / codex）固有のトリガー実装を hook 経由で配線
3. workspace 言語契約や Character Instance 配線などの起動時セットアップ

これらは「AI が読む仕様」ではなく「AI 実行環境を Li+ 対応に整形する装置」である。したがって rules/ の subdir としては現れず、`adapter/` ディレクトリ直下にテンプレートと hook として存在する。

**暫定事項：** Cowork（別ホスト実装）は現時点で hooks をサポートしていない。このためアダプターレイヤーは、本来であれば hook として配線すべき責務（webhook ポーリングの前景リマインダー等）の一部を、テンプレート側の常時指示として抱え込んでいる。cowork 側の hooks サポートが整った段階で、これらの責務はアダプターから hook へ移譲される予定である。

したがって現在のアダプターの膨らみは過渡的なものであり、ホスト側実装の進展に合わせて圧縮される。

---

## 関連

- 判断記録レイヤー運用仕様：`a.-Decision-Log.md`
- レイヤー定義：`rules/model/layer-definition.md`, `rules/model/axis-separation.md`
- L5 意味論：`docs/5.-Notifications.md`
- L6 構成：`docs/6.-Adapter.md`, `docs/C.-Bootstrap.md`
- parent 監査 issue：[Liplus-Project/liplus-language#1125](https://github.com/Liplus-Project/Liplus-language/issues/1125)
- 記録化 issue：[Liplus-Project/liplus-language#1130](https://github.com/Liplus-Project/Liplus-language/issues/1130)

---

## メンテナンス

この判断記録は、以下の場合に削除する：

- L5 Notifications Layer の realtime trigger 実装方式が確定し、rules/ 搭載の是非が決着した時（決着内容が `docs/5.-Notifications.md` か別の decision log に吸収された段階）
- Cowork の hooks サポートが成熟し、L6 Adapter Layer が hook ベースへ完全移行して「アダプターが hook 責務を抱える」暫定状態が解消された時
- L1-L6 構造自体が次の再編で書き換えられ、本記録の前提が無効になった時
