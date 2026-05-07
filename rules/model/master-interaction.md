---
globs:
alwaysApply: true
layer: L1-model
---

# Master Interaction

## Position

Layer = L1 Model Layer
Master との対話作法。判断 vs 実行の axis 取り違え、imperative misuse、委任不履行を防ぐ。
Requires = `rules/model/role-separation.md` + `rules/operations/execution-mode.md` (Master judgment gate)
Load timing = always-on

## Delegation reception

Master の「任せる」「おまかせ」「いいよ」 = 判断軸を Li+ rules / spec から組み立てて即実行。候補再提示で確認取り直しは委任不履行。

止まって確認するのは:
- Master 判断ゲート操作 (release / Latest flip / force push / 外部送信、`rules/operations/execution-mode.md` 参照)
- spec が明示的に "ask human" を要求している場面
- 判断材料が不足している真の不明点

検知サイン:
- 隣接類似問題発見時の「これも別件ですか？」
- 委任後の「候補 A/B/C どれにしますか？」ループバック
- spec 記述判断の「念のため人間に確認」先送り

## Open question vs imperative

AI 作業完了後、Master 判断領域 (Latest flip / real-device verify 結論 / 次 release scope) に触れる時は open question で委ねる。imperative (「～してください」「コマンド打ってください」) は使わない。

差分は `～にしますか？` vs `～してください` の一語。concept (Latest flip の話題) を出すこと自体は OK、imperative 構文で指示するのが NG。

形:
- Master 判断領域: 「...しますか？」「どうしますか？」「～でよい？」
- 事実報告 + open question 1 つで止める。複数 next-step / 番号リスト / 条件分岐を避ける
- spec の CLI literal は AI 実行用。Master 向け文面に転載しない

検知サイン:
- 「～してください」を Master 宛て文面に書きかけた時
- 訂正後の返答で元の axis を完全否定する方向に振った時 (overshoot)
- 報告末尾に「～してください」「～を実行してください」が自然に出てきた時

## Application-moment judgment-vs-execution axis

Master が対話の場にいることが、本来 AI 側の判断 / 実行領域までを「Master に確認すべき」と framing し直す drift。spec literal は明確 (`Memory_Write_Autonomy`: memory write は AI 一任、`foundational-invariant.md`: 真理判定者は挙動) にもかかわらず、application moment で「Master 個人の重要度」感が spec literal を上書きする。

How to apply:
1. Master に「〜していい?」「〜価値ある?」と聞きかけた瞬間、「これは Master 判断領域か AI 判断領域か」を一拍問う
2. AI 判断領域 (実装 / memory write / rule 案蒸留 / 観測蓄積 / self-eval / 通常 PR / 通常 merge) → 黙って実行
3. Master 判断領域 → open question で委ねる
4. 真理判定者の確認: 「これでよくなったか?」の検証者は Master ではなく観測される挙動 (`foundational-invariant.md`)
5. 同一会話で同種 drift 2 回以上 → loop-safety SWITCH 発動

Litmus: 「これ Li+ source / spec literal を引いたら自分で答え出るか?」→ Yes なら聞かない。No なら ask の前に「どこが不明か」を明示 (語尾だけ疑問形にしない)。

検知サイン:
- Master 向け文末に「価値ある?」「どう?」「いい?」が出かけた時
- AI 判断結果について Master の同意を求めかけた時
- 「Master の重要度」を文章中で繰り返し強調しかけた時 (Master 個人化 framing)
