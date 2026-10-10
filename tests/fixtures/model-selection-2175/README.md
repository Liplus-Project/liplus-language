# #2175 比較準備・未完の実測

2026-10-10 の初回最小要求は利用枠エラーで停止した。`probe-result.json` は識別子を除いた結果で、要求モデルは `haiku`、effort は `low`、exit 1、1.922 秒、返却された利用トークンと費用はすべて 0。真のモデル識別子は返らず、Haiku 5.5 が動作したという証拠はない。Opus の要求は行っていない。比較精度・費用差・枠の節約は未測定である。

エラーは monthly spend limit と session limit resets 8:20pm (Asia/Tokyo) の両方を表示した。その文字列を保存しただけで、monthly/5h の制限種別や解除を検証したわけではない。auth、limit、モデル unavailable の場合は追加要求を止める。

`fixtures.json` は抽出、ログ分類、既知文検索を各4件、計12件収める。英語6件、日本語6件。期待値は評価対象モデルへの要求前に固定し、入力と照合したリテラルであり、モデル同士の一致を正解には使わない。`manifest.json` は入力・正解・チェックサム・採点と費用の扱いを保持し、3つの prompt ファイルには正解を含めない。各モデルへ同じ3つの入力を与える。バッチは独立セッションで、各ケースの分母は常に固定する。

`score.py` は厳密な JSON の文字列比較で採点する。一つでも誤答ならバッチ不合格。missing/extra/duplicate key、非文字列、JSON 不正は分母を保持したまま0点。ケースの正解数とバッチ合否は別に記録する。`tests/test_model_selection_2175.py` は12/12、11/12で不合格、不正回答の分母、重複正解ID拒否、バッチの全件被覆をモデル要求なしで確認する。

再開は利用枠が使えることを確認した後、このブランチ上で行う。新たな API 課金の有効化、アカウント変更、利用枠回避は行わない。`runner.py` は明示的な `--execute` がなければ dry run だけを行う。native executable に Python の引数配列を渡すため `--tools ""` の空引数を保持する。safe mode、非永続セッション、スキル・MCP・ツール無効、low のみ。モデルに外部ツールや実際の部屋タスクは与えない。

```powershell
python tests/fixtures/model-selection-2175/runner.py --model haiku --batch 1 --cli C:/Users/smile/AppData/Roaming/npm/node_modules/@anthropic-ai/claude-code/bin/claude.exe --raw-dir D:/Users/hal/Codex_Luna/.benchmark-temp/2175-paired --out D:/Users/hal/Codex_Luna/.benchmark-temp/2175-paired/haiku-1.json
```

実行時は上のコマンドに `--execute` を付ける。`--model haiku/opus` と `--batch 1/2/3` を組み合わせて最大6要求とする。同じ raw-dir を全要求に使い、失敗・訂正も6回に含める。上限・認証・未提供エラーなら残りの要求を行わない。出力先は毎回別ファイルにし、上書きしない。runner は6回を超える起動を拒否し、自動再試行はしない。CLI help に最大出力トークン設定がないためハード上限は設定できない。要求は短い JSON に限定する。

成功時は返却された `model_usage` の真のモデル識別子が目的の Haiku 5.5 / Opus 5.5 に一致することを確認する。別モデルなら比較を止める。全12件が両モデルで揃わない限り paired 比較は未完とする。カテゴリ別・全体の正解数/12、各試行の時間、入力・出力・キャッシュトークン、失敗・訂正を含む費用を集計する。timeout/OSError でも試行を保存し、費用不明を null で残す。不明費用を含む合計では費用優劣を結論しない。`total_cost_usd` は CLI の返却値であり、API 相当推計と実際の subscription 課金・枠消費を混同しない。返却費用が不明の失敗は0費用と仮定せず、不明とする。

raw stdout/stderr はアカウント・セッション情報を含み得るのでコミットしない。raw-dir はリポジトリ外に置く。コミット候補は sanitizer の結果と合成回答だけで、内容を確認してから保存する。

Artificial Analysis の総合指数は今回の狭い課題を証明しない。外部比較とローカル測定を別表に保つ。英語中心の総合指数と本課題の日本語を同一測定とは扱わない。また本課題で12/12でも実際の調査・実装全般を保証しない。

- 過去判断: https://github.com/Liplus-Project/liplus-language/issues/2162
- 比較の要求: https://github.com/Liplus-Project/liplus-language/issues/2175
- AA 対象: https://artificialanalysis.ai/models/claude-haiku-5-5-low 、https://artificialanalysis.ai/models/claude-haiku-5-5 、https://artificialanalysis.ai/models/claude-opus-5-5-low
- AA 方法: https://artificialanalysis.ai/methodology/intelligence-benchmarking
- AA 費用の暫定性・100k超の価格段差: https://artificialanalysis.ai/articles/claude-haiku-5-5

規範的なモデル選択ルールは変更していない。比較が揃うまで issue は forming のまま、外部利用枠待ちの waiting とする。#2177 は解消済みで依存 issue は追加しない。PR、自己レビュー、merge はこの準備段階では行わない。
