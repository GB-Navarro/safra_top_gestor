"""Plano 13: fotografia derivada, fontes primárias novas e correções factuais no pacote publicado."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from analysis import run
from analysis.common import REPO, read_json, sha256_file
from analysis.snapshot import BASELINE_ROOT, derive_snapshot

PARENT = BASELINE_ROOT / "snap_20261031_2cf3206ead"
NEW_SOURCES = ["data/raw/analysis/urae1/urae1_anexo_viii_formacao_tarifa_inicial_apostilado.pdf",
               "data/raw/analysis/agepar/agepar_nt_006_2025_3rtp_sanepar.pdf",
               "data/raw/analysis/copasa/copasa_fato_relevante_20260611_preco_oferta.pdf",
               "data/raw/analysis/sanepar/sanepar_fato_relevante_20261028_sainp.pdf"]


def latest_bundle() -> Path | None:
    ptr = REPO / "outputs/draft/analysis_bundle/latest.json"
    return REPO / "outputs/draft/analysis_bundle" / read_json(ptr)["bundle_id"] if ptr.is_file() else None


@unittest.skipUnless((PARENT / "snapshot.json").is_file(), "fotografia-mãe ausente nesta cópia")
class DerivedSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="an_derive_")
        cls.snap = derive_snapshot(PARENT, baseline_root=Path(cls._tmp.name))
        cls.meta = read_json(cls.snap / "snapshot.json")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_processed_inputs_come_from_parent_not_published_outputs(self):
        parent = {e["path"]: e["sha256"] for e in read_json(PARENT / "snapshot.json")["files"]}
        processed = [e for e in self.meta["files"] if e["path"].startswith("data/processed/") and e["role"] == "input_copy"]
        self.assertTrue(processed)
        for e in processed:
            self.assertEqual(e["sha256"], parent[e["path"]], e["path"])
            self.assertEqual(sha256_file(self.snap / "files" / e["path"]), parent[e["path"]], e["path"])

    def test_new_primary_sources_added_and_extracted(self):
        self.assertEqual(self.meta["derived_from"], "snap_20261031_2cf3206ead")
        for rel in NEW_SOURCES:
            self.assertIn(rel, self.meta["added_or_refreshed"])
            self.assertTrue((self.snap / "files" / rel).is_file(), rel)
        for doc in ("urae1_anexo_viii", "agepar_nt_006_2025", "copasa_fr_20260611", "sanepar_fr_20261028_sainp"):
            self.assertTrue((self.snap / "files/derived/pdf_text" / f"{doc}.json").is_file(), doc)
        self.assertEqual(self.meta["originals"]["mismatched"], [])


class NewSnapshotGuard(unittest.TestCase):
    @unittest.skipUnless((REPO / "data/processed/CANONICAL_SOURCE.json").is_file(), "fonte canônica ainda legada")
    def test_new_snapshot_refused_after_contract_publication(self):
        with self.assertRaises(SystemExit):
            run.main(["--baseline", "new"])


@unittest.skipUnless(latest_bundle() and "derived_from" in read_json(
    REPO / "data/interim/analysis/baseline" / read_json(latest_bundle() / "metadata.json")["snapshot_id"] / "snapshot.json"),
    "pacote publicado ainda não é da fotografia derivada")
class PublishedCorrections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = latest_bundle()
        cls.obs = {r["value_id"]: r for r in csv.DictReader(open(b / "tables/observations.csv", encoding="utf-8"))}
        cls.claims = {r["claim_id"]: r for r in csv.DictReader(open(b / "tables/claims.csv", encoding="utf-8"))}
        cls.cases = {c["case_id"]: c for c in read_json(b / "results/valuation.json")["cases"]}
        cls.matrix = read_json(b / "results/esg_matrix.json")["rows"]
        cls.terms = list(csv.DictReader(open(b / "tables/regulatory_terms.csv", encoding="utf-8")))

    def test_copasa_privatization_is_concluded_not_ongoing(self):
        texts = [c["text_template"] + " " + c["limitations"] for c in self.claims.values()]
        texts += [json.dumps(r, ensure_ascii=False) for r in self.matrix]
        self.assertFalse([t for t in texts if "em andamento" in t and "desestatiza" in t])
        self.assertAlmostEqual(float(self.obs["V.copasa.reference_investor_share"]["value"]), 114075921 / 379181000)
        self.assertIn("desestatizada em jun/2026", json.dumps(self.matrix, ensure_ascii=False))

    def test_copasa_finite_case_resolved_by_weighted_term(self):
        self.assertEqual(self.obs["V.copasa.concession_end_year"]["value_state"], "derived")
        self.assertEqual(float(self.obs["V.copasa.concession_end_year"]["value"]), 2055.0)
        self.assertEqual(self.cases["copasa.terminal_finite"]["target_validity"], "conditional_value")

    def test_sabesp_regulatory_wacc_primary_source(self):
        o = self.obs["V.sabesp.wacc_reg_real_after_tax"]
        self.assertEqual((o["value_state"], float(o["value"])), ("observed", 0.0786))
        self.assertIn("SRC_urae1_anexo_viii_2025", o["source_refs"])
        term = next(t for t in self.terms if t["term_id"] == "REG.sabesp.urae1")
        self.assertEqual(term["review_status"], "verified_primary")

    def test_sanepar_brr_check_is_consistent_and_not_substitution(self):
        imp = float(self.obs["V.sanepar.implied_base.2025"]["value"])
        upd = float(self.obs["V.sanepar.brr_official_net.2024_at_2025_prices"]["value"])
        gap = float(self.obs["V.sanepar.implied_vs_official_brr"]["value"])
        self.assertAlmostEqual(gap, imp / upd - 1)
        self.assertLess(abs(gap), 0.25)  # ordem de grandeza; não é teste de precisão
        self.assertIn("CL.method.brr_check", self.claims)
        # base-case values unchanged by the verification
        self.assertAlmostEqual(float(self.obs["V.case.sanepar.base.paper_value"]["value"]), 42.821190056828854, places=6)


if __name__ == "__main__":
    unittest.main()
