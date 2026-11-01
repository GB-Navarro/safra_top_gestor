"""EN10 — portões por estágio: sucesso só com evidência completa (injetada na sandbox) e motivos explícitos na recusa."""
import json
import tempfile
import unittest
from pathlib import Path

from production import publish, release
from production.common import REPO

FULL = {"bundle_valid": True, "bundle_state": "group_adopted", "bundle_qa": "passed", "open_dispositions": [], "decision_status": "adopted",
        "human_records": ["fixture:H08", "fixture:H09"], "production_qa": "passed", "visual_review": release.VISUAL_OK,
        "h07_records": ["fixture_h07.md"], "rehearsals_logged": 2,
        "clips_ready": True, "video_reviewed_record": "fixture/video_review.json", "submission_receipt": "fixture/comprovante.json"}


class Gates(unittest.TestCase):
    def test_success_path_with_injected_evidence(self):
        self.assertTrue(all(g["passed"] for g in release.report(dict(FULL))))

    def test_proposal_without_human_adoption(self):
        ev = dict(FULL, bundle_state="analysis_proposed", decision_status="proposed", human_records=[])
        g = {r["stage"]: r for r in release.report(ev)}
        self.assertTrue(g["data_factual"]["passed"] and g["analysis_proposal"]["passed"])
        for st in ("group_material", "video_submission", "sent"):
            self.assertFalse(g[st]["passed"])
            self.assertTrue(any("H08/H09" in r for r in g[st]["reasons"]))

    def test_each_human_record_is_required(self):
        for key, stage, needle in (("h07_records", "video_submission", "H07"), ("rehearsals_logged", "video_submission", "H10"),
                                   ("clips_ready", "video_submission", "H11"), ("video_reviewed_record", "video_submission", "revisão integral"),
                                   ("submission_receipt", "sent", "H13")):
            ev = dict(FULL, **{key: 0 if key == "rehearsals_logged" else None})
            r = release.evaluate(stage, ev)
            self.assertFalse(r["passed"], key)
            self.assertTrue(any(needle in x for x in r["reasons"]), (key, r["reasons"]))

    def test_invalid_bundle_blocks_everything(self):
        ev = dict(FULL, bundle_valid=False)
        self.assertFalse(any(g["passed"] for g in release.report(ev)))

    def test_piece_qa_required_for_group_material(self):
        r = release.evaluate("group_material", dict(FULL, production_qa="failed"))
        self.assertFalse(r["passed"])

    def test_visual_review_required_and_must_match_hashes(self):
        for v in (None, "stale_for_current_artifacts"):
            r = release.evaluate("group_material", dict(FULL, visual_review=v))
            self.assertFalse(r["passed"])
            self.assertTrue(any("revisão visual" in x for x in r["reasons"]))

    def test_real_workspace_never_claims_unrecorded_steps(self):
        ev = release.collect()
        if not ev["submission_receipt"]:
            self.assertFalse(release.evaluate("sent", ev)["passed"])
        if ev["decision_status"] != "adopted":
            self.assertFalse(release.evaluate("group_material", ev)["passed"])

    def test_unknown_stage(self):
        with self.assertRaises(ValueError):
            release.evaluate("final", FULL)


class BannerTolerance(unittest.TestCase):
    def test_only_status_banner_is_tolerated(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, pub = Path(tmp) / "src.md", Path(tmp) / "pub.md"
            src.write_text("# T\n\nCorpo\n", encoding="utf-8")
            pub.write_text("# T\r\n\r\n<!-- PROJECT_STATUS:START -->\r\n> aviso\r\n<!-- PROJECT_STATUS:END -->\r\n\r\nCorpo\r\n", encoding="utf-8", newline="")
            self.assertTrue(publish._same_without_banner(pub, src))
            pub.write_text("# T\n\n<!-- PROJECT_STATUS:START -->\n<!-- PROJECT_STATUS:END -->\n\nOutro corpo\n", encoding="utf-8")
            self.assertFalse(publish._same_without_banner(pub, src))


@unittest.skipUnless((REPO / "outputs/draft/production/published.json").is_file(), "nenhuma publicação canônica ainda")
class FinalPromotion(unittest.TestCase):
    """Sandbox: destino e trava temporários; evidência injetada só aqui, nunca nos registros reais."""

    def test_blocked_without_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = publish.promote_final("group_material", dict(FULL, human_records=[], decision_status="proposed"), Path(tmp) / "final",
                                      Path(tmp) / "doc.lock")
            self.assertFalse(r["promoted"])
            self.assertFalse((Path(tmp) / "final").exists())

    def test_success_path_in_sandbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = publish.promote_final("group_material", dict(FULL), Path(tmp) / "final", Path(tmp) / "doc.lock")
            self.assertTrue(r["promoted"])
            self.assertFalse(r["submitted"])
            man = json.loads((Path(tmp) / "final/manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(man["submitted"])
            self.assertTrue((Path(tmp) / "final/apresentacao_esg.pdf").is_file())
            self.assertTrue((Path(tmp) / "final/html/apresentacao_esg.html").is_file())


if __name__ == "__main__":
    unittest.main()
