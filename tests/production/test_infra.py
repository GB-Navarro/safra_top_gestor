"""Raízes de escrita, trava documental, adaptador baseline e interação do HTML no navegador."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from production import adapter, browser, common, consumer, deck_model, html_deck
from production.common import REPO


class WriteRoots(unittest.TestCase):
    def test_bundle_immutable_even_when_publishing(self):
        with self.assertRaises(PermissionError):
            common.writable(REPO / "outputs/draft/analysis_bundle/x/manifest.json", publishing=True)

    def test_canonical_targets_need_integrator(self):
        with self.assertRaises(PermissionError):
            common.writable(REPO / "data/processed/observations.csv")
        self.assertTrue(common.writable(REPO / "data/processed/observations.csv", publishing=True))

    def test_part1_roots_refused(self):
        for rel in ("analysis/run.py", "data/interim/analysis/x.json", "ESTADO_DO_PROJETO.md"):
            with self.assertRaises(PermissionError, msg=rel):
                common.writable(REPO / rel, publishing=True)

    def test_own_roots_allowed(self):
        common.writable(REPO / "outputs/draft/production/x/y.json")
        common.writable(REPO / "tests/production/x.py")


class Lock(unittest.TestCase):
    def test_exclusive_and_owner_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "documentation.lock"
            tok = common.acquire("production", "teste", path)
            with self.assertRaises(common.LockBusy):
                common.acquire("analysis", "concorrente", path)
            with self.assertRaises(common.LockBusy):
                common.release(dict(tok, pid=-1), path)
            common.release(tok, path)
            self.assertFalse(path.exists())
            with common.documentation_lock("ctx", path):
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["owner"], "production")
            self.assertFalse(path.exists())


class BaselineAdapter(unittest.TestCase):
    def test_baseline_is_draft_only(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(adapter, "OUT", Path(tmp)):
            p = adapter.adapt()
            self.assertEqual(consumer.validate(p, allow_kinds=("baseline",)), [])
            self.assertTrue(any("kind 'baseline'" in e for e in consumer.validate(p)))
            man = json.loads((p / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(man["state"], "baseline_unreconciled")
            cases = json.loads((p / "results/valuation.json").read_text(encoding="utf-8"))["cases"]
            self.assertTrue(cases and all(c["target_validity"] == "unresolved" and c["paper_value"] is None for c in cases))


@unittest.skipUnless(browser.executable(), "Edge/Chrome ausente")
class BrowserInteraction(unittest.TestCase):
    def test_selftest_both_resolutions(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = deck_model.build(consumer.load(consumer.resolve("latest")))
            html = html_deck.build(m, Path(tmp) / "deck.html")
            for w, h in ((1920, 1080), (1366, 768)):
                r = browser.selftest(html, w, h)
                self.assertEqual(r["status"], "passed", [c for c in r["checks"] if not c["pass"]])
                self.assertGreaterEqual(len(r["checks"]), 30)


if __name__ == "__main__":
    unittest.main()
