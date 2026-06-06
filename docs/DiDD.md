# 対話駆動開発 ── Dialogue-Driven Development (DiDD)

本文書は Li+ プログラムの**設計思想を束ねる総称**を担う。設計思想 4 文書 (E-H) が軸別に蒸留した内容を、「○○駆動開発」の系譜で呼べる一つの名前にまとめたものが **DiDD (Dialogue-Driven Development / 対話駆動開発)** である。

DiDD は新しい概念ではない。Li+ の三本柱を、TDD / BDD と同じ系譜の手法名として読めるようにした呼び名であり、各軸の定義 literal は `rules/model/*.md`・`docs/1.-Model.md` および `docs/E.-Li+language.md`〜`docs/H.-Roles-and-Evaluation.md` を正本とする。

---

## 看板

> 対話駆動開発 = Dialogue-Driven Development (DiDD)
> ── 対話で要求を作り、構造で実行を律し、現実(実機の動いた挙動)で正しさを測る。──

この一行は Li+ の進め方そのものである。読み下すと、Li+ は三段で動く。

---

## 三本柱 ── 三つの「駆動」

DiDD という総称の中身は、三つの「○○駆動」である。それぞれが Li+ の一段に対応し、深い定義は元の文書が持つ。DiDD ページは流れを束ねる役、各軸の中身はリンク先が担う。

| 駆動 | 一段 | 何をするか | 詳細・背景 |
|------|------|-----------|-----------|
| **対話駆動** | 入口 | 会話そのものはコードではない。会話から蒸留し要求として固定した要求仕様書がコードになる | [E. Li+language](E.-Li+language) |
| **構造駆動** | 方法 | レイヤー・規則・再適用条件を固定し、AI がどう判断し・実行し・どこで止まるかを構造で安定させる | [1. Model](1.-Model) |
| **現実駆動** | 判定 | 説明・意図・内部整合は正しさにならない。実機で動いた挙動だけが正しさを定義する | [F. Behavior-First](F.-Behavior-First)（なぜ現実が正義か の背景） |

DiDD は **対話駆動** を看板に立てているが、束ねているのは三つすべてである。対話で要求を作り（対話駆動）、構造で実行を律し（構造駆動）、現実で正しさを測る（現実駆動）── 三段がそろってはじめて Li+ の一周が閉じる。

---

## なぜ「DiDD」と表記するか

Dialogue-Driven Development を素直に略すと DDD になるが、これは Domain-Driven Design（ドメイン駆動設計）が占有している。衝突を避けるため Dialogue の **Di** を立てて **DiDD** と表記する。

- 表記は小文字 i 固定の **DiDD**。全大文字 DIDD は別領域の略語と衝突するため使わない。
- 語尾の DD（Driven Development）が TDD / BDD と同じ系譜であることを示し、「Li+ は対話を駆動源に置いた開発手法」という位置を一目で伝える。

---

## 「最高級言語」との関係

Li+ は別の入口からは **最高級プログラム言語** と呼ばれる（[A. Concept](A.-Concept)、[E. Li+language](E.-Li+language)）。両者は矛盾しない。

- **最高級言語** = Li+ が **何であるか**（正体・言語としての位置）
- **DiDD** = その言語を **どう回すか**（対話 → 構造 → 現実 の手法・進め方）

同じものを、正体の側から見た名前と、手法の側から見た名前である。

---

## 関連

- 関連 docs（設計思想 4 文書）:
  - `docs/E.-Li+language.md`（対話駆動の中身 ── 要求仕様 = code、対話型コンパイラ、三位一体）
  - `docs/F.-Behavior-First.md`（現実駆動の中身 ── 動いている挙動が正しさ、なぜ現実が正義か）
  - `docs/G.-Sheepdog-Engineering.md`（装具内化、Lilayer / pal）
  - `docs/H.-Roles-and-Evaluation.md`（役割分離、評価軸）
- 関連 spec literal:
  - `rules/model/language-definition.md`（対話駆動 ── Li+ language / 要求仕様 = code の正本）
  - `rules/model/foundational-invariant.md`（現実駆動 ── 正しさの定義の正本）
  - `docs/1.-Model.md`（構造駆動 ── モデルレイヤー仕様）
