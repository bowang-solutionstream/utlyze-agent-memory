"""Synthetic acceptance checks for the distinct I2E team profile."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/i2e-team/scripts/i2e.py"
SPEC = importlib.util.spec_from_file_location("i2e_team_runtime", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)


def ordinary_policy() -> dict:
    return {
        "priority": "P2",
        "risk": "Low",
        "triggers": {
            "consequential_authorization_or_tenant": False,
            "destructive_migration": False,
            "critical_financial_behavior": False,
            "uncertain_cross_system_interaction": False,
            "material_redesign": False,
            "conflicting_reviews": False,
            "user_or_project_requirement": False,
        },
    }


class PolicyTests(unittest.TestCase):
    def assert_blocked(self, request: object) -> None:
        result = RUNTIME.evaluate_policy(request)
        self.assertEqual("BLOCK", result.get("state"))
        self.assertIsNone(result["owner"])
        self.assertIsNone(result["final_review"])
        self.assertTrue(result["errors"], "blocked policy must explain its gap")

    def test_ordinary_task_uses_sol_without_budget_or_astra_final(self) -> None:
        self.assertEqual(
            {
                "schema": "i2e-team-policy-v1",
                "state": "PASS",
                "owner": "sol",
                "final_review": None,
                "errors": [],
            },
            RUNTIME.evaluate_policy(ordinary_policy()),
        )

    def test_each_named_trigger_independently_requires_astra_final(self) -> None:
        for trigger in ordinary_policy()["triggers"]:
            with self.subTest(trigger=trigger):
                request = ordinary_policy()
                request["triggers"][trigger] = True
                result = RUNTIME.evaluate_policy(request)
                self.assertEqual("PASS", result.get("state"))
                self.assertEqual("sol", result["owner"])
                self.assertEqual("astra", result["final_review"])

    def test_p0_selects_astra_owner_without_inventing_final_trigger(self) -> None:
        request = ordinary_policy()
        request["priority"] = "P0"
        result = RUNTIME.evaluate_policy(request)
        self.assertEqual("PASS", result.get("state"))
        self.assertEqual("astra", result["owner"])
        self.assertIsNone(result["final_review"])

    def test_critical_risk_selects_astra_owner_separately_from_final(self) -> None:
        request = ordinary_policy()
        request["risk"] = "Critical"
        result = RUNTIME.evaluate_policy(request)
        self.assertEqual("PASS", result.get("state"))
        self.assertEqual("astra", result["owner"])
        self.assertIsNone(result["final_review"])

    def test_other_classified_priorities_and_risks_keep_sol_owner(self) -> None:
        for priority in ("P1", "P2", "P3"):
            for risk in ("Low", "Medium", "High"):
                with self.subTest(priority=priority, risk=risk):
                    request = ordinary_policy()
                    request.update(priority=priority, risk=risk)
                    result = RUNTIME.evaluate_policy(request)
                    self.assertEqual("PASS", result.get("state"))
                    self.assertEqual("sol", result["owner"])

    def test_unknown_or_malformed_priority_blocks_routing(self) -> None:
        for priority in (None, "UNKNOWN", "P4", "p0", 0, True, [], {}):
            with self.subTest(priority=priority):
                request = ordinary_policy()
                request["priority"] = priority
                self.assert_blocked(request)

    def test_unknown_or_malformed_risk_blocks_routing(self) -> None:
        for risk in (None, "UNKNOWN", "critical", "Extreme", 0, False, [], {}):
            with self.subTest(risk=risk):
                request = ordinary_policy()
                request["risk"] = risk
                self.assert_blocked(request)

    def test_missing_extra_or_malformed_trigger_inventory_blocks(self) -> None:
        missing = ordinary_policy()
        del missing["triggers"]["material_redesign"]
        extra = ordinary_policy()
        extra["triggers"]["eighth_trigger"] = False
        requests = [missing, extra]
        for triggers in (None, [], "UNKNOWN", False):
            request = ordinary_policy()
            request["triggers"] = triggers
            requests.append(request)
        for request in requests:
            with self.subTest(request=request):
                self.assert_blocked(request)

    def test_each_unknown_trigger_blocks_even_with_another_true_trigger(self) -> None:
        for trigger in ordinary_policy()["triggers"]:
            for value in (None, "UNKNOWN", "false", 0, 1, [], {}):
                with self.subTest(trigger=trigger, value=value):
                    request = ordinary_policy()
                    request["triggers"]["material_redesign"] = True
                    request["triggers"][trigger] = value
                    self.assert_blocked(request)

    def test_missing_classifications_or_nonobject_input_blocks(self) -> None:
        missing_priority = ordinary_policy()
        del missing_priority["priority"]
        missing_risk = ordinary_policy()
        del missing_risk["risk"]
        for request in (None, [], "policy", {}, missing_priority, missing_risk):
            with self.subTest(request=request):
                self.assert_blocked(request)

    def test_policy_evaluation_does_not_modify_the_request(self) -> None:
        request = ordinary_policy()
        before = copy.deepcopy(request)
        result = RUNTIME.evaluate_policy(request)
        self.assertEqual("PASS", result.get("state"))
        self.assertEqual(before, request)


class PolicyCliTests(unittest.TestCase):
    def invoke(self, raw: str, *, stdin: bool = False) -> subprocess.CompletedProcess:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        if stdin:
            return subprocess.run(
                [sys.executable, str(SCRIPT), "policy", "--input", "-"],
                input=raw, text=True, capture_output=True, env=env, check=False,
            )
        with tempfile.TemporaryDirectory(prefix="i2e-policy-test-") as temp:
            source = Path(temp) / "policy.json"
            source.write_text(raw, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), "policy", "--input", str(source)],
                text=True, capture_output=True, env=env, check=False,
            )

    def test_policy_cli_reads_json_file_and_reports_selected_owner(self) -> None:
        result = self.invoke(json.dumps(ordinary_policy()))
        payload = json.loads(result.stdout)
        self.assertEqual("PASS", payload.get("state"))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("sol", payload["owner"])

    def test_policy_cli_accepts_stdin_and_returns_block_as_nonzero(self) -> None:
        request = ordinary_policy()
        request["risk"] = "UNKNOWN"
        result = self.invoke(json.dumps(request), stdin=True)
        payload = json.loads(result.stdout)
        self.assertEqual("BLOCK", payload.get("state"))
        self.assertNotEqual(0, result.returncode)

    def test_policy_cli_rejects_duplicate_keys_and_nonfinite_json(self) -> None:
        duplicate = json.dumps(ordinary_policy()).replace(
            '"priority": "P2"', '"priority": "P2", "priority": "P0"'
        )
        for raw in (duplicate, '{"priority": NaN}', '{"priority":'):
            with self.subTest(raw=raw):
                result = self.invoke(raw)
                payload = json.loads(result.stdout)
                self.assertEqual("BLOCK", payload.get("state"))
                self.assertNotEqual(0, result.returncode)
                self.assertTrue(payload["errors"])


CASE_HELPER = Path.home() / ".codex/skills/i2e-failure-cases/scripts/shared_cases.py"


class RuntimeFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="i2e-runtime-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "app.py").write_text("value = 0\n")
        (self.repo / "instructions.md").write_text("Synthetic project rules.\n")
        self.raw = self.root / "evidence.txt"
        self.raw.write_text("Synthetic actual observation.\n")
        self.db = self.root / "private" / "runs.sqlite"

    def contract(self) -> dict:
        result = {
            "schema": "i2e-team-run-v1", "run_id": "run-1", "project": "synthetic",
            "repo": str(self.repo), "scope": ["app.py", "tests.py"],
            "instructions": ["instructions.md"], "contributors": ["owner-session"],
            "authority": {"actions": ["edit"], "evidence": RUNTIME.reference(self.raw)},
            "policy": ordinary_policy(), "known_cases": [],
            "case_store": str(self.root / "cases"), "case_helper": str(CASE_HELPER),
            "case_helper_sha256": hashlib.sha256(CASE_HELPER.read_bytes()).hexdigest(),
        }
        # Explicit fixture migration: archived v1 has no role field. Safety
        # assertions run unchanged against both the frozen and amended schema.
        if getattr(RUNTIME, "AMENDED_PHASES", False):
            result["test_scope"] = ["tests.py"]
        return result

    def seed(self):
        ledger = RUNTIME.Ledger(self.db)
        created = ledger.init_run(self.contract())
        self.assertIsNotNone(created, "run initialization must persist its contract")
        return ledger


class LedgerTests(RuntimeFixture):
    def test_append_is_idempotent_and_conflicting_retries_do_not_overwrite(self) -> None:
        ledger = self.seed()
        event = {"id": "obs-1", "type": "observation", "data": {"status": "INTERRUPTED", "summary": "next investigation"}}
        first = ledger.append("run-1", event, expected_seq=0)
        self.assertIsNotNone(first)
        self.assertEqual(1, first["seq"])
        self.assertEqual(first, ledger.append("run-1", event, expected_seq=0))
        changed = copy.deepcopy(event)
        changed["data"]["summary"] = "invented replacement"
        with self.assertRaises(RUNTIME.RuntimeError):
            ledger.append("run-1", changed, expected_seq=1)
        self.assertEqual("next investigation", ledger.show("run-1")["events"][0]["data"]["summary"])

    def test_two_connections_cannot_reuse_one_expected_sequence(self) -> None:
        ledger = self.seed()
        other = RUNTIME.Ledger(self.db)
        ledger.append("run-1", {"id": "one", "type": "checkpoint", "data": {"next": "continue"}}, expected_seq=0)
        with self.assertRaises(RUNTIME.RuntimeError):
            other.append("run-1", {"id": "two", "type": "checkpoint", "data": {"next": "race"}}, expected_seq=0)
        self.assertEqual(1, other.show("run-1")["seq"])

    def test_fresh_process_retrieves_interruption_and_correction_history(self) -> None:
        ledger = self.seed()
        for seq, event in enumerate([
            {"id": "pause", "type": "checkpoint", "data": {"status": "INTERRUPTED", "next": "inspect boundary"}},
            {"id": "correct", "type": "correction", "data": {"target": "pause", "text": "cause remains unverified"}},
            {"id": "withdraw", "type": "withdrawal", "data": {"target": "objective-1", "text": "owner withdrew objective"}},
        ]):
            ledger.append("run-1", event, expected_seq=seq)
        code = "import json,runpy,sys; n=runpy.run_path(sys.argv[1]); print(json.dumps(n['Ledger'](sys.argv[2]).show('run-1')))"
        result = subprocess.run([sys.executable, "-c", code, str(SCRIPT), str(self.db)], capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        saved = json.loads(result.stdout)
        self.assertEqual(["pause", "correct", "withdraw"], [e["id"] for e in saved["events"]])
        self.assertEqual("withdrawal", saved["current_annotations"][-1]["type"])
        self.assertEqual(1, len(ledger.search("synthetic", "boundary")))
        self.assertEqual([], ledger.search("other-project", "boundary"))

    def test_runtime_database_is_private_and_cannot_live_in_source(self) -> None:
        ledger = self.seed()
        self.assertEqual(0, self.db.stat().st_mode & 0o077)
        with self.assertRaises(RUNTIME.RuntimeError):
            RUNTIME.Ledger(self.repo / "private.sqlite").init_run(self.contract())
        linked = self.root / "linked.sqlite"
        linked.symlink_to(self.db)
        with self.assertRaises(RUNTIME.RuntimeError):
            RUNTIME.Ledger(linked).show("run-1")
        self.assertEqual(0, ledger.show("run-1")["seq"])

    def test_snapshot_binds_absent_files_instructions_and_rejects_symlinks(self) -> None:
        before = RUNTIME.snapshot(self.repo, ["app.py", "tests.py"], ["instructions.md"])
        self.assertIsNotNone(before)
        self.assertIsNone(before["files"]["tests.py"])
        (self.repo / "instructions.md").write_text("Changed rules.\n")
        after = RUNTIME.snapshot(self.repo, ["app.py", "tests.py"], ["instructions.md"])
        self.assertNotEqual(before["sha256"], after["sha256"])
        (self.repo / "tests.py").symlink_to(self.raw)
        with self.assertRaises(RUNTIME.RuntimeError):
            RUNTIME.snapshot(self.repo, ["app.py", "tests.py"], ["instructions.md"])
        with self.assertRaises(RUNTIME.RuntimeError):
            RUNTIME.snapshot(self.repo, ["../evidence.txt"], [])

    def test_local_evidence_reference_binds_real_bytes(self) -> None:
        ref = RUNTIME.reference(self.raw)
        self.assertIsNotNone(ref)
        self.assertEqual(hashlib.sha256(self.raw.read_bytes()).hexdigest(), ref["sha256"])
        self.assertTrue(RUNTIME.verify_reference(ref))
        self.raw.write_text("Edited after observation.\n")
        with self.assertRaises(RUNTIME.RuntimeError):
            RUNTIME.verify_reference(ref)


class LifecycleFixture(RuntimeFixture):
    def prepare(self, *, trigger=False, approve=True, route=True, owner_model="gpt-6.1-sol"):
        self.ledger = self.seed()
        if route:
            self.push("routing", "observation", {"kind": "ROUTING",
                      "owner": {"session": "owner-session", "model": owner_model, "effort": "max", "evidence": RUNTIME.reference(self.raw)},
                      "probe": {"session": "probe-session", "model": "gpt-6.1-sol", "effort": "max", "evidence": RUNTIME.reference(self.raw)}})
        self.ensure_cases()
        self.consultation("c-plan", "plan", "p1")
        policy = ordinary_policy()
        policy["triggers"]["material_redesign"] = trigger
        content = {"artifact": RUNTIME.reference(self.raw), "scope": ["app.py", "tests.py"],
                   "acceptance": [{"id": "behavior", "behavior": True}], "checks": ["unit"],
                   "decisions": [], "decision_reason": "Synthetic assignment boundary; no consequential choice.",
                   "contributors": ["owner-session"], "policy": policy}
        if getattr(RUNTIME, "AMENDED_PHASES", False):
            content["test_scope"] = ["tests.py"]
        self.plan = RUNTIME.digest(content)
        self.push("p1", "plan", {"revision": self.plan, "content": content, "consultation": "c-plan", "supersedes": None})
        if approve:
            self.review("approve-1", "plan_review", "plan-reviewer", "gpt-6-astra", verdict="APPROVE")

    def ensure_cases(self):
        store = self.root / "cases"
        if not (store / "store.json").exists():
            result = subprocess.run([sys.executable, str(CASE_HELPER), "init", "--store", str(store)], capture_output=True, text=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)

    def consultation(self, name, stage, target, *, classify=True, **extra):
        result = self.ledger.consult("run-1", self.ledger.show("run-1")["seq"], {"id": name, "stage": stage, "target": target, "query": "synthetic assignment", **extra})
        self.assertEqual("PASS", result.get("state"), result)
        if classify:
            for index, case_digest in enumerate(result["consultation"]["data"]["known"]):
                self.push(name + "-decision-" + str(index), "case_decision", {"consultation": name, "digest": case_digest, "applicability": "APPLIES", "reason": "Synthetic direct regression", "checks": ["unit"]})
        return result

    def push(self, event_id, kind, data, *, internal=False):
        state = self.ledger.show("run-1")
        return self.ledger._append("run-1", {"id": event_id, "type": kind, "data": data}, expected_seq=state["seq"], internal=internal)

    def current(self):
        return RUNTIME.snapshot(self.repo, ["app.py", "tests.py"], ["instructions.md"])

    def reviewer(self, session, model):
        sessions = {"owner-session"}
        for event in self.ledger.show("run-1")["events"]:
            if event["type"] in {"plan_review", "doubt_review", "audit", "final_review", "recheck", "escalation"}:
                sessions.add(event["data"]["reviewer"]["session"])
            if event["data"].get("kind") == "ROUTING":
                sessions.update(event["data"][lane]["session"] for lane in ("owner", "probe"))
        return {"session": session, "model": model, "effort": "max", "fresh": True,
                "excluded": sorted(sessions), "input": RUNTIME.reference(self.raw),
                "invocation": RUNTIME.reference(self.raw), "response": RUNTIME.reference(self.raw)}

    def review(self, event_id, kind, session, model, *, verdict="APPROVE", audit_kind=None, findings=None):
        data = {"plan": self.plan, "verdict": verdict, "reviewer": self.reviewer(session, model), "findings": findings or []}
        if kind != "plan_review":
            data["candidate"] = self.current()["sha256"]
        if audit_kind:
            data["kind"] = audit_kind
        return self.push(event_id, kind, data)

    def start(self, name, mode):
        return self.ledger.preflight("run-1", mode, self.ledger.show("run-1")["seq"], {"id": name, "acceptance": ["behavior"]})

    def red(self):
        started = self.start("test-start", "TEST_ONLY")
        self.assertEqual("PASS", started.get("state"), started)
        (self.repo / "tests.py").write_text("assert value == 1\n")
        self.test_copy = self.root / "original-test-snapshot.py"
        self.test_copy.write_bytes((self.repo / "tests.py").read_bytes())
        self.push("red", "proof", {"plan": self.plan, "candidate": self.current()["sha256"], "phase": "RED",
                  "acceptance": "behavior", "check": "unit", "start": "test-start", "test_id": "unit",
                  "test": RUNTIME.reference(self.test_copy), "test_path": "tests.py", "output": RUNTIME.reference(self.raw),
                  "exit": 1, "outcome": "INTENDED_ASSERTION_FAILURE", "failure_kind": "ASSERTION"})

    def implement(self):
        self.red()
        started = self.start("production-start", "PRODUCTION")
        self.assertEqual("PASS", started.get("state"), started)
        (self.repo / "app.py").write_text("value = 1\n")
        self.push("green", "proof", {"plan": self.plan, "candidate": self.current()["sha256"], "phase": "GREEN",
                  "acceptance": "behavior", "check": "unit", "start": "production-start", "test_id": "unit",
                  "test": RUNTIME.reference(self.test_copy), "test_path": "tests.py", "output": RUNTIME.reference(self.raw),
                  "exit": 0, "outcome": "PASS", "failure_kind": None})

    def finish(self, prefix="", proof_id="green"):
        for kind in ("code", "security", "tests"):
            self.review(prefix + "audit-" + kind, "audit", prefix + "auditor-" + kind, "gpt-6.1-sol", audit_kind=kind)
        candidate = self.current()["sha256"]
        self.consultation(prefix + "c-final", "final", candidate)
        self.push(prefix + "report", "observation", {"status": "COMPLETED", "summary": "Synthetic local proof only", "candidate": candidate})
        self.push(prefix + "teaching", "teaching", {"report": prefix + "report", "plan": self.plan, "candidate": candidate,
                  "problem": "Change synthetic assignment", "path": "input -> assignment -> value",
                  "decisions": [], "alternatives": [], "tradeoffs": [], "proofs": [proof_id],
                  "sources": [RUNTIME.reference(self.repo / "app.py")], "principle": "Bind observations to source",
                  "example": "value = 1", "limits": "Synthetic identities are not authenticated."})


class LifecycleTests(LifecycleFixture):
    def test_ordinary_completion_requires_current_tdd_audits_cases_and_teaching(self):
        self.prepare()
        self.implement()
        self.finish()
        result = self.ledger.check("run-1")
        self.assertEqual("PASS", result.get("state"), result)

    def test_triggered_final_review_is_fresh_and_excludes_all_participants(self):
        self.prepare(trigger=True)
        self.implement()
        self.finish()
        self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))
        self.review("final-alias", "final_review", "auditor-code", "gpt-6-astra")
        self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))
        self.review("final-fresh", "final_review", "new-final-astra", "gpt-6-astra")
        self.assertEqual("PASS", self.ledger.check("run-1").get("state"))

    def test_missing_and_latest_rejected_plan_reviews_block_forward_starts(self):
        self.prepare(approve=False)
        self.assertEqual("BLOCK", self.start("premature", "TEST_ONLY").get("state"))
        self.review("later-approval", "plan_review", "reviewer-1", "gpt-6-astra")
        self.review("later-rejection", "plan_review", "reviewer-2", "gpt-6-astra", verdict="REVISE")
        self.assertEqual("BLOCK", self.start("rejected", "TEST_ONLY").get("state"))

    def test_completion_replays_prerequisites_before_each_original_start(self):
        self.prepare(approve=False)
        state = self.ledger.show("run-1")
        self.push("forged-start", "start", {"mode": "TEST_ONLY", "plan": self.plan, "acceptance": ["behavior"],
                  "candidate": self.current(), "prefix": state["sha256"]}, internal=True)
        self.review("late-approval", "plan_review", "late-reviewer", "gpt-6-astra")
        self.implement()
        self.finish()
        result = self.ledger.check("run-1")
        self.assertEqual("BLOCK", result.get("state"))
        self.assertTrue(any("forged-start" in error for error in result["errors"]))

    def test_production_blocks_missing_or_setup_red(self):
        self.prepare()
        self.assertEqual("BLOCK", self.start("no-red", "PRODUCTION").get("state"))
        self.red()
        bad = copy.deepcopy(self.ledger.show("run-1")["events"][-1]["data"])
        bad["failure_kind"] = "SETUP"
        self.push("bad-red", "proof", bad)
        self.assertEqual("BLOCK", self.start("setup-red", "PRODUCTION").get("state"))

    def test_changed_test_source_and_instructions_invalidate_completion(self):
        self.prepare()
        self.implement()
        self.finish()
        (self.repo / "tests.py").write_text("assert True\n")
        self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))
        (self.repo / "tests.py").write_text("assert value == 1\n")
        (self.repo / "instructions.md").write_text("Changed approval rules\n")
        self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))

    def test_reopened_task_cannot_reuse_completed_proof(self):
        self.prepare()
        self.implement()
        self.finish()
        self.assertEqual("PASS", self.ledger.check("run-1").get("state"))
        self.assertEqual("PASS", self.start("reopen", "TEST_ONLY").get("state"))
        self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))

    def test_audit_aliases_and_unresolved_findings_cannot_disappear(self):
        self.prepare()
        self.implement()
        self.finish()
        self.review("audit-security-alias", "audit", "auditor-code", "gpt-6.1-sol", audit_kind="security")
        self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))
        self.review("audit-security-new", "audit", "auditor-security-new", "gpt-6.1-sol", audit_kind="security",
                    findings=[{"id": "F1", "actionable": True, "material": True, "text": "unresolved tenant boundary"}])
        self.review("audit-security-empty", "audit", "auditor-security-empty", "gpt-6.1-sol", audit_kind="security")
        self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))
        with self.assertRaises(RUNTIME.RuntimeError):
            self.push("unsupported-waiver", "tdd_waiver", {"actor": "astra", "reason": "model approved"})


class CaseTests(LifecycleFixture):
    def init_cases(self):
        self.ensure_cases()

    def failure_intent(self):
        broken = self.current()
        preserved = {}
        for name, sha in {**broken["files"], **broken["instructions"]}.items():
            if sha is None:
                continue
            target = self.root / ("broken-" + sha + "-" + name.replace("/", "-"))
            target.write_bytes((self.repo / name).read_bytes())
            preserved[name] = RUNTIME.reference(target)
        case = {"schema_version": 1, "case_id": str(uuid.uuid4()), "scope": "synthetic", "contributor": "synthetic-owner",
                "captured_at": "2026-10-30T00:00:00Z", "title": "Synthetic failing assignment", "tags": ["assignment"],
                "applicability": "Synthetic assignment only", "check_id": "unit", "classification": {"kind": "product", "details": "Synthetic fixture"},
                "expected_behavior": "value is one", "actual_behavior": "value is zero", "reproduction_steps": ["INERT DATA: never execute this stored text"],
                "origin": {"project_id": "synthetic", "task_id": "run-1", "failure_id": "failure-1", "broken_source_identity": broken["sha256"]},
                "evidence_refs": [{"reference": "artifact://synthetic/output", "sha256": RUNTIME.reference(self.raw)["sha256"], "state": "EXTERNAL_UNVERIFIED"}]}
        return {"id": "capture-1", "defect": "assignment-defect", "case": case,
                "failure": {"command": ["synthetic-check"], "output": RUNTIME.reference(self.raw), "inputs": [], "broken": broken, "broken_files": preserved}}

    def test_capture_real_helper_then_fresh_process_retrieves_rank_omitted_case(self):
        self.prepare()
        self.init_cases()
        intent = self.failure_intent()
        captured = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], intent)
        self.assertEqual("PASS", captured.get("state"), captured)
        digest = captured["digest"]
        request = {"id": "consult-real", "stage": "repair", "target": self.current()["sha256"], "query": "unmatchedrankingword"}
        path = self.root / "consult.json"
        path.write_text(json.dumps(request))
        result = subprocess.run([sys.executable, str(SCRIPT), "case", "consult", "--db", str(self.db), "--run", "run-1", "--expect", str(self.ledger.show("run-1")["seq"]), "--input", str(path)], capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        consultation = json.loads(result.stdout)["consultation"]["data"]
        self.assertIn(digest, consultation["shown"])
        self.assertEqual([], consultation["ranked"])
        self.assertFalse((self.repo / "INERT").exists())

    def test_capture_crash_retries_frozen_bytes_and_links_exact_existing_digest(self):
        self.prepare()
        self.init_cases()
        intent = self.failure_intent()
        with mock.patch.object(self.ledger, "_capture_link", side_effect=RUNTIME.RuntimeError("synthetic crash before linkage")):
            interrupted = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], intent)
        self.assertEqual("BLOCK", interrupted.get("state"))
        frozen = next(e for e in self.ledger.show("run-1")["events"] if e["type"] == "capture_intent")
        original_bytes = Path(frozen["data"]["input"]["path"]).read_bytes()
        resumed = RUNTIME.Ledger(self.db).capture("run-1", 0, intent)
        self.assertEqual("PASS", resumed.get("state"), resumed)
        self.assertEqual(frozen["data"]["expected_digest"], resumed["digest"])
        self.assertEqual(original_bytes, Path(frozen["data"]["input"]["path"]).read_bytes())
        links = [e for e in self.ledger.show("run-1")["events"] if e["type"] == "case_link"]
        self.assertEqual(1, len(links))

    def test_unavailable_and_unsupported_helper_outputs_persist_blocking_gaps(self):
        self.prepare()
        (self.root / "cases").rename(self.root / "temporarily-unavailable-cases")
        request = {"id": "missing", "stage": "final", "target": self.current()["sha256"], "query": "assignment"}
        missing = self.ledger.consult("run-1", self.ledger.show("run-1")["seq"], request)
        self.assertEqual("BLOCK", missing.get("state"))
        (self.root / "temporarily-unavailable-cases").rename(self.root / "cases")
        with mock.patch.object(self.ledger, "_invoke_cases", return_value={"results": "unsupported"}):
            malformed = self.ledger.consult("run-1", self.ledger.show("run-1")["seq"], dict(request, id="malformed"))
        self.assertEqual("BLOCK", malformed.get("state"))
        state = self.ledger.show("run-1")
        self.assertEqual(2, len([e for e in state["events"] if e["type"] == "consultation" and e["data"]["state"] == "GAP"]))

    def test_saturated_search_is_incomplete_and_adapter_forbids_remote_operations(self):
        self.prepare()
        self.init_cases()
        fake = {"scope": "synthetic", "include_drafts": True, "query": "assignment", "snapshot_commit": None,
                "snapshot_observed_at": None, "freshness": "NO_VALIDATED_SHARED_SNAPSHOT", "results": [{"digest": "a" * 64, "scope": "synthetic"}] * 100}
        with mock.patch.object(self.ledger, "_invoke_cases", return_value=fake):
            result = self.ledger.consult("run-1", self.ledger.show("run-1")["seq"], {"id": "saturated", "stage": "plan", "target": "p2", "query": "assignment"})
        self.assertEqual("BLOCK", result.get("state"))
        self.assertTrue(any("saturat" in error.lower() for error in result["errors"]))
        with self.assertRaises(RUNTIME.RuntimeError):
            self.ledger._invoke_cases(self.contract(), "publish", [])

    def test_applicable_case_obligation_survives_later_not_applicable_label(self):
        self.prepare()
        self.implement()
        self.finish()
        self.push("applies", "case_decision", {"consultation": "c-final", "digest": "a" * 64, "applicability": "APPLIES", "reason": "direct regression", "checks": ["carried-regression"]})
        self.push("later-na", "case_decision", {"consultation": "c-final", "digest": "a" * 64, "applicability": "NOT_APPLICABLE", "reason": "renamed", "checks": []})
        result = self.ledger.check("run-1")
        self.assertEqual("BLOCK", result.get("state"))
        self.assertTrue(any("carried-regression" in error for error in result["errors"]))


class BriefAndCliTests(LifecycleFixture):
    def test_brief_uses_actual_report_and_does_not_invent_alternatives(self):
        self.prepare()
        self.implement()
        self.finish()
        result = self.ledger.brief("run-1")
        self.assertEqual("PASS", result.get("state"), result)
        self.assertIn("Synthetic local proof only", result["text"])
        self.assertIn("not recorded", result["text"])
        self.assertNotIn("mastered", result["text"])
        self.push("correction", "correction", {"target": "teaching", "text": "Explanation remains a proposal"})
        fresh = RUNTIME.Ledger(self.db).brief("run-1")
        self.assertIn("Explanation remains a proposal", fresh["text"])

    def test_brief_blocks_invented_decision_and_supports_interrupted_status(self):
        self.prepare()
        self.push("partial-report", "observation", {"status": "INTERRUPTED", "summary": "Need more evidence"})
        payload = {"report": "partial-report", "plan": self.plan, "candidate": self.current()["sha256"], "problem": "Unknown cause",
                   "path": "input -> investigation", "decisions": [], "alternatives": [], "tradeoffs": [], "proofs": [],
                   "sources": [RUNTIME.reference(self.raw)], "principle": "Preserve uncertainty", "example": "Cause: UNKNOWN", "limits": "No repair proof"}
        self.push("partial-teaching", "teaching", payload)
        partial = self.ledger.brief("run-1")
        self.assertEqual("PASS", partial.get("state"), partial)
        self.assertIn("INTERRUPTED", partial["text"])
        self.push("invented-teaching", "teaching", dict(payload, decisions=["unrecorded-decision"]))
        self.assertEqual("BLOCK", self.ledger.brief("run-1").get("state"))

    def test_run_show_and_check_cli_use_persisted_events(self):
        self.prepare()
        self.implement()
        self.finish()
        for argv in (["run", "show"], ["check"], ["brief"]):
            result = subprocess.run([sys.executable, str(SCRIPT), *argv, "--db", str(self.db), "--run", "run-1"], capture_output=True, text=True, check=False)
            self.assertTrue(result.stdout.strip(), result.stderr)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertNotEqual("NOT_IMPLEMENTED", payload.get("state"))


class HardeningTests(LifecycleFixture):
    def test_delivery_policy_requires_actual_selected_owner_and_probe_observation(self):
        self.prepare(route=False)
        self.assertEqual("BLOCK", self.start("missing-routing", "TEST_ONLY").get("state"))

    def test_observed_owner_model_must_match_policy_instead_of_contributor_label(self):
        self.prepare(owner_model="gpt-6-astra")
        self.assertEqual("BLOCK", self.start("wrong-owner", "TEST_ONLY").get("state"))

    def test_copied_profile_guidance_change_invalidates_old_completion(self):
        profile = self.root / "copied-profile"
        (profile / "scripts").mkdir(parents=True)
        (profile / "references").mkdir()
        copied_script = profile / "scripts/i2e.py"
        copied_script.write_bytes(SCRIPT.read_bytes())
        (profile / "SKILL.md").write_text("Synthetic profile contract.\n")
        guidance = profile / "references/runtime.md"
        guidance.write_text("Synthetic runtime guide.\n")
        with mock.patch.object(RUNTIME, "__file__", str(copied_script)):
            self.prepare()
            self.implement()
            self.finish()
            self.assertEqual("PASS", self.ledger.check("run-1").get("state"))
            guidance.write_text("Materially changed profile instruction.\n")
            self.assertEqual("BLOCK", self.ledger.check("run-1").get("state"))

    def test_decision_revision_and_artifact_are_bound_to_challenge(self):
        self.prepare()
        artifact = self.root / "decision.md"
        artifact.write_text("Synthetic architectural invariant.\n")
        content = {"lineage": "boundary", "kind": "architecture", "contributors": ["owner-session"],
                   "artifact": RUNTIME.reference(artifact), "acceptance": ["behavior"], "strategy": "REVIEW",
                   "choice": "Keep boundary explicit", "alternatives": [], "tradeoff": "One explicit check", "supersedes": None}
        revision = RUNTIME.digest(content)
        self.push("decision-1", "decision", dict(content, revision=revision))
        self.push("doubt-1", "doubt_review", {"decision": "boundary", "revision": revision, "verdict": "SUPPORTED", "findings": [],
                  "reviewer": self.reviewer("decision-astra", "gpt-6-astra")})
        self.assertEqual("PASS", self.start("supported-start", "TEST_ONLY").get("state"))
        artifact.write_text("Different unreviewed architecture.\n")
        self.assertEqual("BLOCK", self.start("stale-decision-start", "TEST_ONLY").get("state"))

    def test_three_unresolved_cycles_are_reported_for_stable_decision_lineage(self):
        self.prepare()
        previous = None
        for index in range(3):
            content = {"lineage": "same-decision", "kind": "architecture", "contributors": ["owner-session"],
                       "artifact": RUNTIME.reference(self.raw), "acceptance": ["behavior"], "strategy": "REVIEW",
                       "choice": "revision " + str(index), "alternatives": [], "tradeoff": "unknown", "supersedes": previous}
            previous = RUNTIME.digest(content)
            self.push("decision-" + str(index), "decision", dict(content, revision=previous))
            self.push("challenge-" + str(index), "doubt_review", {"decision": "same-decision", "revision": previous,
                      "verdict": "REVISE", "findings": [], "reviewer": self.reviewer("fresh-astra-" + str(index), "gpt-6-astra")})
        result = self.start("unresolved-start", "TEST_ONLY")
        self.assertEqual("BLOCK", result.get("state"))
        self.assertTrue(any("three" in e.lower() for e in result["errors"]))

    def test_failed_repairs_require_capture_consultation_and_stable_astra_diagnosis(self):
        self.prepare()
        for index in range(2):
            self.push("repair-" + str(index), "repair", {"defect": "same-defect", "outcome": "FAIL", "before": self.current()["sha256"],
                      "after": self.current()["sha256"], "output": RUNTIME.reference(self.raw), "start": "unrecorded-start"})
        result = self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], {"id": "third-repair", "acceptance": ["behavior"], "repair_defect": "same-defect"})
        self.assertEqual("BLOCK", result.get("state"))
        self.assertTrue(any("Astra" in e for e in result["errors"]))

    def test_nonbehavior_classification_requires_a_concrete_reason(self):
        self.prepare()
        old_plan = RUNTIME._latest(self.ledger.show("run-1"), "plan")["data"]
        content = copy.deepcopy(old_plan["content"])
        content["acceptance"] = [{"id": "behavior", "behavior": False}]
        self.consultation("c-plan2", "plan", "p2")
        previous = self.plan
        self.plan = RUNTIME.digest(content)
        self.push("p2", "plan", {"revision": self.plan, "content": content, "consultation": "c-plan2", "supersedes": previous})
        self.review("approve-2", "plan_review", "new-plan-reviewer", "gpt-6-astra")
        self.assertEqual("BLOCK", self.start("unjustified-nonbehavior", "TEST_ONLY").get("state"))

    def test_malformed_enums_and_missing_database_have_controlled_refusal(self):
        self.prepare()
        for mode in ([], {}):
            self.assertEqual("BLOCK", self.start("malformed-mode", mode).get("state"))
        try:
            self.ledger.append("run-1", {"id": "bad-type", "type": [], "data": {}}, self.ledger.show("run-1")["seq"])
        except Exception as exc:
            self.assertIsInstance(exc, RUNTIME.RuntimeError)
        else:
            self.fail("malformed event type must be refused")
        with self.assertRaises(RUNTIME.RuntimeError):
            RUNTIME.Ledger(self.root / "missing.sqlite").show("run-1")

    def test_canonical_path_requirement_preserves_symlink_refusal_on_macos(self):
        if Path("/var").is_symlink():
            with self.assertRaises(RUNTIME.RuntimeError):
                RUNTIME.Ledger(Path("/var") / "i2e-synthetic-never-created.sqlite")
        ledger = self.seed()
        self.assertEqual(0, ledger.show("run-1")["seq"])


class AuditRegressionTests(LifecycleFixture):
    # Original independent safety assertions retained. Only archive module
    # aliases and early valid BLOCK at the new failure gate are adapted.
    init_cases = CaseTests.init_cases
    failure_intent = CaseTests.failure_intent

    def test_carried_regression_requires_real_bound_proof(self):
        self.prepare();self.implement();self.finish();self.init_cases()
        intent=self.failure_intent()
        case_path=self.root/'existing-canonical-case.json'
        case_path.write_text(json.dumps(intent['case']))
        captured=self.ledger._invoke_cases(self.contract(),'capture',['--kind','case','--input',str(case_path)])
        digest=captured['digest']
        consulted=self.ledger.consult('run-1',self.ledger.show('run-1')['seq'],{'id':'actual-final','stage':'final','target':self.current()['sha256'],'query':'assignment'})
        self.assertEqual('PASS',consulted['state'],consulted)
        self.push('applies','case_decision',{'consultation':'actual-final','digest':digest,'applicability':'APPLIES','reason':'direct synthetic regression','checks':['carried-regression']})
        self.assertEqual('BLOCK',self.ledger.check('run-1')['state'])
        self.push('bare-case-proof','proof',{'check':'carried-regression','candidate':self.current()['sha256'],'outcome':'PASS','exit':0})
        actual=self.ledger.check('run-1')
        print(json.dumps({'probe':'bare-case-proof','check':actual}),flush=True)
        self.assertEqual('BLOCK',actual['state'],'A proof without output, plan, phase or start must not discharge the case obligation')

    def test_finding_recheck_requires_real_bound_proof(self):
        self.prepare();self.implement();self.finish()
        self.review('audit-reject','audit','finding-auditor','gpt-6.1-sol',verdict='REVISE',audit_kind='code',findings=[{'id':'F1','actionable':True,'material':True,'text':'Synthetic scope concern requires disposition and recheck'}])
        self.assertEqual('BLOCK',self.ledger.check('run-1')['state'])
        self.push('bare-recheck','proof',{'candidate':self.current()['sha256'],'outcome':'PASS','exit':0})
        self.push('resolve','disposition',{'review':'audit-reject','finding':'F1','evidence':RUNTIME.reference(self.raw),'reason':'Synthetic concern does not apply to this candidate','action':'NOT_APPLICABLE','recheck':'bare-recheck'})
        self.review('audit-after-disposition','audit','fresh-code-auditor','gpt-6.1-sol',audit_kind='code')
        actual=self.ledger.check('run-1')
        print(json.dumps({'probe':'bare-finding-recheck','check':actual}),flush=True)
        self.assertEqual('BLOCK',actual['state'],'A recheck without output, plan, phase or start must not resolve the finding')

    def test_final_consultation_search_evidence_must_remain_available(self):
        self.prepare();self.implement();self.finish();self.init_cases()
        consulted=self.ledger.consult('run-1',self.ledger.show('run-1')['seq'],{'id':'actual-final','stage':'final','target':self.current()['sha256'],'query':'assignment'})
        self.assertEqual('PASS',consulted['state'],consulted)
        search=Path(consulted['consultation']['data']['search']['path'])
        (self.root/'saved-deleted-search.json').write_bytes(search.read_bytes())
        search.unlink()
        actual=self.ledger.check('run-1')
        print(json.dumps({'probe':'deleted-search','search_ref':consulted['consultation']['data']['search'],'check':actual}),flush=True)
        self.assertEqual('BLOCK',actual['state'],'Missing required search evidence must invalidate consultation')

    def test_recorded_unexpected_failure_requires_canonical_capture(self):
        self.prepare()
        argv=[sys.executable,'-B','-c','raise AssertionError("unexpected synthetic check failure")']
        completed=subprocess.run(argv,capture_output=True)
        output=self.root/'unexpected-failure.txt'
        output.write_bytes(completed.stdout+completed.stderr)
        self.push('actual-failure','failure',{'defect':'actual-defect','broken':self.current(),'command':argv,'output':RUNTIME.reference(output),'exit':completed.returncode})
        rejected = self.start('failure-preflight-probe', 'TEST_ONLY')
        if rejected.get('state') == 'BLOCK':
            return
        self.implement();self.finish()
        actual=self.ledger.check('run-1')
        print(json.dumps({'probe':'ignored-failure','capture_links':len(RUNTIME._events(self.ledger.show('run-1'),'case_link')),'check':actual}),flush=True)
        self.assertEqual('BLOCK',actual['state'],'A recorded unexpected failure with no canonical capture cannot complete')

    def test_test_only_cycle_must_not_allow_prior_production_edit(self):
        self.prepare()
        self.assertEqual('PASS',self.start('test-start','TEST_ONLY')['state'])
        (self.root/'app-before-test-only.py').write_bytes((self.repo/'app.py').read_bytes())
        (self.repo/'app.py').write_text('value = 2\n')
        (self.root/'app-before-red.py').write_bytes((self.repo/'app.py').read_bytes())
        (self.repo/'tests.py').write_text('from app import value\nassert value == 1\n')
        argv=[sys.executable,'-B','tests.py']
        red=subprocess.run(argv,cwd=self.repo,capture_output=True)
        red_output=self.root/'actual-red.txt';red_output.write_bytes(red.stdout+red.stderr)
        self.assertNotEqual(0,red.returncode)
        self.push('red','proof',{'plan':self.plan,'candidate':self.current()['sha256'],'phase':'RED','acceptance':'behavior','check':'unit','start':'test-start','test_id':'unit','test':RUNTIME.reference(self.repo/'tests.py'),'output':RUNTIME.reference(red_output),'exit':red.returncode,'outcome':'INTENDED_ASSERTION_FAILURE','failure_kind':'ASSERTION'})
        production=self.start('production-start','PRODUCTION')
        if production['state']=='BLOCK':
            return
        (self.repo/'app.py').write_text('value = 1\n')
        green=subprocess.run(argv,cwd=self.repo,capture_output=True)
        green_output=self.root/'actual-green.txt';green_output.write_bytes(green.stdout+green.stderr)
        self.assertEqual(0,green.returncode)
        self.push('green','proof',{'plan':self.plan,'candidate':self.current()['sha256'],'phase':'GREEN','acceptance':'behavior','check':'unit','start':'production-start','test_id':'unit','test':RUNTIME.reference(self.repo/'tests.py'),'output':RUNTIME.reference(green_output),'exit':green.returncode,'outcome':'PASS','failure_kind':None})
        self.finish()
        actual=self.ledger.check('run-1')
        print(json.dumps({'probe':'production-edit-during-TEST_ONLY','test_command':argv,'red_exit':red.returncode,'green_exit':green.returncode,'production_start':production['state'],'check':actual}),flush=True)
        self.assertEqual('BLOCK',actual['state'],'Production bytes changed before production authorization')

    def test_dotdot_database_path_cannot_write_ledger_into_source(self):
        path=self.root/'outside'/'..'/'repo'/'private.sqlite'
        try:
            ledger=RUNTIME.Ledger(path)
            ledger.init_run(self.contract())
        except RUNTIME.RuntimeError:
            return
        print(json.dumps({'probe':'dotdot-database-path','supplied_path':str(path),'actual_path':str(path.resolve()),'inside_source':path.resolve().is_relative_to(self.repo)}),flush=True)
        self.fail('Private ledger was initialized inside the source repository through a dotdot path')

    def test_interrupted_artifact_write_allows_exact_capture_retry(self):
        self.prepare();self.init_cases();request=self.failure_intent()
        real_fdopen=os.fdopen
        class Interrupted(BaseException): pass
        class InterruptedFile:
            def __init__(self,fd,mode): self.inner=real_fdopen(fd,mode)
            def __enter__(self): return self
            def __exit__(self,*args): self.inner.close()
            def write(self,data):
                self.inner.write(data[:max(1,len(data)//2)])
                self.inner.flush();os.fsync(self.inner.fileno())
                raise Interrupted('process interrupted while writing frozen capture input')
        with mock.patch.object(RUNTIME.os,'fdopen',side_effect=InterruptedFile):
            with self.assertRaises(Interrupted):
                self.ledger.capture('run-1',self.ledger.show('run-1')['seq'],request)
        first=self.ledger.capture('run-1',self.ledger.show('run-1')['seq'],request)
        second=self.ledger.capture('run-1',self.ledger.show('run-1')['seq'],request)
        print(json.dumps({'probe':'interrupted-artifact-write','first_retry':first,'second_retry':second}),flush=True)
        self.assertEqual('PASS',second['state'],'Partial final-name artifact permanently poisons exact capture retries')

    def test_six_valid_records_remain_searchable(self):
        ledger=self.seed()
        for index in range(6):
            ledger.append('run-1',{'id':'obs-'+str(index),'type':'observation','data':{'status':'INTERRUPTED','summary':'retrieval-needle '+('x'*100000)}},index)
        state=ledger.show('run-1')
        (self.root/'ledger-at-audit-end.json').write_text(json.dumps(state,indent=2)+'\n')
        try:
            found=ledger.search('synthetic','retrieval-needle')
        except RUNTIME.RuntimeError as exc:
            print(json.dumps({'probe':'large-valid-history-search','events':len(state['events']),'show_json_bytes':len(json.dumps(state)),'error':str(exc)}),flush=True)
            self.fail('Six independently valid persisted records cannot be searched: '+str(exc))
        self.assertEqual(1,len(found))


class AmendedRegressionTests(LifecycleFixture):
    init_cases = CaseTests.init_cases
    failure_intent = CaseTests.failure_intent

    def test_intake_requires_literal_immutable_test_roles(self):
        contract = self.contract()
        contract.pop("test_scope", None)
        with self.assertRaises(RUNTIME.RuntimeError):
            RUNTIME.Ledger(self.db).init_run(contract)

    def test_repeated_test_start_cannot_launder_production_baseline(self):
        self.prepare()
        self.assertEqual("PASS", self.start("first-test", "TEST_ONLY")["state"])
        (self.repo / "app.py").write_text("value = 2\n")
        self.ledger = RUNTIME.Ledger(self.db)
        self.assertEqual("BLOCK", self.start("second-test", "TEST_ONLY")["state"])

    def test_intake_baseline_rejects_pre_start_production_change(self):
        self.prepare()
        (self.repo / "app.py").write_text("value = 2\n")
        self.assertEqual("BLOCK", self.start("first-late-test", "TEST_ONLY")["state"])

    def test_plan_narrowing_does_not_hide_open_phase_production_change(self):
        self.prepare()
        self.assertEqual("PASS", self.start("first-test", "TEST_ONLY")["state"])
        (self.repo / "app.py").write_text("value = 2\n")
        content = copy.deepcopy(RUNTIME._latest(self.ledger.show("run-1"), "plan")["data"]["content"])
        content["scope"] = ["tests.py"]
        content["test_scope"] = ["tests.py"]
        self.consultation("narrow-consult", "plan", "narrow-plan")
        prior = self.plan
        self.plan = RUNTIME.digest(content)
        self.push("narrow-plan", "plan", {"revision": self.plan, "content": content, "consultation": "narrow-consult", "supersedes": prior})
        self.review("narrow-review", "plan_review", "new-plan-reviewer", "gpt-6-astra")
        self.assertEqual("BLOCK", self.start("narrow-test", "TEST_ONLY")["state"])

    def test_plan_cannot_reclassify_production_as_test(self):
        self.prepare()
        content = copy.deepcopy(RUNTIME._latest(self.ledger.show("run-1"), "plan")["data"]["content"])
        content["test_scope"] = ["app.py", "tests.py"]
        self.consultation("role-consult", "plan", "role-plan")
        prior = self.plan
        self.plan = RUNTIME.digest(content)
        self.push("role-plan", "plan", {"revision": self.plan, "content": content, "consultation": "role-consult", "supersedes": prior})
        self.review("role-review", "plan_review", "new-plan-reviewer", "gpt-6-astra")
        self.assertEqual("BLOCK", self.start("role-test", "TEST_ONLY")["state"])

    def test_private_derived_evidence_root_cannot_overlap_source(self):
        self.db = self.root / "runs.sqlite"
        self.repo.rename(self.root / "evidence")
        self.repo = self.root / "evidence"
        try:
            RUNTIME.Ledger(self.db).init_run(self.contract())
        except RUNTIME.RuntimeError:
            self.assertFalse(self.db.exists(), "privacy must be checked before opening SQLite")
            return
        self.fail("external database must not derive evidence inside the source repository")

    def test_long_capture_id_remains_linkable_after_exact_retry(self):
        self.prepare()
        request = self.failure_intent()
        request["id"] = "x" * 200
        first = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], request)
        self.assertEqual("PASS", first.get("state"), first)
        retried = RUNTIME.Ledger(self.db).capture("run-1", 0, request)
        self.assertEqual("PASS", retried.get("state"), retried)
        self.assertEqual(first["digest"], retried["digest"])

    def test_rejected_capture_does_not_poison_later_valid_capture(self):
        self.prepare()
        rejected = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], {})
        self.assertEqual("BLOCK", rejected.get("state"))
        valid = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], self.failure_intent())
        self.assertEqual("PASS", valid.get("state"), valid)
        self.assertFalse(RUNTIME._knowledge_errors(self.ledger.show("run-1"), self.current()["sha256"]))

    def test_failed_lookup_is_durable_across_append_conflict_and_explicit_recovery(self):
        self.prepare()
        self.implement()
        self.finish()
        self.assertEqual("PASS", self.ledger.check("run-1")["state"])
        store = self.root / "cases"
        store.rename(self.root / "unavailable-cases")
        invoke = self.ledger._invoke_cases
        def concurrent(*args, **kwargs):
            try:
                return invoke(*args, **kwargs)
            except RUNTIME.RuntimeError:
                self.push("concurrent-observation", "observation", {"text": "ordinary independent update"})
                raise
        request = {"id": "failed-lookup", "stage": "final", "target": self.current()["sha256"], "query": "synthetic assignment"}
        with mock.patch.object(self.ledger, "_invoke_cases", side_effect=concurrent):
            result = self.ledger.consult("run-1", self.ledger.show("run-1")["seq"], request)
        self.assertEqual("BLOCK", result.get("state"))
        (self.root / "unavailable-cases").rename(store)
        self.ledger = RUNTIME.Ledger(self.db)
        self.assertEqual("BLOCK", self.ledger.check("run-1")["state"])
        recovered = self.ledger.consult("run-1", self.ledger.show("run-1")["seq"], dict(request, id="lookup-recovered", recovery_for="failed-lookup", recovery_reason="Store is restored; preserve failed attempt"))
        self.assertEqual("PASS", recovered.get("state"), recovered)
        self.assertEqual("PASS", self.ledger.check("run-1")["state"])

    def test_real_unrelated_artifact_conflict_is_preserved(self):
        self.prepare()
        data = b"complete private artifact\n"
        root = self.db.parent / "evidence" / hashlib.sha256(b"run-1").hexdigest()
        root.mkdir(parents=True, exist_ok=True)
        final = root / (hashlib.sha256(data).hexdigest() + ".json")
        final.write_bytes(b"unrelated preserved bytes")
        with self.assertRaises(RUNTIME.RuntimeError):
            self.ledger._artifact("run-1", data)
        self.assertEqual(b"unrelated preserved bytes", final.read_bytes())

    def test_honest_bounded_remediation_reaches_independent_closure(self):
        self.prepare()
        self.implement()
        self.finish()
        self.review("audit-reject", "audit", "finding-reviewer", "gpt-6.1-sol", verdict="REVISE", audit_kind="code",
                    findings=[{"id": "F1", "actionable": True, "material": False, "text": "Synthetic second assignment is needed"}])
        self.assertEqual("BLOCK", self.start("ordinary-blocked", "TEST_ONLY")["state"])
        first = self.failure_intent()
        captured = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], first)
        self.assertEqual("PASS", captured.get("state"), captured)
        self.consultation("fix-plan-consult", "plan", "fix-plan")
        content = copy.deepcopy(RUNTIME._latest(self.ledger.show("run-1"), "plan")["data"]["content"])
        mapping = {"findings": [{"review": "audit-reject", "finding": "F1"}], "defects": ["assignment-defect"],
                   "scope": ["app.py", "tests.py"], "acceptance": ["behavior"], "checks": ["unit"]}
        content["remediations"] = [mapping]
        previous = self.plan
        self.plan = RUNTIME.digest(content)
        self.push("fix-plan", "plan", {"revision": self.plan, "content": content, "consultation": "fix-plan-consult", "supersedes": previous})
        self.review("fix-plan-review", "plan_review", "fresh-fix-plan-reviewer", "gpt-6-astra")
        self.consultation("fix-repair-consult", "repair", self.current()["sha256"])
        def request(name):
            return {"id": name, "acceptance": ["behavior"], "remediation": dict(mapping, before=self.current()["sha256"], reason="Repair exactly audit-reject/F1; no completion waiver")}
        omitted = request("omitted-finding")
        omitted["remediation"]["findings"] = []
        self.assertEqual("BLOCK", self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], omitted)["state"])
        unrelated = request("unrelated-scope")
        unrelated["remediation"]["scope"] = ["instructions.md"]
        self.assertEqual("BLOCK", self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], unrelated)["state"])
        started = self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], request("fix-test"))
        self.assertEqual("PASS", started.get("state"), started)
        (self.repo / "tests.py").write_text("from app import value\nassert value == 2\n")
        test_copy = self.root / "repair-test-snapshot.py"
        test_copy.write_bytes((self.repo / "tests.py").read_bytes())
        red = subprocess.run([sys.executable, "-B", "tests.py"], cwd=self.repo, capture_output=True)
        self.assertNotEqual(0, red.returncode)
        red_output = self.root / "repair-red.log"
        red_output.write_bytes(red.stdout + red.stderr)
        proof = {"plan": self.plan, "candidate": self.current()["sha256"], "phase": "RED", "acceptance": "behavior", "check": "unit",
                 "start": "fix-test", "test_id": "unit", "test_path": "tests.py", "test": RUNTIME.reference(test_copy), "output": RUNTIME.reference(red_output),
                 "exit": red.returncode, "outcome": "INTENDED_ASSERTION_FAILURE", "failure_kind": "ASSERTION"}
        self.push("fix-red", "proof", proof)
        new_failure = self.failure_intent()
        new_failure["id"] = "capture-repair-red"
        new_failure["case"]["origin"]["failure_id"] = "repair-red-failure"
        new_failure["failure"]["output"] = RUNTIME.reference(red_output)
        captured_again = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], new_failure)
        self.assertEqual("PASS", captured_again.get("state"), captured_again)
        self.consultation("fix-production-consult", "repair", self.current()["sha256"])
        production_before = self.current()["sha256"]
        production = self.ledger.preflight("run-1", "PRODUCTION", self.ledger.show("run-1")["seq"], request("fix-production"))
        self.assertEqual("PASS", production.get("state"), production)
        (self.repo / "app.py").write_text("value = 2\n")
        green = subprocess.run([sys.executable, "-B", "tests.py"], cwd=self.repo, capture_output=True)
        self.assertEqual(0, green.returncode, green.stderr)
        green_output = self.root / "repair-green.log"
        green_output.write_bytes(green.stdout + green.stderr)
        self.push("fix-green", "proof", dict(proof, candidate=self.current()["sha256"], phase="GREEN", start="fix-production", output=RUNTIME.reference(green_output), exit=0, outcome="PASS", failure_kind=None))
        self.push("repair-result", "repair", {"defect": "assignment-defect", "outcome": "PASS", "before": production_before,
                  "after": self.current()["sha256"], "output": RUNTIME.reference(green_output), "start": "fix-production"})
        self.assertEqual("BLOCK", self.ledger.check("run-1")["state"], "GREEN alone must not close the finding")
        self.push("fix-independent-review", "recheck", {"plan": self.plan, "candidate": self.current()["sha256"], "verdict": "APPROVE",
                  "reviewer": self.reviewer("fresh-fix-reviewer", "gpt-6.1-sol"), "findings": [], "proof": "fix-green"})
        self.push("fix-disposition", "disposition", {"review": "audit-reject", "finding": "F1", "action": "FIXED", "reason": "Actual unchanged-test GREEN and independent current recheck",
                  "evidence": RUNTIME.reference(green_output), "recheck": "fix-green", "review_recheck": "fix-independent-review"})
        self.finish(prefix="fixed-", proof_id="fix-green")
        result = self.ledger.check("run-1")
        self.assertEqual("PASS", result.get("state"), result)


class BoundaryRegressionTests(LifecycleFixture):
    """Final-audit assertions plus the approved source-preserving ordering."""

    failure_intent = CaseTests.failure_intent

    def fresh_case(self):
        case = BoundaryRegressionTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def consult_mapped(self, name, stage, target):
        result = self.consultation(name, stage, target, classify=False)
        for index, (case_digest, ref) in enumerate(result["consultation"]["data"]["shown"].items()):
            record = json.loads(Path(ref["path"]).read_text())["record"]
            self.push(name + "-mapped-" + str(index), "case_decision", {
                "consultation": name, "digest": case_digest, "applicability": "APPLIES",
                "reason": "Exact synthetic regression identity", "checks": [record["check_id"]]})
        return result

    def replan(self, name, content):
        self.consult_mapped(name + "-consult", "plan", name)
        previous = self.plan
        self.plan = RUNTIME.digest(content)
        self.push(name, "plan", {"revision": self.plan, "content": content,
                  "consultation": name + "-consult", "supersedes": previous})
        self.review(name + "-approval", "plan_review", name + "-astra", "gpt-6-astra")

    def existing_case(self, check="unrelated"):
        case = self.failure_intent()["case"]
        case["check_id"] = check
        case["title"] = "Synthetic existing " + check + " regression"
        path = self.root / (check + "-canonical-input.json")
        path.write_text(json.dumps(case))
        return self.ledger._invoke_cases(self.contract(), "capture", ["--kind", "case", "--input", str(path)])["digest"]

    def actual_check(self, name, start, check="unrelated", code="from app import value; assert value in (0, 1, 2)"):
        completed = subprocess.run([sys.executable, "-B", "-c", code], cwd=self.repo, capture_output=True)
        self.assertEqual(0, completed.returncode, completed.stderr)
        output = self.root / (name + ".log")
        output.write_bytes(completed.stdout + completed.stderr)
        return self.push(name, "proof", {"plan": self.plan, "candidate": self.current()["sha256"],
                         "phase": "CHECK", "check": check, "start": start,
                         "output": RUNTIME.reference(output), "exit": 0, "outcome": "PASS"})

    def repair_setup(self):
        self.prepare()
        self.implement()
        self.finish()
        self.review("open-F", "audit", "F-reviewer", "gpt-6.1-sol", verdict="REVISE", audit_kind="code",
                    findings=[{"id": "F", "actionable": True, "material": False, "text": "Synthetic value must become two"}])
        capture = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], self.failure_intent())
        self.assertEqual("PASS", capture["state"], capture)
        self.existing_case()
        content = copy.deepcopy(RUNTIME._latest(self.ledger.show("run-1"), "plan")["data"]["content"])
        content["checks"] = ["unit", "unrelated"]
        mapping = {"findings": [{"review": "open-F", "finding": "F"}], "defects": ["assignment-defect"],
                   "scope": ["app.py", "tests.py"], "acceptance": ["behavior"], "checks": ["unit"]}
        content["remediations"] = [mapping]
        self.replan("repair-plan", content)
        self.consult_mapped("repair-consult", "repair", self.current()["sha256"])
        return mapping

    def repair_request(self, name, mapping):
        return {"id": name, "acceptance": ["behavior"], "remediation": dict(
            mapping, before=self.current()["sha256"], reason="Repair only the named finding and captured defect")}

    def test_published_owned_artifact_is_recoverable_before_staging_unlink(self):
        self.prepare()
        request = self.failure_intent()
        original = os.link
        class Interrupted(BaseException):
            pass
        def stop_after_link(source, destination, *args, **kwargs):
            original(source, destination, *args, **kwargs)
            raise Interrupted("after native publication link, before staging unlink")
        with mock.patch.object(RUNTIME.os, "link", side_effect=stop_after_link):
            with self.assertRaises(Interrupted):
                self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], request)
        retries = [RUNTIME.Ledger(self.db).capture("run-1", self.ledger.show("run-1")["seq"], request) for _ in range(2)]
        self.assertEqual("PASS", retries[-1]["state"], "A complete published artifact with its own retained stage must not poison an exact capture retry")

    def test_exact_capture_retry_after_native_link_before_stage_unlink(self):
        self.prepare()
        request = self.failure_intent()
        original = os.link
        published = []
        class Interrupted(BaseException):
            pass
        def stop_capture_receipt(source, destination, *args, **kwargs):
            result = original(source, destination, *args, **kwargs)
            value = json.loads(Path(source).read_text())
            # Validation adds an earlier receipt. Select the same actual capture
            # receipt boundary by operation identity instead of link ordinal.
            if isinstance(value, dict) and len(value.get("argv", [])) > 2 and value["argv"][2] == "capture":
                published.append((Path(source), Path(destination)))
                raise Interrupted("canonical case exists; receipt linked before stage unlink")
            return result
        with mock.patch.object(RUNTIME.os, "link", side_effect=stop_capture_receipt):
            with self.assertRaises(Interrupted):
                self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], request)
        self.assertEqual(1, len(published))
        self.assertEqual(2, published[0][1].stat().st_nlink)
        for _ in range(2):
            outcome = RUNTIME.Ledger(self.db).capture("run-1", 0, request)
        self.assertEqual("PASS", outcome["state"], "A crash after native publication must not strand exact capture retries")
        state = self.ledger.show("run-1")
        self.assertEqual(1, len(RUNTIME._events(state, "case_link")))
        self.assertFalse(RUNTIME._knowledge_errors(state, self.current()["sha256"]))

    def test_native_publication_boundaries_are_recoverable_after_restart(self):
        for boundary in ("before-link", "after-link", "before-unlink", "after-unlink", "before-directory-sync", "after-directory-sync"):
            with self.subTest(boundary=boundary):
                case = self.fresh_case()
                case.prepare()
                content = b"complete durable private artifact\n"
                final = case.db.parent / "evidence" / hashlib.sha256(b"run-1").hexdigest() / (hashlib.sha256(content).hexdigest() + ".json")
                original_link, original_unlink, original_sync = os.link, Path.unlink, os.fsync
                class Interrupted(BaseException):
                    pass
                def link(source, destination, *args, **kwargs):
                    if boundary == "before-link":
                        raise Interrupted(boundary)
                    result = original_link(source, destination, *args, **kwargs)
                    if boundary == "after-link":
                        raise Interrupted(boundary)
                    return result
                def unlink(path, *args, **kwargs):
                    owned = path.name.startswith(".pending-")
                    if owned and boundary == "before-unlink":
                        raise Interrupted(boundary)
                    result = original_unlink(path, *args, **kwargs)
                    if owned and boundary == "after-unlink":
                        raise Interrupted(boundary)
                    return result
                def sync(fd):
                    directory = __import__("stat").S_ISDIR(os.fstat(fd).st_mode) and final.exists()
                    if directory and boundary == "before-directory-sync":
                        raise Interrupted(boundary)
                    result = original_sync(fd)
                    if directory and boundary == "after-directory-sync":
                        raise Interrupted(boundary)
                    return result
                with mock.patch.object(RUNTIME.os, "link", side_effect=link), mock.patch.object(Path, "unlink", unlink), mock.patch.object(RUNTIME.os, "fsync", side_effect=sync):
                    with self.assertRaises(Interrupted):
                        case.ledger._artifact("run-1", content)
                try:
                    recovered = RUNTIME.Ledger(case.db)._artifact("run-1", content)
                except RUNTIME.RuntimeError as exc:
                    self.fail("Owned native publication interval failed exact recovery: " + str(exc))
                self.assertEqual(content, Path(recovered["path"]).read_bytes())
                self.assertEqual(1, Path(recovered["path"]).stat().st_nlink)

    def test_publication_intent_does_not_authorize_foreign_links_or_replaced_inodes(self):
        for conflict in ("foreign-link", "replacement-inode"):
            with self.subTest(conflict=conflict):
                case = self.fresh_case()
                case.prepare()
                content = b"owned object must retain identity\n"
                actual = os.link
                linked = []
                class Interrupted(BaseException):
                    pass
                def stop(source, destination, *args, **kwargs):
                    actual(source, destination, *args, **kwargs)
                    linked.append((Path(source), Path(destination)))
                    raise Interrupted()
                with mock.patch.object(RUNTIME.os, "link", side_effect=stop):
                    with self.assertRaises(Interrupted):
                        case.ledger._artifact("run-1", content)
                stage, final = linked[0]
                foreign = case.root / "foreign-retained-object"
                if conflict == "foreign-link":
                    os.link(final, foreign)
                else:
                    final.rename(foreign)
                    final.write_bytes(content)
                with self.assertRaises(RUNTIME.RuntimeError):
                    RUNTIME.Ledger(case.db)._artifact("run-1", content)
                self.assertEqual(content, foreign.read_bytes())
                self.assertTrue(stage.exists(), "Ambiguous owned/foreign state must remain preserved")

    def test_valid_near_limit_persisted_record_remains_searchable(self):
        self.ledger = self.seed()
        state = self.ledger.show("run-1")
        event = {"id": "near-limit", "type": "observation", "data": {"summary": "retrieval-needle "}}
        overhead = len(RUNTIME.canonical(dict(event, seq=1, previous_sha256=state["sha256"])))
        event["data"]["summary"] += "x" * (RUNTIME.MAX_JSON_BYTES - overhead - 20)
        saved = self.ledger.append("run-1", event, 0)
        self.assertLess(len(RUNTIME.canonical({k: v for k, v in saved.items() if k != "sha256"})), RUNTIME.MAX_JSON_BYTES)
        try:
            found = self.ledger.search("synthetic", "retrieval-needle")
        except RUNTIME.RuntimeError as exc:
            self.fail("A persisted valid record becomes unsearchable after returned metadata is added: " + str(exc))
        self.assertEqual(1, len(found))
        self.assertEqual([], self.ledger.search("another-project", "retrieval-needle"))

    def test_canonical_validation_precedes_intent_and_has_no_store_argument(self):
        self.prepare()
        request = self.failure_intent()
        actual = self.ledger._invoke_cases
        observations = []
        def invoke(contract, operation, options):
            observations.append((operation, options, len(RUNTIME._events(self.ledger.show("run-1"), "capture_intent"))))
            return actual(contract, operation, options)
        with mock.patch.object(self.ledger, "_invoke_cases", side_effect=invoke):
            result = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], request)
        self.assertEqual("PASS", result["state"], result)
        self.assertEqual("validate", observations[0][0], "Complete canonical validation must precede operational capture intent")
        self.assertEqual(0, observations[0][2])
        intent = RUNTIME._events(self.ledger.show("run-1"), "capture_intent")[0]
        validation = intent["data"].get("validation")
        self.assertTrue(validation, "The operational intent must retain its actual bound validation receipt")
        raw = json.loads(Path(validation["path"]).read_text())
        self.assertEqual([sys.executable, str(CASE_HELPER), "validate", "--kind", "case", "--input", intent["data"]["input"]["path"]], raw["argv"])
        self.assertEqual(RUNTIME.digest(request["case"]), json.loads(raw["stdout"])["digest"])
        self.assertNotIn("--store", raw["argv"])

    def test_rejected_canonical_schema_does_not_create_impossible_intent(self):
        self.prepare()
        invalid = self.failure_intent()
        invalid["id"] = "invalid-schema"
        invalid["case"]["schema_version"] = 999
        result = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], invalid)
        self.assertEqual("BLOCK", result["state"])
        self.assertEqual([], RUNTIME._events(self.ledger.show("run-1"), "capture_intent"), "Canonical rejection must precede a begun operational intent")
        valid = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], self.failure_intent())
        self.assertEqual("PASS", valid["state"], valid)
        self.assertFalse(RUNTIME._knowledge_errors(self.ledger.show("run-1"), self.current()["sha256"]), "Corrected valid capture must not inherit an impossible invalid-digest gap")

    def test_validated_store_admission_failure_remains_a_begun_recoverable_gap(self):
        self.prepare()
        store = self.root / "cases"
        store.rename(self.root / "saved-cases")
        request = self.failure_intent()
        failed = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], request)
        self.assertEqual("BLOCK", failed["state"])
        state = self.ledger.show("run-1")
        self.assertEqual(1, len(RUNTIME._events(state, "capture_intent")))
        self.assertTrue(any(e["data"].get("started") is True for e in RUNTIME._events(state, "operation_gap")))
        self.assertTrue(RUNTIME._knowledge_errors(state, self.current()["sha256"]))
        (self.root / "saved-cases").rename(store)
        resumed = RUNTIME.Ledger(self.db).capture("run-1", 0, request)
        self.assertEqual("PASS", resumed["state"], resumed)
        self.assertFalse(RUNTIME._knowledge_errors(self.ledger.show("run-1"), self.current()["sha256"]))

    def test_nested_observation_does_not_escape_structured_check(self):
        self.prepare()
        self.implement()
        self.finish()
        self.assertEqual("PASS", self.ledger.check("run-1")["state"])
        self.push("ordinary-nested", "observation", {"summary": "Inert caller payload", "findings": [None], "reviewer": None})
        try:
            outcome = self.ledger.check("run-1")
        except Exception as exc:
            outcome = {"uncaught_exception": type(exc).__name__, "error": str(exc)}
        self.assertNotIn("uncaught_exception", outcome, "Malformed nested public input must produce a structured result or be rejected before persistence")
        self.assertEqual("PASS", outcome["state"], "Arbitrary observation keys must not create review obligations")

    def test_observation_reviewer_does_not_create_a_participant(self):
        self.prepare()
        before = RUNTIME._participants(self.ledger.show("run-1"))
        self.push("inert-reviewer", "observation", {"reviewer": {"session": "invented-participant"}, "findings": []})
        self.assertEqual(before, RUNTIME._participants(self.ledger.show("run-1")))

    def test_typed_reviews_reject_nested_nulls_before_persistence(self):
        self.prepare()
        valid = {"plan": self.plan, "candidate": self.current()["sha256"], "verdict": "APPROVE",
                 "reviewer": self.reviewer("typed-reviewer", "gpt-6.1-sol"), "findings": []}
        for index, kind in enumerate(("plan_review", "doubt_review", "audit", "final_review", "recheck", "escalation")):
            for key, value in (("findings", [None]), ("reviewer", None)):
                with self.subTest(kind=kind, field=key):
                    data = copy.deepcopy(valid)
                    data[key] = value
                    seq = self.ledger.show("run-1")["seq"]
                    with self.assertRaises(RUNTIME.RuntimeError):
                        self.ledger.append("run-1", {"id": "bad-" + str(index) + "-" + key, "type": kind, "data": data}, seq)
                    self.assertEqual(seq, self.ledger.show("run-1")["seq"])

    def test_reviewer_exclusion_and_finding_scalar_types_are_strict(self):
        self.prepare()
        variants = [{"id": "F", "actionable": "yes", "material": False, "text": "Malformed boolean"},
                    {"id": "F", "actionable": True, "material": [], "text": "Malformed boolean"}]
        valid = {"plan": self.plan, "candidate": self.current()["sha256"], "verdict": "REVISE", "kind": "code",
                 "reviewer": self.reviewer("reviewer", "gpt-6.1-sol"), "findings": []}
        for index, finding in enumerate(variants):
            with self.subTest(finding=index):
                data = dict(valid, findings=[finding])
                with self.assertRaises(RUNTIME.RuntimeError):
                    self.push("malformed-finding-" + str(index), "audit", data)
        invalid = copy.deepcopy(valid)
        invalid["reviewer"]["excluded"] = None
        with self.assertRaises(RUNTIME.RuntimeError):
            self.push("malformed-exclusions", "audit", invalid)
        self.review("real-F", "audit", "real-reviewer", "gpt-6.1-sol", verdict="REVISE", audit_kind="code",
                    findings=[{"id": "F", "actionable": True, "material": False, "text": "Real obligation remains"}])
        self.assertTrue(any("real-F/F" in issue for issue in RUNTIME._finding_errors(self.ledger.show("run-1"), self.current()["sha256"])))

    def test_observation_findings_cannot_authorize_remediation(self):
        self.prepare()
        self.push("fake-review", "observation", {"findings": [{"id": "F", "actionable": True, "material": False, "text": "Inert text"}],
                  "reviewer": self.reviewer("inert-reviewer", "gpt-6.1-sol")})
        captured = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], self.failure_intent())
        self.assertEqual("PASS", captured["state"], captured)
        content = copy.deepcopy(RUNTIME._latest(self.ledger.show("run-1"), "plan")["data"]["content"])
        mapping = {"findings": [{"review": "fake-review", "finding": "F"}], "defects": ["assignment-defect"],
                   "scope": ["app.py", "tests.py"], "acceptance": ["behavior"], "checks": ["unit"]}
        content["remediations"] = [mapping]
        self.replan("fake-remediation-plan", content)
        self.consult_mapped("fake-remediation-consult", "repair", self.current()["sha256"])
        result = self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], self.repair_request("fake-start", mapping))
        self.assertEqual("BLOCK", result["state"], "An observation is not an earlier actionable review finding")

    def test_ordinary_production_cannot_defer_current_case_proof(self):
        self.prepare()
        self.red()
        self.existing_case("unit")
        self.consult_mapped("current-case", "plan", "later-context")
        missing = RUNTIME._knowledge_errors(self.ledger.show("run-1"), self.current()["sha256"])
        self.assertTrue(any("unit" in issue for issue in missing))
        self.assertEqual("BLOCK", self.start("ordinary-production", "PRODUCTION")["state"], "Ordinary PRODUCTION may not defer a current carried regression without named remediation")

    def test_verify_collects_missing_unrelated_proof_while_finding_stays_open(self):
        mapping = self.repair_setup()
        self.assertEqual("BLOCK", self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], self.repair_request("missing-U", mapping))["state"])
        started = self.start("verify-U", "VERIFY")
        self.assertEqual("PASS", started["state"], started)
        self.assertEqual([], started["start"]["data"]["write_scope"])
        self.actual_check("U-proof", "verify-U")
        self.assertTrue(any("open-F/F" in issue for issue in RUNTIME._finding_errors(self.ledger.show("run-1"), self.current()["sha256"])))
        self.assertEqual("BLOCK", self.start("ordinary-test", "TEST_ONLY")["state"])
        bounded = self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], self.repair_request("bounded-test", mapping))
        self.assertEqual("PASS", bounded["state"], bounded)

    def test_test_red_verify_production_green_preserves_finding_and_unrelated_proof(self):
        mapping = self.repair_setup()
        initial = self.start("verify-initial-U", "VERIFY")
        self.assertEqual("PASS", initial["state"], initial)
        self.actual_check("initial-U", "verify-initial-U")
        tested = self.ledger.preflight("run-1", "TEST_ONLY", self.ledger.show("run-1")["seq"], self.repair_request("F-test", mapping))
        self.assertEqual("PASS", tested["state"], tested)
        (self.repo / "tests.py").write_text("from app import value\nassert value == 2\n")
        frozen = self.root / "F-test-snapshot.py"
        frozen.write_bytes((self.repo / "tests.py").read_bytes())
        actual = subprocess.run([sys.executable, "-B", "tests.py"], cwd=self.repo, capture_output=True)
        self.assertNotEqual(0, actual.returncode)
        self.assertIn(b"AssertionError", actual.stderr)
        output = self.root / "F-red.log"
        output.write_bytes(actual.stdout + actual.stderr)
        red = {"plan": self.plan, "candidate": self.current()["sha256"], "phase": "RED", "acceptance": "behavior",
               "check": "unit", "start": "F-test", "test_id": "unit", "test_path": "tests.py", "test": RUNTIME.reference(frozen),
               "output": RUNTIME.reference(output), "exit": actual.returncode, "outcome": "INTENDED_ASSERTION_FAILURE", "failure_kind": "ASSERTION"}
        self.push("F-red", "proof", red)
        repair_failure = self.failure_intent()
        repair_failure["id"] = "F-current-capture"
        repair_failure["case"]["origin"]["failure_id"] = "F-current-RED"
        repair_failure["failure"]["output"] = RUNTIME.reference(output)
        captured = self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], repair_failure)
        self.assertEqual("PASS", captured["state"], captured)
        self.consult_mapped("F-current-consult", "repair", self.current()["sha256"])
        self.assertEqual("BLOCK", self.ledger.preflight("run-1", "PRODUCTION", self.ledger.show("run-1")["seq"], self.repair_request("stale-U", mapping))["state"], "Authorized test edits make unrelated U proof stale")
        self.ledger = RUNTIME.Ledger(self.db)
        self.assertEqual("PASS", self.start("verify-current-U", "VERIFY")["state"])
        self.actual_check("current-U", "verify-current-U")
        self.assertEqual("PASS", self.start("verify-repeat", "VERIFY")["state"])
        self.actual_check("repeat-U", "verify-repeat")
        self.assertTrue(any("open-F/F" in issue for issue in RUNTIME._finding_errors(self.ledger.show("run-1"), self.current()["sha256"])))
        self.assertEqual("BLOCK", self.start("ordinary-F-production", "PRODUCTION")["state"])
        omitted = self.repair_request("omitted-F", mapping)
        omitted["remediation"]["findings"] = []
        self.assertEqual("BLOCK", self.ledger.preflight("run-1", "PRODUCTION", self.ledger.show("run-1")["seq"], omitted)["state"])
        production = self.ledger.preflight("run-1", "PRODUCTION", self.ledger.show("run-1")["seq"], self.repair_request("F-production", mapping))
        self.assertEqual("PASS", production["state"], production)
        (self.repo / "app.py").write_text("value = 2\n")
        actual = subprocess.run([sys.executable, "-B", "tests.py"], cwd=self.repo, capture_output=True)
        self.assertEqual(0, actual.returncode, actual.stderr)
        output = self.root / "F-green.log"
        output.write_bytes(actual.stdout + actual.stderr)
        self.push("F-green", "proof", dict(red, candidate=self.current()["sha256"], phase="GREEN", start="F-production",
                  output=RUNTIME.reference(output), exit=0, outcome="PASS", failure_kind=None))
        self.actual_check("final-U", "F-production")
        self.push("F-repair-result", "repair", {"defect": "assignment-defect", "outcome": "PASS",
                  "before": production["start"]["data"]["candidate"]["sha256"], "after": self.current()["sha256"],
                  "output": RUNTIME.reference(output), "start": "F-production"})
        self.assertEqual("BLOCK", self.ledger.check("run-1")["state"])
        self.push("F-independent-recheck", "recheck", {"plan": self.plan, "candidate": self.current()["sha256"], "verdict": "APPROVE",
                  "reviewer": self.reviewer("independent-F-recheck", "gpt-6.1-sol"), "findings": [], "proof": "F-green"})
        self.push("F-fixed", "disposition", {"review": "open-F", "finding": "F", "action": "FIXED", "reason": "Actual current GREEN plus independent recheck",
                  "evidence": RUNTIME.reference(output), "recheck": "F-green", "review_recheck": "F-independent-recheck"})
        self.finish(prefix="closed-F-", proof_id="F-green")
        self.assertEqual("PASS", self.ledger.check("run-1")["state"], self.ledger.check("run-1"))

    def test_verify_refuses_source_test_instruction_and_profile_drift(self):
        for changed in ("app.py", "tests.py", "instructions.md", "profile"):
            with self.subTest(changed=changed):
                case = self.fresh_case()
                profile = case.root / "profile"
                (profile / "scripts").mkdir(parents=True)
                copied_script = profile / "scripts/i2e.py"
                copied_script.write_bytes(SCRIPT.read_bytes())
                entry = profile / "SKILL.md"
                entry.write_text("Synthetic profile.\n")
                with mock.patch.object(RUNTIME, "__file__", str(copied_script)):
                    case.prepare()
                    started = case.start("verify-before-drift", "VERIFY")
                    self.assertEqual("PASS", started["state"], started)
                    target = entry if changed == "profile" else case.repo / changed
                    target.write_text("changed during source-preserving verification\n")
                    proof = case.actual_check("drift-proof", "verify-before-drift", check="unit", code="pass")
                    errors = RUNTIME._proof_errors(case.ledger.show("run-1"), proof, "PASS", case.current()["sha256"], case.plan)
                    self.assertTrue(errors, "VERIFY CHECK must bind the unchanged actual source/instruction/profile")
                    self.assertEqual("BLOCK", case.start("after-drift", "TEST_ONLY")["state"])

    def test_verify_does_not_reset_open_test_baseline_or_supply_green(self):
        self.prepare()
        self.red()
        started = self.start("verify-between-phases", "VERIFY")
        self.assertEqual("PASS", started["state"], started)
        self.assertEqual("PASS", self.start("verify-again", "VERIFY")["state"])
        fake_green = self.push("verify-green", "proof", {"plan": self.plan, "candidate": self.current()["sha256"],
            "phase": "GREEN", "acceptance": "behavior", "check": "unit", "start": "verify-again", "test_id": "unit",
            "test_path": "tests.py", "test": RUNTIME.reference(self.test_copy), "output": RUNTIME.reference(self.raw), "exit": 0, "outcome": "PASS"})
        self.assertTrue(RUNTIME._proof_errors(self.ledger.show("run-1"), fake_green, "GREEN", self.current()["sha256"], self.plan))
        self.assertEqual("BLOCK", self.ledger.check("run-1")["state"], "VERIFY cannot replace a production completion cycle")
        (self.repo / "app.py").write_text("value = 9\n")
        self.assertEqual("BLOCK", self.start("test-rebase-after-verify", "TEST_ONLY")["state"])

    def test_verify_keeps_approval_capture_and_failure_counter_prerequisites(self):
        self.prepare(approve=False)
        result = self.start("unapproved-verify", "VERIFY")
        self.assertEqual("BLOCK", result["state"])
        self.assertTrue(any("approval" in issue for issue in result["errors"]))
        self.review("current-approval", "plan_review", "current-plan-astra", "gpt-6-astra")
        request = self.failure_intent()
        with mock.patch.object(self.ledger, "_capture_link", side_effect=RUNTIME.RuntimeError("Expected begun capture gap")):
            self.assertEqual("BLOCK", self.ledger.capture("run-1", self.ledger.show("run-1")["seq"], request)["state"])
        result = self.start("gap-verify", "VERIFY")
        self.assertEqual("BLOCK", result["state"])
        self.assertTrue(any("capture" in issue for issue in result["errors"]))
        self.assertEqual("PASS", self.ledger.capture("run-1", 0, request)["state"])
        for index in range(2):
            self.push("failed-repair-" + str(index), "repair", {"defect": "assignment-defect", "outcome": "FAIL",
                      "before": self.current()["sha256"], "after": self.current()["sha256"], "output": RUNTIME.reference(self.raw), "start": "unrecorded"})
        result = self.ledger.preflight("run-1", "VERIFY", self.ledger.show("run-1")["seq"], {"id": "third-verify", "acceptance": ["behavior"], "repair_defect": "assignment-defect"})
        self.assertEqual("BLOCK", result["state"])
        self.assertTrue(any("Astra" in issue for issue in result["errors"]))

    def test_verify_defers_only_ordinary_pending_tdd_challenge_and_not_three_cycles(self):
        self.prepare()
        ordinary = {"lineage": "ordinary", "kind": "ordinary", "contributors": ["owner-session"],
                    "artifact": RUNTIME.reference(self.raw), "acceptance": ["behavior"], "strategy": "TDD_RED",
                    "choice": "Add an assertion", "alternatives": [], "tradeoff": "One focused test", "supersedes": None}
        self.push("ordinary-choice", "decision", dict(ordinary, revision=RUNTIME.digest(ordinary)))
        started = self.start("verify-pending-ordinary", "VERIFY")
        self.assertEqual("PASS", started["state"], started)
        previous = None
        for index in range(3):
            architecture = dict(ordinary, lineage="architecture", kind="architecture", strategy="REVIEW",
                                supersedes=previous, choice="Architecture revision " + str(index))
            previous = RUNTIME.digest(architecture)
            self.push("architecture-" + str(index), "decision", dict(architecture, revision=previous))
            if index == 0:
                self.assertEqual("BLOCK", self.start("unsupported-architecture-verify", "VERIFY")["state"])
            self.push("architecture-rejection-" + str(index), "doubt_review", {"decision": "architecture", "revision": previous,
                      "verdict": "REVISE", "findings": [], "reviewer": self.reviewer("architecture-astra-" + str(index), "gpt-6-astra")})
        result = self.start("three-cycle-verify", "VERIFY")
        self.assertEqual("BLOCK", result["state"])
        self.assertTrue(any("three" in issue.lower() for issue in result["errors"]))


class PostVerifyCompletionTests(LifecycleFixture):
    actual_check = BoundaryRegressionTests.actual_check
    fresh_case = BoundaryRegressionTests.fresh_case

    def test_source_preserving_VERIFY_retains_existing_production_completion(self):
        self.prepare()
        self.implement()
        self.finish()
        before = self.ledger.check("run-1")
        self.assertEqual("PASS", before["state"], before)
        verified = self.start("post-production-verify", "VERIFY")
        self.assertEqual("PASS", verified["state"], verified)
        self.assertEqual([], verified["start"]["data"]["write_scope"])
        proof = self.actual_check("post-verify-current-check", "post-production-verify", check="unit", code="from app import value; assert value == 1")
        self.finish(prefix="after-verify-", proof_id="post-verify-current-check")
        state = self.ledger.show("run-1")
        after = self.ledger.check("run-1")
        green = RUNTIME._latest(state, "proof", lambda event: event["data"].get("phase") == "GREEN")
        validation = {"GREEN": RUNTIME._proof_errors(state, green, "GREEN", self.current()["sha256"], self.plan),
                      "VERIFY_CHECK": RUNTIME._proof_errors(state, proof, "PASS", self.current()["sha256"], self.plan)}
        self.assertEqual(before["candidate"], after.get("candidate"))
        self.assertEqual({"GREEN": [], "VERIFY_CHECK": []}, validation)
        self.assertEqual("PRODUCTION", RUNTIME._latest_work_start(state)["data"]["mode"])
        self.assertEqual("PASS", after["state"], "Read-only VERIFY cannot erase the still-current authorized PRODUCTION/GREEN cycle")

    def test_verify_alone_or_after_reopened_test_cannot_complete(self):
        for history in ("verify-alone", "open-test-after-production"):
            with self.subTest(history=history):
                case = self.fresh_case()
                case.prepare()
                if history == "open-test-after-production":
                    case.implement()
                    case.finish()
                    self.assertEqual("PASS", case.ledger.check("run-1")["state"])
                    self.assertEqual("PASS", case.start("reopened-test", "TEST_ONLY")["state"])
                verified = case.start("verification-only", "VERIFY")
                self.assertEqual("PASS", verified["state"], verified)
                # A passing source observation does not supply behavioral GREEN
                # or close a newly opened writing cycle.
                case.actual_check("existing-observation", "verification-only", check="unit", code="from app import value; assert value in (0, 1)")
                case.finish(prefix="verify-only-", proof_id="existing-observation")
                self.assertEqual("BLOCK", case.ledger.check("run-1")["state"])

    def test_post_production_verify_retains_source_test_instruction_profile_drift_guards(self):
        for changed in ("app.py", "tests.py", "instructions.md", "profile"):
            with self.subTest(changed=changed):
                case = self.fresh_case()
                profile = case.root / "profile"
                (profile / "scripts").mkdir(parents=True)
                copied_script = profile / "scripts/i2e.py"
                copied_script.write_bytes(SCRIPT.read_bytes())
                entry = profile / "SKILL.md"
                entry.write_text("Synthetic frozen profile.\n")
                with mock.patch.object(RUNTIME, "__file__", str(copied_script)):
                    case.prepare()
                    case.implement()
                    case.finish()
                    self.assertEqual("PASS", case.ledger.check("run-1")["state"])
                    self.assertEqual("PASS", case.start("post-production-verify", "VERIFY")["state"])
                    case.actual_check("verified-observation", "post-production-verify", check="unit", code="from app import value; assert value == 1")
                    case.finish(prefix="verified-", proof_id="verified-observation")
                    target = entry if changed == "profile" else case.repo / changed
                    target.write_text("Changed after source-preserving CHECK.\n")
                    self.assertEqual("BLOCK", case.ledger.check("run-1")["state"], "Earlier production cannot hide VERIFY source/instruction/profile drift")


class DecisionCycleQualificationTests(LifecycleFixture):
    def fresh_cycle_case(self):
        case = DecisionCycleQualificationTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def cycle_decision(self, index, previous, *, kind="ordinary", strategy=None, contributors=None, claimed=None, lineage="same-decision"):
        artifact = self.root / (lineage + "-artifact-" + str(index) + ".md")
        artifact.write_text("Immutable synthetic decision revision " + str(index) + ".\n")
        content = {"lineage": lineage, "kind": kind, "contributors": contributors or ["owner-session"],
                   "artifact": RUNTIME.reference(artifact), "acceptance": ["behavior"],
                   "strategy": strategy or ("TDD_RED" if kind == "ordinary" else "REVIEW"),
                   "choice": "revision " + str(index), "alternatives": [], "tradeoff": "unresolved", "supersedes": previous}
        revision = claimed or RUNTIME.digest(content)
        self.ledger.append("run-1", {"id": lineage + "-choice-" + str(index), "type": "decision", "data": dict(content, revision=revision)}, self.ledger.show("run-1")["seq"])
        return revision

    def cycle_review(self, name, revision, verdict, *, kind="ordinary", session=None, fields=None, lineage="same-decision"):
        receipt = self.reviewer(session or name, "gpt-6.1-sol" if kind == "ordinary" else "gpt-6-astra")
        receipt.update(fields or {})
        data = {"decision": lineage, "revision": revision, "verdict": verdict, "findings": [], "reviewer": receipt}
        return self.ledger.append("run-1", {"id": name, "type": "doubt_review", "data": data}, self.ledger.show("run-1")["seq"])

    def rejected_cycles(self, *, count=3, kind="ordinary", strategy=None):
        self.raw.write_text("SYNTHETIC_ONLY_NO_MODEL_INVOKED: decision-cycle protocol fixture.\n")
        self.prepare()
        previous, revisions = None, []
        for index in range(count):
            previous = self.cycle_decision(index, previous, kind=kind, strategy=strategy)
            revisions.append(previous)
            self.cycle_review("rejection-" + str(index), previous, "REVISE", kind=kind)
        return revisions

    def assert_cycle_stop(self):
        for mode in ("TEST_ONLY", "VERIFY"):
            result = self.start("must-stop-" + mode, mode)
            self.assertEqual("BLOCK", result["state"], result)
            self.assertTrue(any("three unresolved" in issue for issue in result["errors"]), result)

    def refresh_plan_for_contributors(self, sessions):
        receipt = self.reviewer("late-plan-astra", "gpt-6-astra")
        receipt["excluded"] = sorted(set(receipt["excluded"]) | set(sessions))
        self.push("late-plan-approval", "plan_review", {"plan": self.plan, "verdict": "APPROVE", "reviewer": receipt, "findings": []})

    def test_stale_or_nonexistent_supported_revision_cannot_reset_three_cycles(self):
        for selection in ("obsolete", "nonexistent"):
            with self.subTest(selection=selection):
                case = self.fresh_cycle_case()
                revisions = case.rejected_cycles()
                before = case.start("before-stale-support", "TEST_ONLY")
                self.assertEqual("BLOCK", before["state"])
                self.assertTrue(any("three unresolved" in issue for issue in before["errors"]))
                case.cycle_review("stale-support", revisions[0] if selection == "obsolete" else "f" * 64, "SUPPORTED")
                after = case.start("after-stale-support", "TEST_ONLY")
                # Exact independent native counterexample safety assertion.
                assert after["state"] == "BLOCK", "Stale SUPPORTED review incorrectly reset three unresolved decision cycles and authorized TEST_ONLY"
                self.assertTrue(any("three unresolved" in issue for issue in after["errors"]), after)
                case.assert_cycle_stop()

    def test_unqualified_supported_receipts_cannot_reset_three_cycles(self):
        variants = [("ordinary", {"model": "gpt-6-astra"}), ("architecture", {"model": "gpt-6.1-sol"}),
                    ("ordinary", {"effort": "high"}), ("ordinary", {"fresh": False}),
                    ("ordinary", {"session": "rejection-0"}), ("ordinary", {"session": "owner-session"}),
                    ("ordinary", {"excluded": []})]
        for index, (kind, fields) in enumerate(variants):
            with self.subTest(variant=index, kind=kind):
                case = self.fresh_cycle_case()
                revisions = case.rejected_cycles(kind=kind)
                case.cycle_review("unqualified-support", revisions[-1], "SUPPORTED", kind=kind, fields=fields)
                case.assert_cycle_stop()

    def test_stale_raw_review_references_do_not_reset_three_cycles(self):
        for field in ("input", "invocation", "response"):
            with self.subTest(field=field):
                case = self.fresh_cycle_case()
                revisions = case.rejected_cycles()
                raw = case.root / ("support-" + field + ".txt")
                raw.write_text("SYNTHETIC_ONLY_NO_MODEL_INVOKED: original review evidence.\n")
                case.cycle_review("stale-evidence-support", revisions[-1], "SUPPORTED", fields={field: RUNTIME.reference(raw)})
                raw.write_text("Changed evidence bytes cannot qualify the recorded resolution.\n")
                case.assert_cycle_stop()

    def test_wrong_observed_profile_cannot_reset_three_cycles(self):
        profile = self.root / "copied-profile"
        (profile / "scripts").mkdir(parents=True)
        script = profile / "scripts/i2e.py"
        script.write_bytes(SCRIPT.read_bytes())
        entry = profile / "SKILL.md"
        original = b"Synthetic reviewed profile A.\n"
        entry.write_bytes(original)
        with mock.patch.object(RUNTIME, "__file__", str(script)):
            revisions = self.rejected_cycles()
            entry.write_text("Unreviewed profile B at actual support observation.\n")
            self.cycle_review("wrong-profile-support", revisions[-1], "SUPPORTED")
            entry.write_bytes(original)
            self.assert_cycle_stop()

    def test_malformed_historical_revision_cannot_qualify_a_reset(self):
        revisions = self.rejected_cycles(count=2)
        malformed = self.cycle_decision(2, revisions[-1], claimed="a" * 64)
        self.cycle_review("malformed-revision-support", malformed, "SUPPORTED")
        current = self.cycle_decision(3, malformed)
        self.cycle_review("current-rejection", current, "REVISE")
        self.assert_cycle_stop()

    def test_stale_historical_decision_artifact_cannot_qualify_a_reset(self):
        revisions = self.rejected_cycles(count=2)
        self.cycle_review("old-resolution", revisions[-1], "SUPPORTED")
        previous = revisions[-1]
        for index in (2, 3):
            previous = self.cycle_decision(index, previous)
            self.cycle_review("later-rejection-" + str(index), previous, "REVISE")
        (self.root / "same-decision-artifact-1.md").write_text("Changed historical artifact; immutable evidence is unavailable.\n")
        self.assert_cycle_stop()

    def test_qualified_active_revision_resolution_resets_cycles_for_designated_model(self):
        for kind in ("ordinary", "architecture"):
            with self.subTest(kind=kind):
                case = self.fresh_cycle_case()
                revisions = case.rejected_cycles(kind=kind)
                case.assert_cycle_stop()
                case.cycle_review("genuine-resolution", revisions[-1], "SUPPORTED", kind=kind)
                for mode in ("TEST_ONLY", "VERIFY"):
                    result = case.start("resolved-" + mode, mode)
                    self.assertEqual("PASS", result["state"], result)

    def test_historical_active_resolution_survives_later_revisions_and_contributors(self):
        revisions = self.rejected_cycles()
        self.cycle_review("genuine-historical-resolution", revisions[-1], "SUPPORTED")
        previous = revisions[-1]
        for index in (3, 4):
            previous = self.cycle_decision(index, previous, contributors=["owner-session", "future-author"])
            self.cycle_review("future-rejection-" + str(index), previous, "REVISE")
        self.refresh_plan_for_contributors(["future-author"])
        for mode in ("TEST_ONLY", "VERIFY"):
            result = self.start("historical-resolution-" + mode, mode)
            self.assertEqual("PASS", result["state"], "A qualifying then-active historical resolution remains valid before two later unresolved cycles: " + str(result))
        current = self.cycle_decision(5, previous, contributors=["owner-session", "future-author"])
        self.cycle_review("third-future-rejection", current, "REVISE")
        self.assert_cycle_stop()

    def test_historical_reset_does_not_waive_current_reviewer_independence(self):
        revisions = self.rejected_cycles(strategy="REVIEW")
        self.cycle_review("genuine-resolution", revisions[-1], "SUPPORTED", session="later-author")
        self.cycle_decision(0, None, contributors=["owner-session", "later-author"], lineage="another-decision")
        self.refresh_plan_for_contributors(["later-author"])
        result = self.start("current-author-reviewer", "TEST_ONLY")
        self.assertEqual("BLOCK", result["state"])
        self.assertTrue(any("independence" in issue for issue in result["errors"]), result)
        self.assertFalse(any("three unresolved" in issue for issue in result["errors"]), "Historical qualification and current authorization use their proper separate contributor contexts")


if __name__ == "__main__":
    unittest.main()
