"""Plano 14: carteira da 2ª carta como ponto de partida, lida do original e publicada no pacote."""
import csv
import json
import unittest

from analysis.common import REPO, read_json, sha256_file
from analysis.origin import LETTER


def latest():
    ptr = REPO / "outputs/draft/analysis_bundle/latest.json"
    return REPO / "outputs/draft/analysis_bundle" / read_json(ptr)["bundle_id"] if ptr.is_file() else None


B = latest()
HAS = bool(B) and (B / "tables/observations.csv").is_file() and "V.carta2.weight.sabesp" in (B / "tables/observations.csv").read_text(encoding="utf-8")


@unittest.skipUnless(HAS, "pacote vigente ainda sem a origem da 2ª carta")
class LetterOrigin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = {r["value_id"]: r for r in csv.DictReader(open(B / "tables/observations.csv", encoding="utf-8"))}
        cls.claims = {r["claim_id"]: r for r in csv.DictReader(open(B / "tables/claims.csv", encoding="utf-8"))}
        cls.slots = read_json(B / "results/narrative.json")["slots"]

    def test_weights_match_letter_table(self):
        expected = {"petrobras": 0.05, "vale": 0.05, "weg": 0.05, "suzano": 0.05, "bradesco": 0.03, "sabesp": 0.02}
        for slug, w in expected.items():
            o = self.obs[f"V.carta2.weight.{slug}"]
            self.assertAlmostEqual(float(o["value"]), w, msg=slug)
            self.assertEqual(o["value_state"], "observed")
            self.assertIn("SRC_carta_2a_asset_dev", o["source_refs"])
        self.assertIn("Escolha do modelo (prêmio de risco)", self.obs["V.carta2.weight.sabesp"]["note"])

    def test_origin_claim_opens_lead_slot(self):
        self.assertEqual(self.slots["lead"][0], "CL.lead.origin")
        self.assertEqual(self.claims["CL.lead.origin"]["claim_type"], "fact")

    def test_letter_copy_is_byte_identical_to_original(self):
        snap = REPO / "data/interim/analysis/baseline" / read_json(B / "metadata.json")["snapshot_id"]
        self.assertEqual(sha256_file(snap / "files" / LETTER), sha256_file(REPO / LETTER))
        manifest = read_json(REPO / "data/catalog/original_files_manifest.json")["files"]
        entry = next(f for f in manifest if f["current_path"] == LETTER)
        self.assertEqual(entry["sha256"], sha256_file(REPO / LETTER))


if __name__ == "__main__":
    unittest.main()
