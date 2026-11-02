"""Installer proof uses synthetic roots only; no installed skill is mutated."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("i2e_installer", SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def files(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in root.rglob("*") if p.is_file()}


class Interrupted(BaseException):
    pass


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.package = self.source / "skills" / "i2e-team"
        self.package.mkdir(parents=True)
        (self.package / "SKILL.md").write_bytes(
            b"---\nname: i2e-team\ndescription: Synthetic local fixture\n---\n\n# Team\n")
        (self.package / "scripts").mkdir()
        (self.package / "scripts" / "i2e.py").write_bytes(b"print('synthetic')\n")
        (self.package / "references").mkdir()
        (self.package / "references" / "fixture.bin").write_bytes(b"\x00\xfffixture")
        self.expected = files(self.package)
        self.skills = self.root / "skills"
        self.router = self.skills / "i2e-mode" / "SKILL.md"
        self.router.parent.mkdir(parents=True)
        self.before = (b"---\r\nname: i2e-mode\r\ndescription: Fixture router\r\n---\r\n"
                       b"\r\n# Existing router\r\n\r\nKeep every original byte.\r\n")
        self.router.write_bytes(self.before)
        self.helper = self.skills / "i2e-failure-cases" / "scripts" / "shared_cases.py"
        self.helper.parent.mkdir(parents=True)
        self.helper.write_bytes(b"# canonical helper fixture\n")
        self.legacy = self.skills / "i2e-chat-astra-sol" / "SKILL.md"
        self.legacy.parent.mkdir(parents=True)
        self.legacy.write_bytes(b"# legacy unchanged\n")
        self.state = self.root / "state"

    def do_install(self):
        result = installer.install(self.source, self.skills, self.state,
                                   self.expected, sha(self.before))
        self.assertEqual(result["status"], "INSTALLED")
        self.assertTrue(Path(result["receipt"]).is_file())
        return result

    def receipt_after_interruption(self):
        receipts = list(self.state.glob("*/receipt.json"))
        self.assertEqual(len(receipts), 1)
        return receipts[0]

    def test_manifest_is_literal_nested_source_bytes(self):
        self.assertEqual(installer.source_manifest(self.source), self.expected)

    def test_install_preserves_router_bytes_and_external_dependencies(self):
        helper_before = self.helper.read_bytes()
        legacy_before = self.legacy.read_bytes()
        result = self.do_install()
        self.assertEqual(files(self.skills / "i2e-team"), self.expected)
        after = self.router.read_bytes()
        self.assertTrue(after.startswith(self.before.split(b"# Existing router")[0]))
        self.assertIn(b"i2e-team default route: begin", after)
        self.assertIn(b"i2e-chat-astra-sol", after)
        self.assertIn(b"../i2e-team/SKILL.md", after)
        self.assertLess(after.index(b"explicit"), after.index(b"default engineering"))
        start = after.index(b"<!-- i2e-team default route: begin -->")
        end = after.index(b"<!-- i2e-team default route: end -->")
        suffix = end + len(b"<!-- i2e-team default route: end -->\n\n")
        self.assertEqual(after[:start] + after[suffix:], self.before)
        receipt = Path(result["receipt"])
        self.assertEqual(stat.S_IMODE(receipt.parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
        self.assertEqual((receipt.parent / "router-before.bin").read_bytes(), self.before)
        self.assertEqual(self.helper.read_bytes(), helper_before)
        self.assertEqual(self.legacy.read_bytes(), legacy_before)

    def test_rollback_restores_exact_router_and_is_idempotent(self):
        result = self.do_install()
        rolled = installer.rollback(result["receipt"], self.state)
        self.assertEqual(rolled["status"], "ROLLED_BACK")
        self.assertEqual(self.router.read_bytes(), self.before)
        self.assertFalse((self.skills / "i2e-team").exists())
        self.assertEqual(installer.rollback(result["receipt"], self.state)["status"],
                         "ALREADY_ROLLED_BACK")

    def test_source_drift_refused_before_destination_writes(self):
        (self.package / "SKILL.md").write_text("changed source")
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.skills, self.state, self.expected, sha(self.before))
        self.assertEqual(self.router.read_bytes(), self.before)
        self.assertFalse((self.skills / "i2e-team").exists())

    def test_added_source_file_is_drift(self):
        (self.package / "unreviewed.py").write_text("unreviewed")
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.skills, self.state, self.expected, sha(self.before))

    def test_router_drift_refused(self):
        changed = self.before + b"Owner edit\n"
        self.router.write_bytes(changed)
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.skills, self.state, self.expected, sha(self.before))
        self.assertEqual(self.router.read_bytes(), changed)

    def test_unowned_existing_target_refused_even_if_identical(self):
        import shutil
        target = self.skills / "i2e-team"
        shutil.copytree(self.package, target)
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.skills, self.state, self.expected, sha(self.before))
        self.assertEqual(files(target), self.expected)
        self.assertEqual(self.router.read_bytes(), self.before)

    def test_canonical_helper_is_required_and_never_installed(self):
        self.helper.unlink()
        with self.assertRaises(installer.InstallError):
            installer.install(self.source, self.skills, self.state, self.expected, sha(self.before))
        self.assertFalse(self.helper.exists())

    def test_source_symlink_refused(self):
        (self.package / "alias").symlink_to(self.legacy)
        with self.assertRaises(installer.InstallError):
            installer.source_manifest(self.source)

    def test_source_directory_symlink_refused(self):
        (self.package / "alias").symlink_to(self.legacy.parent, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            installer.source_manifest(self.source)

    def test_destination_and_state_symlinks_refused(self):
        for kind in ("target", "router", "helper", "state", "skills-ancestor"):
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as directory:
                    point = Path(directory) / "link"
                    if kind == "target":
                        path = self.skills / "i2e-team"
                        path.symlink_to(self.package, target_is_directory=True)
                    elif kind == "router":
                        path = self.router
                        self.router.rename(point)
                        path.symlink_to(point)
                    elif kind == "helper":
                        path = self.helper
                        self.helper.rename(point)
                        path.symlink_to(point)
                    elif kind == "state":
                        path = self.state
                        path.symlink_to(directory, target_is_directory=True)
                    else:
                        path = point
                        path.symlink_to(self.skills, target_is_directory=True)
                    try:
                        with self.assertRaises(installer.InstallError):
                            installer.install(self.source,
                                              point if kind == "skills-ancestor" else self.skills,
                                              self.state, self.expected, sha(self.before))
                    finally:
                        path.unlink()
                        if kind in ("router", "helper"):
                            point.rename(path)

    def test_state_cannot_live_inside_package_or_skills_root(self):
        for state in (self.package / "state", self.skills / "state"):
            with self.subTest(state=state), self.assertRaises(installer.InstallError):
                installer.install(self.source, self.skills, state, self.expected, sha(self.before))

    def test_manifest_paths_and_hashes_are_validated(self):
        for manifest in ({"../escape": "0" * 64}, {"/escape": "0" * 64},
                         {"SKILL.md": "invalid"}, {}, []):
            with self.subTest(manifest=manifest), self.assertRaises(installer.InstallError):
                installer.install(self.source, self.skills, self.state, manifest, sha(self.before))

    def test_edited_router_preserves_both_route_and_package_on_rollback(self):
        result = self.do_install()
        self.router.write_bytes(self.router.read_bytes() + b"\nOwner addition\n")
        before = self.router.read_bytes()
        self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "CONFLICT")
        self.assertEqual(self.router.read_bytes(), before)
        self.assertEqual(files(self.skills / "i2e-team"), self.expected)

    def test_changed_or_extra_package_preserves_both_on_rollback(self):
        for kind in ("changed", "extra"):
            with self.subTest(kind=kind):
                result = self.do_install()
                target = self.skills / "i2e-team"
                changed = target / ("SKILL.md" if kind == "changed" else "owner-note.md")
                changed.write_text("owner content")
                router_before = self.router.read_bytes()
                package_before = files(target)
                self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "CONFLICT")
                self.assertEqual(self.router.read_bytes(), router_before)
                self.assertEqual(files(target), package_before)
                if kind == "changed":
                    changed.write_bytes((self.package / "SKILL.md").read_bytes())
                else:
                    changed.unlink()
                self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "ROLLED_BACK")

    def test_malformed_receipt_and_wrong_state_root_refused(self):
        result = self.do_install()
        path = Path(result["receipt"])
        original = path.read_bytes()
        variants = [b"not-json", b'{"version":1,"version":1}',
                    json.dumps({**json.loads(original), "skills_root": "/"}).encode(),
                    json.dumps({**json.loads(original), "unexpected": True}).encode()]
        for variant in variants:
            with self.subTest(variant=variant):
                path.write_bytes(variant)
                with self.assertRaises(installer.InstallError):
                    installer.rollback(path, self.state)
        path.write_bytes(original)
        with self.assertRaises(installer.InstallError):
            installer.rollback(path, self.root / "other-state")
        self.assertNotEqual(self.router.read_bytes(), self.before)
        self.assertTrue((self.skills / "i2e-team").exists())

    def test_install_interruption_each_durable_phase_is_recoverable(self):
        phases = ("PREPARED", "STAGED", "INSTALLING_PACKAGE", "PACKAGE_INSTALLED",
                  "INSTALLING_ROUTER", "INSTALLED")
        write = installer._write_receipt
        for phase in phases:
            with self.subTest(phase=phase):
                def interrupt(path, data):
                    write(path, data)
                    if data["phase"] == phase:
                        raise Interrupted(phase)
                with patch.object(installer, "_write_receipt", side_effect=interrupt):
                    with self.assertRaises(Interrupted):
                        self.do_install()
                receipt = self.receipt_after_interruption()
                self.assertEqual(installer.rollback(receipt, self.state)["status"], "ROLLED_BACK")
                self.assertEqual(self.router.read_bytes(), self.before)
                self.assertFalse((self.skills / "i2e-team").exists())
                import shutil
                shutil.rmtree(self.state)

    def test_install_interruption_after_atomic_destination_operations(self):
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        for primitive, where in (("_rename_noreplace", self.skills / "i2e-team"),
                                 ("_link_noreplace", self.router)):
            with self.subTest(where=where):
                original = getattr(installer, primitive)
                def interrupt(src, dst):
                    original(src, dst)
                    if Path(dst) == where:
                        raise Interrupted(str(where))
                with patch.object(installer, primitive, side_effect=interrupt):
                    with self.assertRaises(Interrupted):
                        self.do_install()
                self.assertEqual(installer.rollback(self.receipt_after_interruption(), self.state)["status"],
                                 "ROLLED_BACK")
                self.assertEqual(self.router.read_bytes(), self.before)
                self.assertFalse((self.skills / "i2e-team").exists())
                import shutil
                shutil.rmtree(self.state)

    def test_rollback_interruption_keeps_receipt_and_recovers_partial_removal(self):
        # The amended contract retires the whole object; recursive removal is forbidden.
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        result = self.do_install()
        move = installer._rename_noreplace
        target = self.skills / "i2e-team"
        def interrupt(src, dst):
            move(src, dst)
            if Path(src) == target:
                raise Interrupted("package retired before receipt update")
        with patch.object(installer, "_rename_noreplace", side_effect=interrupt):
            with self.assertRaises(Interrupted):
                installer.rollback(result["receipt"], self.state)
        self.assertTrue(any(p.name == "SKILL.md" for p in self.state.rglob("SKILL.md")))
        self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "ROLLED_BACK")
        self.assertFalse(target.exists())

    def test_rollback_interruption_each_durable_phase_is_recoverable(self):
        write = installer._write_receipt
        for phase in ("ROLLING_BACK_ROUTER", "ROLLING_BACK_PACKAGE", "ROLLED_BACK"):
            with self.subTest(phase=phase):
                result = self.do_install()
                def interrupt(path, data):
                    write(path, data)
                    if data["phase"] == phase:
                        raise Interrupted(phase)
                with patch.object(installer, "_write_receipt", side_effect=interrupt):
                    with self.assertRaises(Interrupted):
                        installer.rollback(result["receipt"], self.state)
                recovered = installer.rollback(result["receipt"], self.state)["status"]
                self.assertIn(recovered, ("ROLLED_BACK", "ALREADY_ROLLED_BACK"))
                self.assertEqual(self.router.read_bytes(), self.before)
                self.assertFalse((self.skills / "i2e-team").exists())
                import shutil
                shutil.rmtree(self.state)

    def test_rollback_interruption_after_atomic_router_restoration(self):
        self.assertTrue(callable(getattr(installer, "_link_noreplace", None)))
        result = self.do_install()
        publish = installer._link_noreplace
        def interrupt(src, dst):
            publish(src, dst)
            if Path(dst) == self.router:
                raise Interrupted("router restored before phase update")
        with patch.object(installer, "_link_noreplace", side_effect=interrupt):
            with self.assertRaises(Interrupted):
                installer.rollback(result["receipt"], self.state)
        self.assertEqual(self.router.read_bytes(), self.before)
        self.assertTrue(any(p.name == "SKILL.md" for p in self.state.rglob("SKILL.md")))
        self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "ROLLED_BACK")

    def test_interrupted_partial_rollback_retry_preserves_recovery_progress(self):
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        result = self.do_install()
        move = installer._rename_noreplace
        target = self.skills / "i2e-team"
        def retire(src, dst):
            move(src, dst)
            if Path(src) == target:
                raise Interrupted("retired package before receipt update")
        with patch.object(installer, "_rename_noreplace", side_effect=retire):
            with self.assertRaises(Interrupted):
                installer.rollback(result["receipt"], self.state)
        write = installer._write_receipt
        def interrupt_retry(path, data):
            write(path, data)
            if data["phase"].startswith("ROLLING_BACK"):
                raise Interrupted("retry interrupted before more package removals")
        with patch.object(installer, "_write_receipt", side_effect=interrupt_retry):
            with self.assertRaises(Interrupted):
                installer.rollback(result["receipt"], self.state)
        self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "ROLLED_BACK")
        self.assertEqual(self.router.read_bytes(), self.before)
        self.assertFalse(target.exists())

    def test_generation_identity_and_anchors_are_outside_payload(self):
        result = self.do_install()
        receipt = Path(result["receipt"])
        data = json.loads(receipt.read_text())
        self.assertEqual(data.get("version"), 2)
        self.assertEqual(files(self.skills / "i2e-team"), self.expected)
        for key, path in (("package", self.skills / "i2e-team"), ("router_after", self.router)):
            self.assertEqual(data["objects"][key], [path.stat().st_dev, path.stat().st_ino])
        for name, original in (("package-skill", self.skills / "i2e-team" / "SKILL.md"),
                               ("router-after", self.router)):
            anchor = receipt.parent / "anchors" / name
            self.assertEqual(anchor.stat().st_ino, original.stat().st_ino)
        self.assertEqual(receipt.parent.stat().st_dev, self.skills.stat().st_dev)
        self.assertNotIn(self.skills, receipt.parents)

    def test_prepared_receipt_cannot_consume_later_generation_across_state_roots(self):
        write = installer._write_receipt
        def interrupt(path, data):
            write(path, data)
            if data["phase"] == "PREPARED":
                raise Interrupted("first attempt never activated")
        with patch.object(installer, "_write_receipt", side_effect=interrupt):
            with self.assertRaises(Interrupted):
                self.do_install()
        pending = self.receipt_after_interruption()
        for separate in (False, True):
            with self.subTest(separate=separate):
                old_state = self.state
                if separate:
                    self.state = self.root / "different-state"
                later = self.do_install()
                self.assertEqual(installer.rollback(pending, old_state)["status"], "CONFLICT")
                self.assertEqual(files(self.skills / "i2e-team"), self.expected)
                self.assertIn(b"i2e-team default route:", self.router.read_bytes())
                self.assertEqual(installer.rollback(later["receipt"], self.state)["status"], "ROLLED_BACK")
                self.state = old_state

    def test_same_bytes_different_inodes_are_not_owned(self):
        for which in ("router", "package"):
            with self.subTest(which=which):
                result = self.do_install()
                import shutil
                path = self.router if which == "router" else self.skills / "i2e-team"
                retained = self.root / ("replaced-" + which)
                path.rename(retained)
                if which == "router":
                    path.write_bytes(retained.read_bytes())
                else:
                    shutil.copytree(retained, path)
                self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "CONFLICT")
                self.assertTrue((self.skills / "i2e-team").exists())
                if which == "router":
                    path.unlink()
                else:
                    shutil.rmtree(path)
                retained.rename(path)
                self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "ROLLED_BACK")

    def test_router_edits_after_durable_intents_are_preserved(self):
        for phase in ("INSTALLING_ROUTER", "ROLLING_BACK_ROUTER"):
            with self.subTest(phase=phase):
                fixture = InstallerTests("test_manifest_is_literal_nested_source_bytes")
                fixture.setUp()
                self.addCleanup(fixture.doCleanups)
                result = fixture.do_install() if phase.startswith("ROLLING") else None
                edited = fixture.router.read_bytes() + b"Owner edit at durable intent\n"
                write = installer._write_receipt
                def edit(path, data):
                    write(path, data)
                    if data["phase"] == phase:
                        fixture.router.write_bytes(edited)
                with patch.object(installer, "_write_receipt", side_effect=edit):
                    if result:
                        self.assertEqual(installer.rollback(result["receipt"], fixture.state)["status"], "CONFLICT")
                    else:
                        with self.assertRaises(installer.InstallError):
                            fixture.do_install()
                self.assertEqual(fixture.router.read_bytes(), edited)
                self.assertTrue((fixture.skills / "i2e-team").exists())

    def test_late_package_file_is_preserved_by_pair_capture(self):
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        result = self.do_install()
        target = self.skills / "i2e-team"
        move = installer._rename_noreplace
        def add_owner_file(src, dst):
            if Path(src) == target:
                (target / "owner-note.md").write_text("owner content")
            return move(src, dst)
        with patch.object(installer, "_rename_noreplace", side_effect=add_owner_file):
            rolled = installer.rollback(result["receipt"], self.state)
        self.assertEqual(rolled["status"], "CONFLICT")
        self.assertEqual((target / "owner-note.md").read_text(), "owner content")
        self.assertIn(b"i2e-team default route:", self.router.read_bytes())

    def test_exclusive_promotion_preserves_late_empty_target(self):
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        target = self.skills / "i2e-team"
        move = installer._rename_noreplace
        identity = []
        def compete(src, dst):
            if Path(dst) == target:
                target.mkdir()
                identity.append(target.stat().st_ino)
            return move(src, dst)
        with patch.object(installer, "_rename_noreplace", side_effect=compete):
            with self.assertRaises(installer.InstallError):
                self.do_install()
        self.assertEqual(target.stat().st_ino, identity[0])
        self.assertEqual(list(target.iterdir()), [])
        self.assertEqual(self.router.read_bytes(), self.before)

    def test_competing_publication_preserves_both_router_objects(self):
        self.assertTrue(callable(getattr(installer, "_link_noreplace", None)))
        publish = installer._link_noreplace
        competitor = b"Owner router created during publication\n"
        def compete(src, dst):
            if Path(dst) == self.router:
                self.router.write_bytes(competitor)
            return publish(src, dst)
        with patch.object(installer, "_link_noreplace", side_effect=compete):
            with self.assertRaises(installer.InstallError):
                self.do_install()
        self.assertEqual(self.router.read_bytes(), competitor)
        self.assertTrue(any(p.read_bytes() == self.before for p in self.state.rglob("*")
                            if p.is_file()))

    def test_competing_capture_name_is_never_replaced(self):
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        move = installer._rename_noreplace
        competitors = []
        def compete(src, dst):
            if Path(src) == self.router:
                Path(dst).write_bytes(b"Recovery path competitor")
                competitors.append(Path(dst))
            return move(src, dst)
        with patch.object(installer, "_rename_noreplace", side_effect=compete):
            with self.assertRaises(installer.InstallError):
                self.do_install()
        self.assertEqual(self.router.read_bytes(), self.before)
        self.assertEqual(competitors[0].read_bytes(), b"Recovery path competitor")

    def test_retired_objects_keep_open_descriptor_writes_after_restart(self):
        result = self.do_install()
        target = self.skills / "i2e-team"
        with (target / "SKILL.md").open("ab") as package_fd, self.router.open("ab") as router_fd:
            rolled = installer.rollback(result["receipt"], self.state)
            self.assertEqual(rolled["status"], "ROLLED_BACK")
            package_fd.write(b"Late package fd write"); package_fd.flush()
            router_fd.write(b"Late router fd write"); router_fd.flush()
        self.assertTrue(any(b"Late package fd write" in p.read_bytes() for p in self.state.rglob("SKILL.md")))
        self.assertTrue(any(b"Late router fd write" in p.read_bytes() for p in self.state.rglob("*") if p.is_file()))
        completed = subprocess.run([sys.executable, "-B", str(SCRIPT), "rollback", "--receipt",
                                    result["receipt"], "--state-root", str(self.state)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "ALREADY_ROLLED_BACK")

    def test_unsupported_primitive_and_cross_filesystem_refuse(self):
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        import errno
        for failure in (errno.ENOTSUP, errno.EXDEV):
            with self.subTest(errno=failure):
                with patch.object(installer, "_rename_noreplace", side_effect=OSError(failure, "injected unavailable primitive")):
                    with self.assertRaises(installer.InstallError):
                        self.do_install()
                self.assertEqual(self.router.read_bytes(), self.before)
                self.assertFalse((self.skills / "i2e-team").exists())

    def test_router_edits_immediately_after_actual_capture_are_preserved(self):
        for rollback in (False, True):
            with self.subTest(rollback=rollback):
                fixture = InstallerTests("test_manifest_is_literal_nested_source_bytes")
                fixture.setUp()
                self.addCleanup(fixture.doCleanups)
                installed = fixture.do_install() if rollback else None
                edited = fixture.router.read_bytes() + b"Owner write after capture syscall\n"
                move = installer._rename_noreplace
                def edit_captured(src, dst):
                    move(src, dst)
                    if Path(src) == fixture.router:
                        Path(dst).write_bytes(edited)
                with patch.object(installer, "_rename_noreplace", side_effect=edit_captured):
                    if rollback:
                        result = installer.rollback(installed["receipt"], fixture.state)
                        self.assertEqual(result["status"], "CONFLICT")
                    else:
                        with self.assertRaises(installer.InstallError):
                            fixture.do_install()
                self.assertEqual(fixture.router.read_bytes(), edited)
                self.assertTrue((fixture.skills / "i2e-team").exists())

    def test_competing_package_name_during_conflict_retains_captured_pair(self):
        installed = self.do_install()
        target = self.skills / "i2e-team"
        move = installer._rename_noreplace
        captured = []
        def compete(src, dst):
            move(src, dst)
            if Path(src) == target:
                captured.append(Path(dst))
                (Path(dst) / "owner-note.md").write_text("retained owner edit")
                target.mkdir()
                (target / "competitor.md").write_text("competing package")
        with patch.object(installer, "_rename_noreplace", side_effect=compete):
            result = installer.rollback(installed["receipt"], self.state)
        self.assertEqual(result["status"], "CONFLICT")
        self.assertEqual((target / "competitor.md").read_text(), "competing package")
        self.assertEqual((captured[0] / "owner-note.md").read_text(), "retained owner edit")
        self.assertTrue(any(b"i2e-team default route:" in p.read_bytes()
                            for p in self.state.rglob("*") if p.is_file()))
        self.assertTrue(result["retained_paths"])

    def test_competing_router_during_original_restore_preserves_dependency(self):
        installed = self.do_install()
        publish = installer._link_noreplace
        competitor = b"Owner router during original restoration\n"
        def compete(src, dst):
            if Path(dst) == self.router:
                self.router.write_bytes(competitor)
            return publish(src, dst)
        with patch.object(installer, "_link_noreplace", side_effect=compete):
            result = installer.rollback(installed["receipt"], self.state)
        self.assertEqual(result["status"], "CONFLICT")
        self.assertEqual(self.router.read_bytes(), competitor)
        self.assertEqual(files(self.skills / "i2e-team"), self.expected)

    def test_interrupted_conflict_pair_restoration_resumes_before_live_package_refusal(self):
        """I-CODE-R1-01: port the independent assertion without weakening it."""
        installed = self.do_install()
        target = self.skills / "i2e-team"
        installed_router = self.router.read_bytes()
        move = installer._rename_noreplace
        stopped = [False]
        def edit_package_and_stop_after_restore(source, destination):
            source, destination = Path(source), Path(destination)
            move(source, destination)
            if source == target:
                (destination / "owner-note.md").write_text("Owner addition during capture\n")
            elif destination == target and not stopped[0]:
                stopped[0] = True
                raise Interrupted("package restored; captured router restoration not begun")
        with patch.object(installer, "_rename_noreplace", side_effect=edit_package_and_stop_after_restore):
            with self.assertRaises(Interrupted):
                installer.rollback(installed["receipt"], self.state)
        outcomes = [installer.rollback(installed["receipt"], self.state) for _ in range(2)]
        self.assertTrue(all(result["status"] == "CONFLICT" for result in outcomes))
        self.assertTrue(target.exists())
        self.assertEqual((target / "owner-note.md").read_text(), "Owner addition during capture\n")
        self.assertTrue(self.router.exists(), "Free router name must receive its captured object on retry")
        self.assertEqual(self.router.read_bytes(), installed_router)

    def test_router_object_swapped_at_capture_is_restored_without_replacement(self):
        move = installer._rename_noreplace
        edited = self.before + b"Owner replacement at capture\n"
        def swap(src, dst):
            if Path(src) == self.router:
                self.router.rename(self.root / "owner-retained-original")
                self.router.write_bytes(edited)
            return move(src, dst)
        with patch.object(installer, "_rename_noreplace", side_effect=swap):
            with self.assertRaises(installer.InstallError):
                self.do_install()
        self.assertEqual(self.router.read_bytes(), edited)
        self.assertEqual((self.root / "owner-retained-original").read_bytes(), self.before)
        self.assertEqual(files(self.skills / "i2e-team"), self.expected)

    def test_native_adapter_never_falls_back_after_unsupported_or_cross_device(self):
        import ctypes
        import errno
        from unittest.mock import Mock
        source = self.root / "native-source"
        target = self.root / "native-target"
        source.mkdir()
        for code in (errno.ENOTSUP, errno.EXDEV):
            with self.subTest(errno=code):
                def fail(*args):
                    ctypes.set_errno(code)
                    return -1
                native = Mock(side_effect=fail)
                with patch.object(installer.ctypes, "CDLL", return_value=Mock(renameatx_np=native)):
                    with patch.object(os, "replace", side_effect=AssertionError("unsafe fallback")):
                        with self.assertRaises(OSError) as raised:
                            installer._rename_noreplace(source, target)
                self.assertEqual(raised.exception.errno, code)
                self.assertTrue(source.exists())
                self.assertFalse(target.exists())
        with patch.object(installer.sys, "platform", "unsupported"):
            with self.assertRaises(installer.InstallError):
                installer._rename_noreplace(source, target)

    def test_mutation_and_sync_interruptions_reconcile_without_deletion(self):
        self.assertTrue(callable(getattr(installer, "_rename_noreplace", None)))
        primitives = ("_rename_noreplace", "_link_noreplace", "_fsync_dir")
        for primitive in primitives:
            original = getattr(installer, primitive)
            calls = []
            def trace(*args):
                calls.append(args)
                return original(*args)
            fixture = InstallerTests("test_manifest_is_literal_nested_source_bytes")
            fixture.setUp()
            try:
                with patch.object(installer, primitive, side_effect=trace):
                    installed = fixture.do_install()
                    self.assertEqual(installer.rollback(installed["receipt"], fixture.state)["status"], "ROLLED_BACK")
            finally:
                fixture.doCleanups()
            for number in range(1, len(calls) + 1):
                for when in ("before", "after"):
                    with self.subTest(primitive=primitive, number=number, when=when):
                        fixture = InstallerTests("test_manifest_is_literal_nested_source_bytes")
                        fixture.setUp()
                        counter = [0]
                        def interrupt(*args):
                            counter[0] += 1
                            chosen = counter[0] == number
                            if chosen and when == "before":
                                raise Interrupted("before mutation/sync")
                            answer = original(*args)
                            if chosen and when == "after":
                                raise Interrupted("after mutation/sync")
                            return answer
                        try:
                            with patch.object(installer, primitive, side_effect=interrupt):
                                with self.assertRaises(Interrupted):
                                    installed = fixture.do_install()
                                    installer.rollback(installed["receipt"], fixture.state)
                            receipts = list(fixture.state.glob("*/receipt.json"))
                            if receipts:
                                self.assertIn(installer.rollback(receipts[0], fixture.state)["status"],
                                              ("ROLLED_BACK", "ALREADY_ROLLED_BACK"))
                            self.assertEqual(fixture.router.read_bytes(), fixture.before)
                            self.assertFalse((fixture.skills / "i2e-team").exists())
                        finally:
                            fixture.doCleanups()

    def test_source_drift_during_staging_remains_recoverable(self):
        write = installer._write_receipt
        def change_source(path, data):
            write(path, data)
            if data["phase"] == "PREPARED":
                (self.package / "SKILL.md").write_text("changed while staging")
        with patch.object(installer, "_write_receipt", side_effect=change_source):
            with self.assertRaises(installer.InstallError):
                self.do_install()
        self.assertEqual(self.router.read_bytes(), self.before)
        self.assertFalse((self.skills / "i2e-team").exists())
        self.assertEqual(installer.rollback(self.receipt_after_interruption(), self.state)["status"],
                         "ROLLED_BACK")

    def test_destination_drift_during_staging_preserves_intervening_edit(self):
        write = installer._write_receipt
        changed = self.before + b"Owner edit during staging\n"
        def change_router(path, data):
            write(path, data)
            if data["phase"] == "STAGED":
                self.router.write_bytes(changed)
        with patch.object(installer, "_write_receipt", side_effect=change_router):
            with self.assertRaises(installer.InstallError):
                self.do_install()
        self.assertEqual(self.router.read_bytes(), changed)
        self.assertFalse((self.skills / "i2e-team").exists())
        self.assertEqual(installer.rollback(self.receipt_after_interruption(), self.state)["status"],
                         "CONFLICT")
        self.assertEqual(self.router.read_bytes(), changed)

    def test_rollback_does_not_remove_target_recreated_after_completed_rollback(self):
        result = self.do_install()
        self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "ROLLED_BACK")
        import shutil
        shutil.copytree(self.package, self.skills / "i2e-team")
        self.assertEqual(installer.rollback(result["receipt"], self.state)["status"], "CONFLICT")
        self.assertEqual(files(self.skills / "i2e-team"), self.expected)
        self.assertEqual(self.router.read_bytes(), self.before)

    def test_receipt_symlink_is_refused(self):
        result = self.do_install()
        receipt = Path(result["receipt"])
        original = receipt.with_name("owner-copy.json")
        receipt.rename(original)
        receipt.symlink_to(original)
        with self.assertRaises(installer.InstallError):
            installer.rollback(receipt, self.state)
        self.assertTrue((self.skills / "i2e-team").exists())

    def test_malformed_phase_types_receive_controlled_refusal(self):
        result = self.do_install()
        receipt = Path(result["receipt"])
        before = json.loads(receipt.read_text())
        for value in ([], {}, None, 42):
            with self.subTest(value=value):
                receipt.write_text(json.dumps({**before, "phase": value}))
                error = None
                try:
                    installer.rollback(receipt, self.state)
                except Exception as exc:
                    error = exc
                self.assertIsInstance(error, installer.InstallError)
        self.assertTrue((self.skills / "i2e-team").exists())

    def test_cli_manifest_install_and_rollback_round_trip(self):
        def cli(*args):
            return subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                                  capture_output=True, text=True)
        manifest = cli("manifest", "--source-root", self.source)
        self.assertEqual(manifest.returncode, 0)
        self.assertEqual(json.loads(manifest.stdout or "{}"), self.expected)
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(manifest.stdout)
        result = cli("install", "--source-root", self.source, "--skills-root", self.skills,
                     "--state-root", self.state, "--manifest", manifest_path,
                     "--expected-router-sha256", sha(self.before))
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = json.loads(result.stdout)
        self.assertEqual(installed["status"], "INSTALLED")
        rolled = cli("rollback", "--receipt", installed["receipt"], "--state-root", self.state)
        self.assertEqual(rolled.returncode, 0, rolled.stderr)
        self.assertEqual(json.loads(rolled.stdout)["status"], "ROLLED_BACK")
        self.assertEqual(self.router.read_bytes(), self.before)


if __name__ == "__main__":
    unittest.main()
