# Li+ Wiki

この Wiki は、**Li+ に基づく開発・運用を支えるための情報整理空間**です。

## ページ構成について

### 要求仕様書（数字：1–9）

数字で始まるページは、
**Li+プログラムの各レイヤーの仕様を定義するページ**です。

- 要求（何を満たすか）と仕様（どう振る舞うか）を一体として記述する
- 実装前に作成または更新する
- issue群から採用された要件を集約する

これらのページは **安定性と一貫性を重視**して管理されます。

---

### 参考文書（アルファベット：A–）

アルファベットで始まるページは、
**Li+の構想・設定・導入手順などの参照用ページ**です。

- 設計思想・背景
- 設定リファレンス・インストール手順

これらのページは **必要に応じて更新・拡張されます**。

---

### `rules/`, `skills/`, adapter/bootstrap 各ファイル

リポジトリ内の `rules/**/*.md`（L1–L4 の常時ロード分、subdir 含む）、`skills/**/SKILL.md`（トリガー起動分）、`adapter/claude/Li+agent.md`、`adapter/claude/Li+hooks.md`、`adapter/codex/Li+agent.md`、およびルート直下の `Li+config.md`、`Li+bootstrap.md` は、
**AIやランタイムが直接読む実行用プログラム / 定義ファイル**です。

- `docs/` は人間向けの仕様書・要求仕様・手順書
- `rules/`, `skills/` および adapter/bootstrap は実行時に読み込まれる本体

両者は対応しているが、役割は同じではない。

---

[Home](Home) | [1. Model](1.-Model) | [2. Evolution](2.-Evolution) | [3. Task](3.-Task) | [4. Operations](4.-Operations) | [A. Concept](A.-Concept)
