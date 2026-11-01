"""Fotografia, conciliação das 64 células e cronograma do precatório (sobre a fotografia mais recente)."""
import unittest

from analysis import assumptions, capital, obligations, reconciliation
from analysis.common import REPO, read_json, sha256_file
from analysis.data import Baseline, Registry
from analysis.snapshot import BASELINE_ROOT, _original_check


def latest_snapshot():
    snaps = sorted((p for p in BASELINE_ROOT.glob("snap_*") if (p / "snapshot.json").is_file()), key=lambda p: (p / "snapshot.json").stat().st_mtime)
    return snaps[-1] if snaps else None


@unittest.skipIf(latest_snapshot() is None, "sem fotografia AN01")
class LineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Baseline(latest_snapshot())
        cls.reg = Registry("t")
        for r in cls.base.csv("data/processed/sources.csv"):
            cls.reg.source(**r)
        cls.reg.source("SRC_an_sabesp_inst_2025")
        cls.rec = reconciliation.build(cls.reg, cls.base, "2026-11-01")

    def test_snapshot_integrity_and_originals(self):
        meta = self.base.meta
        # A fotografia registra o escopo histórico; a checagem atual segue o inventário ativo.
        self.assertGreater(meta["originals"]["checked"], 0)
        active = sum(r["content_policy"] == "preserve_bytes" for r in read_json(REPO / "data/catalog/original_files_manifest.json")["files"])
        self.assertEqual(_original_check(), {"checked": active, "mismatched": []})
        self.assertEqual(meta["originals"]["mismatched"], [])
        for f in meta["files"]:
            if f["role"] in ("input_copy", "derived_extraction"):
                self.assertEqual(sha256_file(self.base.files / f["path"]), f["sha256"], f["path"])

    def test_all_open_cells_have_disposition(self):
        mapping = self.base.csv("data/catalog/cell_issue_mapping.csv")
        self.assertEqual(len(mapping), 64)
        keys = {(m["entity_id"], int(m["year"]), m["cell"]) for m in mapping}
        rows = {(r["entity_id"], int(r["period"]), r["cell"]): r for r in self.rec["rows"] if r["requirement_id"] in ("C02", "C03", "C04", "C05", "C06", "C07")}
        self.assertEqual(keys, set(rows))
        for k in keys:
            self.assertTrue(rows[k]["disposition"] and rows[k]["justification"] and rows[k]["source_refs"], k)

    def test_construction_and_capex_confirmed_exactly(self):
        for r in self.rec["rows"]:
            if r["requirement_id"] in ("C02", "C04"):
                self.assertEqual(r["disposition"], "confirmed", r["reconciliation_id"])
                self.assertLess(abs(r["difference"]), 0.0015)

    def test_sanepar_zero_is_documented_not_filled(self):
        rows = [r for r in self.rec["rows"] if r["requirement_id"] == "C07"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(r["disposition"] == "confirmed_net_presentation" and "margem nula" in r["source_locators"][1] for r in rows))

    def test_recurring_bases_exclude_non_cash_items(self):
        b = self.rec["basis"]["sabesp"]
        rev = self.reg.get(b["revenue_2025"])
        self.assertAlmostEqual(rev, 38092.05 - 14437.363 - (1676.434 - 179.084), places=3)
        self.assertAlmostEqual(self.reg.get(self.rec["basis"]["sanepar"]["ebitda_2025"]), 3101.5)

    def test_capital_events_and_scales(self):
        cap = capital.build(self.reg, self.base)
        self.assertAlmostEqual(self.reg.get(cap["shares"]["copasa"]["total"]), 379.181, places=3)
        self.assertAlmostEqual(self.reg.get(cap["shares"]["sabesp"]["total"]), 3506.830477, places=6)
        self.assertIn("5.000000", cap["events"][0]["reflected_in"])

    def test_precatorio_schedule_consumes_balance_once(self):
        m = assumptions.macro(self.reg, self.base)
        infl = assumptions.inflation_path(self.reg, m)
        base_flows = obligations.precatorio_schedule(self.reg, self.base, infl, "base")
        fav = obligations.precatorio_schedule(self.reg, self.base, infl, "favorable")
        nominal = sum(f["nominal"] for f in base_flows)
        self.assertGreater(nominal, 4407.957)  # atualização por IPCA + 8,08% real
        self.assertLess(abs(sum(f["nominal"] for f in fav) / nominal - 0.75), 0.01)
        comps = {f["component"] for f in base_flows}
        self.assertEqual(comps, {"tariff_discount", "non_onerous_capex"})
        self.assertEqual(max(f["date"] for f in base_flows if f["component"] == "tariff_discount").isoformat()[:7], "2029-05")
        self.assertEqual(max(f["date"] for f in base_flows if f["component"] == "non_onerous_capex").isoformat()[:7], "2030-12")
        # Acréscimo ≈ WACC: PV na data fica próximo do saldo contábil atualizado, não de zero.
        fut, past = obligations.pv_flows(base_flows, 0.1325)
        self.assertGreater(fut + past, 4407.957)
        self.assertLess(fut + past, 4407.957 * 1.10)


if __name__ == "__main__":
    unittest.main()
