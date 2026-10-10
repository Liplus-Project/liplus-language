# #2175 種類別の追加比較

この段階はログ分類を下げる対象に含めない。新しい独立の合成課題を抽出・既知文検索各4問、各種類日本語2問/英語2問で固定する。`prepare.py` はモデルを呼ばず、固定期待値と入力を保存する。期待値・入力・prompt・manifestを先に commit/push し、実行後に変更しない。

通常は各種類1バッチずつ、Haiku 5.5 low / Opus 5.5 low に同一入力を与える計4要求。各種類のHaikuに誤答が出た場合だけ、追加で実際のOpus訂正引き継ぎを1要求ずつ許可し、全体は最大6要求。ログ分類課題の追加、無条件再試行、pairedのOpus回答を後付けの訂正費用に使うことはしない。

共有 runner は `../model-selection-2175/runner.py` と厳密採点器を使う。safe-mode、native executable、非永続セッション、hooks/MCP/skills/toolsを無効化する。真の modelUsage ID と token/cost を確認し、認証/上限/unavailable/timeout/モデル不一致/不足usageでは停止する。rawはリポジトリ外の新しい `D:/Users/hal/Codex_Luna/.benchmark-temp/2175-separated` に置き、過去の6要求を上書きしない。訂正引き継ぎには元の入力、Haiku回答、検証器が不一致としたIDを渡すが期待値は渡さず、全問の回答を取り直す。

```powershell
python tests/fixtures/model-selection-2175/runner.py --fixture-dir tests/fixtures/model-selection-2175-separated --model haiku --batch 1 --cli C:/Users/smile/AppData/Roaming/npm/node_modules/@anthropic-ai/claude-code/bin/claude.exe --raw-dir D:/Users/hal/Codex_Luna/.benchmark-temp/2175-separated --out D:/Users/hal/Codex_Luna/.benchmark-temp/2175-separated/haiku-1.json
```

まずdry run。実行は `--execute` を追加し、model haiku/opus と batch 1（抽出）/2（検索）を組み合わせる。訂正が必要な場合だけ opus の要求に `--handoff-from .../haiku-1.json` または `haiku-2.json` を加え、out は `correction-1.json` 等の別名にする。runnerは元のHaiku回答の固定検証を再計算し、同じ種類の訂正を1回に制限する。

費用は各種類のバッチごとの CLI 返却 LLM 費用とし、固定機械検証器の実行時間を別に記録する。検証器の現金費用、親による意味検証費、subscription消費、実仕事への一般化は未測定。キャッシュやシステム文のトークン差、少数の固定課題・単発試行の限界を残し、返却費用だけから月額節約を主張しない。規範的なskills/rules変更、PR、自己レビュー、mergeはこの段階でも行わない。
