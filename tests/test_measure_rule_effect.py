"""The pure logic of `scripts/measure_rule_effect.py` holds its structural guarantees.

Spec source: issue #1848, and `skills/evolution-rule-effect-measurement/SKILL.md`.

Scope. The arm launch (`claude -p`) is an external dependency that consumes external
budget, so it is not exercised here and never runs in CI. What is exercised is
everything the design turned from a procedure into a structure, which is exactly the
part that fails silently when it regresses:

- the lock, which replaces "take care not to run two at once" with "the second one
  cannot start", including both ways a held lock is broken - a dead holder PID, and
  the stale-timestamp takeover the accepted tradeoff names;
- the two cleanup layers, the unconditional wipe at the head of a run and the
  `finally` removal, and the fact that the wipe does not take the lock with it;
- the contrast principle, held in two places - the plan's edit budget, and the
  verification against the arms as built;
- the guards that turn a silently-wrong run into a refused one: an anchor that
  matches zero or several times, and inserted text that tells the arm what it is
  standing in.

`rules/model/subtractive-structural-beauty.md` puts a procedure whose execution is not
guaranteed on the replace-with-a-structure side. These assertions are what keeps those
structures from decaying back into procedures without anything reporting it.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import measure_rule_effect as module


NOW = datetime(2026, 9, 4, 12, 0, 0, tzinfo=timezone.utc)


def valid_plan_data(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "probe": "A governance restructure with no observable behavior change. Version type?",
        "model": "opus",
        "repetitions": 3,
        "arms": [
            {"name": "a", "edits": []},
            {
                "name": "b",
                "edits": [
                    {"path": ".claude/rules/model/sample.md", "drop": "the anchor line"}
                ],
            },
        ],
    }
    data.update(overrides)
    return data


class TempDirCase(unittest.TestCase):
    def temp_path(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def make_source_root(self, body: str = "keep\nthe anchor line\ntail\n") -> Path:
        root = self.temp_path() / "workspace"
        rules = root / ".claude" / "rules" / "model"
        rules.mkdir(parents=True)
        (rules / "sample.md").write_text(body, encoding="utf-8")
        (root / "CLAUDE.md").write_text("# host instruction\n", encoding="utf-8")
        (root / "Li+config.md").write_text("LI_PLUS_MODE=clone\n", encoding="utf-8")
        return root


class PlanValidationTest(unittest.TestCase):
    def test_a_valid_plan_loads(self) -> None:
        plan = module.load_plan(valid_plan_data())
        self.assertEqual(plan.model, "opus")
        self.assertEqual(plan.repetitions, 3)
        self.assertEqual([arm.name for arm in plan.arms], ["a", "b"])
        self.assertEqual(plan.arms[1].edits[0].replace_with, "")

    def test_the_two_arms_must_differ_in_exactly_one_place(self) -> None:
        """The contrast principle, on the asked-for side."""
        second_edit = {"path": "CLAUDE.md", "drop": "host"}
        too_many = valid_plan_data()
        too_many["arms"][1]["edits"].append(second_edit)  # type: ignore[index]
        with self.assertRaises(module.PlanError):
            module.load_plan(too_many)

        none_at_all = valid_plan_data()
        none_at_all["arms"][1]["edits"] = []  # type: ignore[index]
        with self.assertRaises(module.PlanError):
            module.load_plan(none_at_all)

    def test_the_edit_may_sit_on_either_arm(self) -> None:
        """Which arm carries the change is the operator's call; the budget is not."""
        data = valid_plan_data()
        data["arms"][0]["edits"] = data["arms"][1]["edits"]  # type: ignore[index]
        data["arms"][1]["edits"] = []  # type: ignore[index]
        plan = module.load_plan(data)
        self.assertEqual(len(plan.arms[0].edits), 1)
        self.assertEqual(plan.arms[1].edits, ())

    def test_the_arm_model_has_no_default(self) -> None:
        """Measured: leak rate reversed with the arm's model, so it is a condition."""
        data = valid_plan_data()
        del data["model"]
        with self.assertRaises(module.PlanError):
            module.load_plan(data)

    def test_arm_count_is_fixed_at_two(self) -> None:
        for arms in ([valid_plan_data()["arms"][0]], []):  # type: ignore[index]
            with self.subTest(count=len(arms)):
                with self.assertRaises(module.PlanError):
                    module.load_plan(valid_plan_data(arms=arms))

    def test_duplicate_arm_names_are_refused(self) -> None:
        data = valid_plan_data()
        data["arms"][1]["name"] = "a"  # type: ignore[index]
        with self.assertRaises(module.PlanError):
            module.load_plan(data)

    def test_repetitions_must_be_a_positive_integer(self) -> None:
        for value in (0, -1, "3", 1.5, True):
            with self.subTest(value=value):
                with self.assertRaises(module.PlanError):
                    module.load_plan(valid_plan_data(repetitions=value))

    def test_edit_paths_stay_inside_the_arm(self) -> None:
        for path in ("../outside.md", "/etc/passwd", ".claude/../../escape.md"):
            with self.subTest(path=path):
                data = valid_plan_data()
                data["arms"][1]["edits"][0]["path"] = path  # type: ignore[index]
                with self.assertRaises(module.PlanError):
                    module.load_plan(data)

    def test_edit_paths_must_target_a_copied_entry(self) -> None:
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["path"] = "rules/model/sample.md"  # type: ignore[index]
        with self.assertRaises(module.PlanError):
            module.load_plan(data)

    def test_the_grounding_measurement_is_refused_verbatim(self) -> None:
        """Acceptance case 0 (issue #1938): the guard catches its own grounds.

        The first two entries are the measured literal, copied from
        `skills/evolution-rule-effect-measurement/SKILL.md` Containment when a
        file is placed, with its determiner `the` and not a paraphrase's
        `this`. A guard that cannot reject the sentence its grounds rest on is
        a hole in the guard; the first shipped shape rejected it on the bare
        word `trial`, and the co-occurrence shape that replaced the bare word
        let it through, which is what this asserts against.
        """
        for text in (
            "The file was a copy made for a trial.",
            "Note: the file is a copy made for a trial, so the verdict is not "
            "for production use.",
            "This file was a copy made for a trial.",
            "This file is a copy made for a trial; "
            "its verdict is not for production use.",
        ):
            with self.subTest(text=text):
                data = valid_plan_data()
                data["arms"][1]["edits"][0]["replace_with"] = text  # type: ignore[index]
                with self.assertRaises(module.PlanError):
                    module.load_plan(data)

    def test_inserted_text_may_not_say_this_body_is_made_for_the_run(self) -> None:
        """The claim in the forms the guard was already asserted against."""
        for text in (
            "this file is an experimental copy",
            "This document is variant B of the rules.",
            "This text is a test fixture, not the shipped one.",
            "You are reading a copy made for a trial.",
            "このファイルは実験用の複写である",
            "この複製は検証用に作られた",
        ):
            with self.subTest(text=text):
                data = valid_plan_data()
                data["arms"][1]["edits"][0]["replace_with"] = text  # type: ignore[index]
                with self.assertRaises(module.PlanError):
                    module.load_plan(data)

    def test_the_claim_is_refused_in_shapes_no_earlier_list_carried(self) -> None:
        """Acceptance case 4 (issue #1938), and fresh shapes beyond it.

        The first three are the measured false negatives: a Japanese deictic
        absent from the earlier set (`本ファイル`), a Japanese run word absent
        from the earlier vocabulary (`試行`), and an English determiner the
        earlier set could not reach (`That copy`). The rest are written here
        rather than measured, to check that the predicate holds a shape and is
        not fitted to a list: a relative clause between subject and copula,
        markdown list markers ahead of the subject, plural subjects, and a
        perfect passive.
        """
        for text in (
            "本ファイルは試験用の複製である。",
            "この写しは試行のために作られた。",
            "That copy was produced by an experiment.",
            "The document you are reading was generated for a measurement.",
            "This draft is an excerpt prepared for the trial run.",
            "The note was placed here by the harness and will be deleted.",
            "These files are duplicates created for the experiment.",
            "The body has been derived from the upstream file for this "
            "evaluation.",
            "* This page is a snapshot made for the variant comparison.",
            "1. The version was cloned for a probe run.",
            "この文書は計測のために用意されたものだ。",
            "本稿はテスト用に書かれている。",
        ):
            with self.subTest(text=text):
                data = valid_plan_data()
                data["arms"][1]["edits"][0]["replace_with"] = text  # type: ignore[index]
                with self.assertRaises(module.PlanError):
                    module.load_plan(data)

    def test_a_report_of_the_claim_is_not_the_claim(self) -> None:
        """The subject constraint, which is what separates the two.

        The entry below is the sentence in
        `skills/evolution-rule-effect-measurement/SKILL.md` that the acceptance
        case above is copied out of. It contains that sentence, word for word,
        and its own subject is the arm - so the body reporting a measurement of
        the claim is not itself making it. Removing the subject constraint
        makes the guard unable to measure its own spec.
        """
        text = (
            "Measured: an arm read a note inside its own source saying the "
            "file was a copy made for a trial, and added that its verdict was "
            "therefore not for production use."
        )
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["replace_with"] = text  # type: ignore[index]
        plan = module.load_plan(data)
        self.assertEqual(plan.arms[1].edits[0].replace_with, text)

    def test_run_vocabulary_without_the_claim_passes(self) -> None:
        """Acceptance case 1 (issue #1938), in a form that carries no local path.

        The failing input was a body written from scratch out of judgment
        records: it exists in no repository file, so the provenance exemption
        cannot reach it, and it carries the L2 layer's own domain vocabulary
        without ever declaring what it is. The excerpt below reproduces that
        shape - `variants`, `probe`, `test` and `tested` all present, no
        sentence claiming this body was made for a run.
        """
        text = (
            "- **`P` (premise_variations)** - how many premise variants of the "
            "same round are run side by side.\n"
            "Required again for a `skills/<name>/SKILL.md` draft read by a "
            "probe-type evaluator, since a probe's validity depends on the "
            "skill actually being invokable.\n"
            "For the fixed axis, the source is the removal test defined in "
            "`skills/evolution-impression-literal-detection/SKILL.md`.\n"
            "A rejected finding gets a full reply: the finding quoted, the "
            "source it was tested against, and what the test returned.\n"
        )
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["replace_with"] = text  # type: ignore[index]
        plan = module.load_plan(data)
        self.assertEqual(plan.arms[1].edits[0].replace_with, text)

    def test_an_artifact_subject_without_the_predicate_passes(self) -> None:
        """Acceptance case 5 (issue #1938): the measured false positives.

        Each names the artifact and carries a run word, and none of them claims
        the body was made for a run. The third is what fixes the complement
        slot at two words off the copula: `is quoted from the probe` puts the
        run word four words out, and a wider slot would take it.
        """
        for text in (
            "This file states the removal test.",
            "This document fixes what the harness enforces structurally.",
            "This text is quoted from the probe specification.",
            "Read this body against the test the spec fixes.",
        ):
            with self.subTest(text=text):
                data = valid_plan_data()
                data["arms"][1]["edits"][0]["replace_with"] = text  # type: ignore[index]
                plan = module.load_plan(data)
                self.assertEqual(plan.arms[1].edits[0].replace_with, text)

    def test_ordinary_li_plus_prose_passes(self) -> None:
        """Fresh sentences, written here rather than taken from a measured list.

        Every one names an artifact and a run word, several in copular form.
        A predicate fitted to the measured false positives above would let the
        next sentence off that list fail, which is the failure mode this whole
        issue repairs.
        """
        for text in (
            "The file the harness copies is never the one under test.",
            "This document is the canonical surface for the removal test.",
            "The arm reads the probe once per repetition.",
            "This body was written to be read at the application moment.",
            "The copy the reviewer sees is the PR diff, not a local tree.",
            "This note explains why the trial vocabulary is not the predicate.",
            "A test that has stopped checking what it claims still reports "
            "green.",
            "The measurement is raised before brake 1, not after it.",
            "Every probe in this file is answered by a separate process.",
            "This version of the harness places nothing under .claude/.",
            "The draft is reviewed against the issue body, and the test suite "
            "is run.",
            "This text fixes what the probe specification leaves open.",
            "This file names the latest release that wins the contest.",
            "This document holds the operational detail; this file does not "
            "restate it.",
        ):
            with self.subTest(text=text):
                data = valid_plan_data()
                data["arms"][1]["edits"][0]["replace_with"] = text  # type: ignore[index]
                plan = module.load_plan(data)
                self.assertEqual(plan.arms[1].edits[0].replace_with, text)

    def test_this_rule_is_not_an_artifact_subject(self) -> None:
        """`this rule` names what the body is about, not what the body is.

        Carrying it in the artifact-noun set would reintroduce the
        over-rejection issue #1938 reports, one noun over.
        """
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["replace_with"] = (  # type: ignore[index]
            "This rule is a test of the removal criterion; this section is a "
            "copy of the probe."
        )
        plan = module.load_plan(data)
        self.assertIn("removal criterion", plan.arms[1].edits[0].replace_with)

    def test_the_claim_must_stand_in_one_sentence(self) -> None:
        """Neighbouring sentences are not a self-declaration."""
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["replace_with"] = (  # type: ignore[index]
            "The probe is answered once per repetition. This file holds the "
            "adjudication rules."
        )
        plan = module.load_plan(data)
        self.assertIn("probe", plan.arms[1].edits[0].replace_with)

    def test_no_repository_markdown_body_is_rejected(self) -> None:
        """Acceptance case 6 (issue #1938): the over-rejection sweep, as a test.

        Every markdown body under the always-loaded surfaces and the docs tree,
        put to the guard with the provenance exemption off, so that each one is
        judged on the predicate alone. A hit here is the guard reading ordinary
        Li+ prose as a self-declaration, which is the direction the earlier bare
        word shape failed in.
        """
        root = Path(__file__).resolve().parents[1]
        swept = 0
        for directory in ("rules", "skills", "adapter", "docs"):
            for body in sorted((root / directory).rglob("*.md")):
                swept += 1
                with self.subTest(body=str(body.relative_to(root))):
                    module._reject_self_declaring(
                        body.read_text(encoding="utf-8"), None, body.name
                    )
        self.assertGreater(swept, 50)



class SelfDeclaringProvenanceTest(TempDirCase):
    """Issue #1935: provenance exempts a file's own full body from the vocabulary guard."""

    def test_text_matching_an_existing_file_in_full_is_exempted(self) -> None:
        """(b): a verbatim full-file match was not written for this run.

        The body carries a sentence the guard would otherwise refuse, so the
        exemption is what this asserts and not the claim check.
        """
        body = "this file is a copy made for a trial\nsecond line\n"
        source = self.make_source_root(body=body)
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["replace_with"] = body  # type: ignore[index]
        plan = module.load_plan(data, source)
        self.assertEqual(plan.arms[1].edits[0].replace_with, body)

    def test_a_partial_match_is_not_exempted(self) -> None:
        """Acceptance case 3 (issue #1938): partial fabrication stays refused.

        A real file's body with one self-declaring line added clears neither
        gate - not the exemption, which needs a full match, and not the
        claim check, which the added line trips.
        """
        body = "the harness runs a probe against the test arm\nsecond line\n"
        source = self.make_source_root(body=body)
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["replace_with"] = (  # type: ignore[index]
            body + "this file is an experimental copy"
        )
        with self.assertRaises(module.PlanError):
            module.load_plan(data, source)

    def test_the_guards_own_skill_passes_without_the_exemption(self) -> None:
        """Acceptance case 2 (issue #1938): the instrument can measure its own spec.

        Asserted against the claim check alone (`source_root=None`), so
        it does not pass merely by being byte-identical to itself. The skill
        discusses probes and tests throughout without ever saying that this body
        was made for a run.
        """
        skill = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "evolution-rule-effect-measurement"
            / "SKILL.md"
        )
        module._reject_self_declaring(
            skill.read_text(encoding="utf-8"), None, skill.name
        )

    def test_no_file_at_the_edit_path_falls_back_to_the_guard(self) -> None:
        source = self.make_source_root()
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["path"] = ".claude/rules/model/missing.md"  # type: ignore[index]
        data["arms"][1]["edits"][0]["replace_with"] = "This file is a test fixture"  # type: ignore[index]
        with self.assertRaises(module.PlanError):
            module.load_plan(data, source)

    def test_a_mismatched_body_at_a_real_path_is_not_exempted(self) -> None:
        source = self.make_source_root(body="keep\nthe anchor line\ntail\n")
        data = valid_plan_data()
        data["arms"][1]["edits"][0]["replace_with"] = (  # type: ignore[index]
            "This file is a test fixture, not the real body"
        )
        with self.assertRaises(module.PlanError):
            module.load_plan(data, source)


class LockTest(TempDirCase):
    def test_the_second_run_cannot_start(self) -> None:
        root = self.temp_path() / "harness"
        first = module.acquire_lock(root, NOW)
        self.assertTrue(first.is_dir())
        with self.assertRaises(module.LockUnavailable):
            module.acquire_lock(root, NOW)

    def test_the_lock_carries_a_timestamp_and_the_holder_pid(self) -> None:
        """Both are written: the PID decides first, the timestamp is the fallback."""
        root = self.temp_path() / "harness"
        lock_dir = module.acquire_lock(root, NOW)
        entries = sorted(path.name for path in lock_dir.iterdir())
        self.assertEqual(
            entries, sorted([module.LOCK_STAMP_FILENAME, module.LOCK_PID_FILENAME])
        )
        stamp = (lock_dir / module.LOCK_STAMP_FILENAME).read_text(encoding="utf-8")
        self.assertEqual(datetime.fromisoformat(stamp), NOW)
        self.assertEqual(module.lock_holder_pid(lock_dir), os.getpid())

    def test_a_live_holder_still_refuses_a_fresh_lock(self) -> None:
        """The acceptance line: holder alive, so the refusal is unchanged."""
        root = self.temp_path() / "harness"
        module.acquire_lock(root, NOW)
        with mock.patch.object(module, "process_is_alive", return_value=True):
            with self.assertRaises(module.LockUnavailable) as caught:
                module.acquire_lock(root, NOW)
        self.assertIn(f"held by pid {os.getpid()}", str(caught.exception))

    def test_a_dead_holder_lock_is_broken_well_inside_the_threshold(self) -> None:
        """The defect #1945 reports: a killed run must not lock successors out."""
        root = self.temp_path() / "harness"
        module.acquire_lock(root, NOW)
        moments_later = NOW + timedelta(seconds=257)
        with mock.patch.object(module, "process_is_alive", return_value=False):
            retaken = module.acquire_lock(root, moments_later)
        stamp = (retaken / module.LOCK_STAMP_FILENAME).read_text(encoding="utf-8")
        self.assertEqual(datetime.fromisoformat(stamp), moments_later)

    def test_a_lock_with_no_pid_is_judged_by_the_threshold_alone(self) -> None:
        """Backward compatibility: a lock from the revision that wrote no PID."""
        root = self.temp_path() / "harness"
        lock_dir = module.acquire_lock(root, NOW)
        (lock_dir / module.LOCK_PID_FILENAME).unlink()
        self.assertIsNone(module.lock_holder_pid(lock_dir))
        with mock.patch.object(module, "process_is_alive") as probe:
            with self.assertRaises(module.LockUnavailable):
                module.acquire_lock(root, NOW)
            probe.assert_not_called()
        later = NOW + timedelta(seconds=module.STALE_LOCK_SECONDS + 1)
        with mock.patch.object(module, "process_is_alive") as probe:
            module.acquire_lock(root, later)
            probe.assert_not_called()

    def test_a_liveness_check_that_raises_reads_as_alive(self) -> None:
        """Undecidable falls to refusal; breaking a live run's lock is the worse error."""
        root = self.temp_path() / "harness"
        module.acquire_lock(root, NOW)
        with mock.patch.object(module, "process_is_alive", side_effect=OSError("opaque")):
            with self.assertRaises(module.LockUnavailable):
                module.acquire_lock(root, NOW)

    def test_the_live_probe_answers_for_this_process_without_starting_one(self) -> None:
        """The real probe, on both platforms, against the one PID known to be alive."""
        self.assertTrue(module.process_is_alive(os.getpid()))
        self.assertTrue(module.process_is_alive(0))
        self.assertTrue(module.process_is_alive(-1))

    def test_a_lock_older_than_the_threshold_is_taken_over(self) -> None:
        root = self.temp_path() / "harness"
        module.acquire_lock(root, NOW)
        later = NOW + timedelta(seconds=module.STALE_LOCK_SECONDS + 1)
        retaken = module.acquire_lock(root, later)
        stamp = (retaken / module.LOCK_STAMP_FILENAME).read_text(encoding="utf-8")
        self.assertEqual(datetime.fromisoformat(stamp), later)

    def test_a_lock_at_the_threshold_is_still_held(self) -> None:
        root = self.temp_path() / "harness"
        module.acquire_lock(root, NOW)
        at_threshold = NOW + timedelta(seconds=module.STALE_LOCK_SECONDS)
        with self.assertRaises(module.LockUnavailable):
            module.acquire_lock(root, at_threshold)

    def test_a_lock_with_no_stamp_falls_back_to_directory_mtime(self) -> None:
        """A run killed between mkdir and the stamp write must not wedge the harness."""
        root = self.temp_path() / "harness"
        lock_dir = module.acquire_lock(root, NOW)
        (lock_dir / module.LOCK_STAMP_FILENAME).unlink()
        age = module.lock_age_seconds(lock_dir, datetime.now(timezone.utc))
        self.assertGreaterEqual(age, 0.0)
        retaken = module.acquire_lock(
            root, datetime.now(timezone.utc), stale_after=-1.0
        )
        self.assertTrue((retaken / module.LOCK_STAMP_FILENAME).is_file())

    def test_release_removes_the_lock(self) -> None:
        root = self.temp_path() / "harness"
        lock_dir = module.acquire_lock(root, NOW)
        module.release_lock(lock_dir)
        self.assertFalse(lock_dir.exists())
        module.release_lock(lock_dir)  # idempotent: `finally` may run after a failure

    def test_release_of_a_never_taken_lock_is_silent(self) -> None:
        module.release_lock(self.temp_path() / "absent" / "lock")


class WorkDirTest(TempDirCase):
    def test_the_head_of_a_run_wipes_what_the_previous_one_left(self) -> None:
        root = self.temp_path() / "harness"
        arms = root / module.ARMS_DIRNAME
        (arms / "a" / ".claude").mkdir(parents=True)
        (arms / "a" / "debris.md").write_text("left behind\n", encoding="utf-8")

        recreated = module.reset_work_dir(root)
        self.assertEqual(recreated, arms)
        self.assertEqual(list(recreated.iterdir()), [])

    def test_a_read_only_entry_does_not_wedge_the_wipe(self) -> None:
        """The copy carries the live tree's read-only attribute; the wipe clears it.

        Measured: an arm's copied `.claude` refused removal while sitting empty, and
        the wipe that raises does so at the *head* of the next run - aborting it
        before it launches anything.
        """
        root = self.temp_path()
        arms = root / module.ARMS_DIRNAME
        nested = arms / "a-off" / ".claude"
        nested.mkdir(parents=True)
        (nested / "settings.json").write_text("{}", encoding="utf-8")
        module.os.chmod(nested / "settings.json", module.stat.S_IREAD)
        module.os.chmod(nested, module.stat.S_IREAD | module.stat.S_IEXEC)

        module.reset_work_dir(root)

        self.assertTrue(arms.is_dir())
        self.assertEqual(list(arms.iterdir()), [])

    def test_removing_an_absent_tree_is_silent(self) -> None:
        module.remove_tree(self.temp_path() / "never-existed")

    def test_the_wipe_does_not_take_the_lock_with_it(self) -> None:
        """The two are siblings on purpose; wiping the lock would defeat it."""
        root = self.temp_path() / "harness"
        lock_dir = module.acquire_lock(root, NOW)
        module.reset_work_dir(root)
        self.assertTrue(lock_dir.is_dir())
        self.assertTrue((lock_dir / module.LOCK_STAMP_FILENAME).is_file())

    def test_the_work_path_is_fixed_under_temp(self) -> None:
        base = self.temp_path()
        self.assertEqual(module.harness_root(base), base / module.HARNESS_DIRNAME)
        self.assertEqual(module.harness_root(base), module.harness_root(base))


class MaterializeTest(TempDirCase):
    def test_an_arm_carries_the_always_loaded_surface_and_no_git(self) -> None:
        source = self.make_source_root()
        (source / ".git").mkdir()
        (source / ".git" / "config").write_text("[remote]\n", encoding="utf-8")
        (source / "unrelated.py").write_text("x = 1\n", encoding="utf-8")

        arm = self.temp_path() / "arm"
        copied = module.materialize_arm(source, arm)

        self.assertEqual(copied, [".claude", "CLAUDE.md", "Li+config.md"])
        self.assertTrue((arm / ".claude" / "rules" / "model" / "sample.md").is_file())
        self.assertFalse((arm / ".git").exists())
        self.assertFalse((arm / "unrelated.py").exists())

    def test_a_source_without_claude_is_refused(self) -> None:
        source = self.temp_path() / "bare"
        source.mkdir()
        with self.assertRaises(module.HarnessError):
            module.materialize_arm(source, self.temp_path() / "arm")

    def test_hooks_are_removed_from_the_arm(self) -> None:
        source = self.make_source_root()
        hooks = source / ".claude" / "hooks"
        hooks.mkdir()
        (hooks / "on-session-start.sh").write_text("echo material\n", encoding="utf-8")
        (source / ".claude" / "settings.json").write_text(
            json.dumps({"outputStyle": "character_Instance", "hooks": {"SessionStart": []}}),
            encoding="utf-8",
        )

        arm = self.temp_path() / "arm"
        module.materialize_arm(source, arm)

        self.assertFalse((arm / ".claude" / "hooks").exists())
        settings = json.loads((arm / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertNotIn("hooks", settings)
        self.assertEqual(settings["outputStyle"], "character_Instance")

    def test_unreadable_settings_stop_the_run(self) -> None:
        """Silently leaving a live hook in place would add a second difference."""
        source = self.make_source_root()
        (source / ".claude" / "settings.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(module.HarnessError):
            module.materialize_arm(source, self.temp_path() / "arm")

    def test_find_workspace_root_walks_up_to_the_claude_directory(self) -> None:
        source = self.make_source_root()
        nested = source / "a" / "b"
        nested.mkdir(parents=True)
        self.assertEqual(module.find_workspace_root(nested), source.resolve())

    def test_find_workspace_root_reports_when_there_is_none(self) -> None:
        """`.claude` is patched away rather than sought in a bare temp directory.

        A temp directory's own ancestors reach the user's home, which carries a
        `.claude` on a normal developer machine. A test asserting the walk finds
        nothing there would pass or fail on where the host puts its temp files.
        """
        with mock.patch.object(module.Path, "is_dir", return_value=False):
            with self.assertRaises(module.HarnessError):
                module.find_workspace_root(self.temp_path())


class EditTest(TempDirCase):
    def build_arm(self, body: str) -> Path:
        source = self.make_source_root(body)
        arm = self.temp_path() / "arm"
        module.materialize_arm(source, arm)
        return arm

    def test_an_edit_drops_its_anchor(self) -> None:
        arm = self.build_arm("keep\nthe anchor line\ntail\n")
        module.apply_edit(arm, module.Edit(path=".claude/rules/model/sample.md", drop="the anchor line\n"))
        text = (arm / ".claude" / "rules" / "model" / "sample.md").read_text(encoding="utf-8")
        self.assertEqual(text, "keep\ntail\n")

    def test_an_edit_may_replace_rather_than_delete(self) -> None:
        arm = self.build_arm("keep\nthe anchor line\ntail\n")
        module.apply_edit(
            arm,
            module.Edit(
                path=".claude/rules/model/sample.md",
                drop="the anchor line",
                replace_with="a shorter line",
            ),
        )
        text = (arm / ".claude" / "rules" / "model" / "sample.md").read_text(encoding="utf-8")
        self.assertIn("a shorter line", text)

    def test_an_anchor_that_matches_nothing_is_refused(self) -> None:
        """Zero matches would compare two identical arms and report no difference."""
        arm = self.build_arm("keep\ntail\n")
        with self.assertRaises(module.EditError):
            module.apply_edit(arm, module.Edit(path=".claude/rules/model/sample.md", drop="absent"))

    def test_an_ambiguous_anchor_is_refused(self) -> None:
        arm = self.build_arm("the anchor line\nthe anchor line\n")
        with self.assertRaises(module.EditError):
            module.apply_edit(
                arm, module.Edit(path=".claude/rules/model/sample.md", drop="the anchor line")
            )

    def test_a_missing_target_file_is_refused(self) -> None:
        arm = self.build_arm("keep\n")
        with self.assertRaises(module.EditError):
            module.apply_edit(arm, module.Edit(path="CLAUDE.md/nope.md", drop="x"))


class ContrastTest(TempDirCase):
    def build_pair(self, edits: bool = True) -> list[Path]:
        source = self.make_source_root()
        base = self.temp_path() / "arms"
        roots = []
        for name in ("a", "b"):
            arm = base / name
            module.materialize_arm(source, arm)
            roots.append(arm)
        if edits:
            module.apply_edit(
                roots[1], module.Edit(path=".claude/rules/model/sample.md", drop="the anchor line\n")
            )
        return roots

    def test_the_built_arms_differ_in_exactly_one_file(self) -> None:
        """The contrast principle, verified against what was built, not what was asked."""
        roots = self.build_pair()
        self.assertEqual(
            module.assert_single_contrast(roots), [".claude/rules/model/sample.md"]
        )

    def test_identical_arms_are_refused(self) -> None:
        roots = self.build_pair(edits=False)
        with self.assertRaises(module.HarnessError):
            module.assert_single_contrast(roots)

    def test_a_second_difference_is_refused(self) -> None:
        roots = self.build_pair()
        (roots[1] / "CLAUDE.md").write_text("# drifted\n", encoding="utf-8")
        with self.assertRaises(module.HarnessError):
            module.assert_single_contrast(roots)

    def test_a_file_only_one_arm_holds_counts_as_a_difference(self) -> None:
        roots = self.build_pair(edits=False)
        (roots[1] / ".claude" / "extra.md").write_text("added\n", encoding="utf-8")
        self.assertEqual(module.differing_paths(*roots), [".claude/extra.md"])


class CommandAndRecordTest(TempDirCase):
    def test_the_arm_is_a_separate_process_with_a_named_model(self) -> None:
        command = module.arm_command("what is the version type?", "opus")
        self.assertEqual(command[:2], ["claude", "-p"])
        self.assertIn("what is the version type?", command)
        self.assertIn("--output-format", command)
        self.assertIn("opus", command)

    def test_the_executable_is_resolved_against_path_before_launch(self) -> None:
        """npm ships `claude.CMD` on Windows; the extensionless sibling will not start.

        Asserted through a stubbed `which` rather than a real binary, so the check
        holds on a host that has no `claude` installed - which is every CI runner.
        """
        with mock.patch.object(
            module.shutil, "which", return_value=r"C:\npm\claude.CMD"
        ):
            argv = module.launch_argv(["claude", "-p", "probe"])
        self.assertEqual(argv, [r"C:\npm\claude.CMD", "-p", "probe"])

    def test_an_unresolvable_executable_is_refused_by_name(self) -> None:
        with mock.patch.object(module.shutil, "which", return_value=None):
            with self.assertRaises(module.HarnessError) as caught:
                module.launch_argv(["claude", "-p", "probe"])
        self.assertIn("claude", str(caught.exception))

    def test_resolution_happens_inside_the_launch_seam(self) -> None:
        """A caller that substitutes the launch must lose the PATH dependency with it.

        Measured: resolution sitting ahead of an injected runner raised on CI, where
        nothing was ever going to be launched.
        """
        seen: dict[str, object] = {}

        def fake_run(argv, **kwargs):  # type: ignore[no-untyped-def]
            seen["argv"] = argv
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        with mock.patch.object(
            module.shutil, "which", return_value="/usr/bin/claude"
        ), mock.patch.object(module.subprocess, "run", fake_run):
            module.launch(["claude", "-p", "probe"], capture_output=True)

        self.assertEqual(seen["argv"], ["/usr/bin/claude", "-p", "probe"])

    def test_the_run_record_names_the_model_and_the_contrast(self) -> None:
        plan = module.load_plan(valid_plan_data())
        record = module.build_run_record(
            plan,
            Path("/workspace"),
            [".claude/rules/model/sample.md"],
            [{"arm": "a", "run": 1}],
            NOW,
        )
        self.assertEqual(record["model"], "opus")
        self.assertEqual(record["repetitions"], 3)
        self.assertEqual(record["differing_paths"], [".claude/rules/model/sample.md"])
        self.assertEqual(record["started_at"], NOW.isoformat())
        json.dumps(record)  # the record has to survive serialization


class PlanFileMixin(TempDirCase):
    """Plan-on-disk helpers, shared by the two classes that drive `main()`."""

    def write_plan(self, data: dict[str, object]) -> Path:
        path = self.temp_path() / "plan.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def full_plan(self) -> dict[str, object]:
        data = valid_plan_data()
        data["repetitions"] = 2
        data["arms"][1]["edits"][0]["drop"] = "the anchor line\n"  # type: ignore[index]
        return data


class MainTest(PlanFileMixin):
    def test_a_dry_run_builds_the_arms_and_leaves_nothing_behind(self) -> None:
        source = self.make_source_root()
        base = self.temp_path()
        out = self.temp_path() / "record.json"
        code = module.main(
            [
                str(self.write_plan(self.full_plan())),
                "--source-root",
                str(source),
                "--base-dir",
                str(base),
                "--out",
                str(out),
                "--dry-run",
            ]
        )
        self.assertEqual(code, 0)

        record = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(record["differing_paths"], [".claude/rules/model/sample.md"])
        self.assertEqual(len(record["results"]), 4)
        self.assertEqual(record["results"][0]["command"][:2], ["claude", "-p"])

        root = module.harness_root(base)
        self.assertFalse((root / module.ARMS_DIRNAME).exists())
        self.assertFalse((root / module.LOCK_DIRNAME).exists())

    def test_a_failing_run_still_releases_the_lock(self) -> None:
        """The removal sits in `finally`, not at the tail of the happy path."""
        source = self.make_source_root()
        base = self.temp_path()
        broken = self.full_plan()
        broken["arms"][1]["edits"][0]["drop"] = "no such anchor"  # type: ignore[index]

        code = module.main(
            [
                str(self.write_plan(broken)),
                "--source-root",
                str(source),
                "--base-dir",
                str(base),
                "--dry-run",
            ]
        )
        self.assertEqual(code, 2)

        root = module.harness_root(base)
        self.assertFalse((root / module.LOCK_DIRNAME).exists())
        self.assertFalse((root / module.ARMS_DIRNAME).exists())

    def test_a_held_lock_stops_the_run_before_it_builds_anything(self) -> None:
        source = self.make_source_root()
        base = self.temp_path()
        module.acquire_lock(module.harness_root(base), datetime.now(timezone.utc))

        code = module.main(
            [
                str(self.write_plan(self.full_plan())),
                "--source-root",
                str(source),
                "--base-dir",
                str(base),
                "--dry-run",
            ]
        )
        self.assertEqual(code, 3)
        self.assertFalse((module.harness_root(base) / module.ARMS_DIRNAME).exists())

    def test_an_invalid_plan_never_takes_the_lock(self) -> None:
        source = self.make_source_root()
        base = self.temp_path()
        invalid = valid_plan_data()
        del invalid["model"]

        code = module.main(
            [
                str(self.write_plan(invalid)),
                "--source-root",
                str(source),
                "--base-dir",
                str(base),
                "--dry-run",
            ]
        )
        self.assertEqual(code, 2)
        self.assertFalse((module.harness_root(base) / module.LOCK_DIRNAME).exists())


class ArmExitCodeTest(PlanFileMixin):
    """The exit code is the surface a reader opens first, so it has to carry the wipeout.

    Measured (issue #1944): a stage 2 run whose six launches all returned 1 - every one
    of them a spend-limit refusal - exited 0, and two readers in succession took that
    zero as evidence the measurement had run. The per-arm `returncode` held the truth
    and nobody opened it.

    The launch is substituted here, as everywhere in this file: no `claude -p` process
    starts, and none ever does in CI.
    """

    def run_with(self, returncodes: Sequence[int]) -> tuple[int, dict[str, Any]]:
        source = self.make_source_root()
        base = self.temp_path()
        out = self.temp_path() / "record.json"
        remaining = list(returncodes)

        def fake_launch(command, **kwargs):  # type: ignore[no-untyped-def]
            return SimpleNamespace(
                returncode=remaining.pop(0), stdout="answer", stderr=""
            )

        with mock.patch.object(module, "launch", fake_launch):
            code = module.main(
                [
                    str(self.write_plan(self.full_plan())),
                    "--source-root",
                    str(source),
                    "--base-dir",
                    str(base),
                    "--out",
                    str(out),
                ]
            )
        self.assertEqual(remaining, [], "the plan launched a different arm count")
        return code, json.loads(out.read_text(encoding="utf-8"))

    def test_a_run_where_no_arm_returned_zero_exits_non_zero(self) -> None:
        code, record = self.run_with([1, 1, 1, 1])
        self.assertEqual(code, module.EXIT_NO_ARM_RETURNED)
        self.assertEqual(module.EXIT_NO_ARM_RETURNED, 4)
        # The record is still written: dropping the information and fixing the exit
        # code are separate axes, and the per-arm returncode is where the reader goes.
        self.assertEqual([entry["returncode"] for entry in record["results"]], [1] * 4)

    def test_the_new_code_does_not_collide_with_the_plan_and_lock_codes(self) -> None:
        self.assertEqual(
            len({module.EXIT_PLAN, module.EXIT_LOCK, module.EXIT_NO_ARM_RETURNED}), 3
        )

    def test_one_surviving_arm_keeps_the_run_at_zero(self) -> None:
        """A non-zero arm can be the behavior under measurement, so it is not the line."""
        code, record = self.run_with([1, 1, 1, 0])
        self.assertEqual(code, 0)
        self.assertEqual(len(record["results"]), 4)

    def test_a_clean_run_exits_zero(self) -> None:
        code, _ = self.run_with([0, 0, 0, 0])
        self.assertEqual(code, 0)

    def test_a_dry_run_is_outside_the_judgment(self) -> None:
        """No entry carries a `returncode`, so there is no wipeout to detect."""
        source = self.make_source_root()
        base = self.temp_path()
        out = self.temp_path() / "record.json"
        code = module.main(
            [
                str(self.write_plan(self.full_plan())),
                "--source-root",
                str(source),
                "--base-dir",
                str(base),
                "--out",
                str(out),
                "--dry-run",
            ]
        )
        self.assertEqual(code, 0)
        record = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(any("returncode" in entry for entry in record["results"]))

    def test_an_empty_result_set_is_not_a_wipeout(self) -> None:
        self.assertFalse(module.every_arm_failed([]))


if __name__ == "__main__":
    unittest.main()
