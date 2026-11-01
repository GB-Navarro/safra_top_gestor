"""EN11/EN03 — duas versões de pacote mudam números sem mudar código; estados incompatíveis são recusados."""
import json
import tempfile
import unittest
from pathlib import Path

from fixture_bundle import edit_json, make, set_value
from production import consumer, deck_model, html_deck

PRICE = "V.SAPR11.close.2026-10-30"


def load_fx(p):
    return consumer.load(p, allow_kinds=("fixture",))


def page(model, pid):
    return next(p for p in model["pages"] if p["id"] == pid)


class TwoVersions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="prod_ver_")
        tmp = Path(cls._tmp.name)
        cls.v1 = load_fx(make(tmp, "v1"))
        cls.v2 = load_fx(make(tmp, "v2", mutate=set_value(PRICE, "33.1")))
        cls.m1, cls.m2 = deck_model.build(cls.v1), deck_model.build(cls.v2)
        cls.h1 = html_deck.build(cls.m1, tmp / "v1.html").read_text(encoding="utf-8")
        cls.h2 = html_deck.build(cls.m2, tmp / "v2.html").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_numbers_follow_bundle(self):
        self.assertEqual(page(self.m1, "P01")["hero"][1]["fmt"], "R$ 30,85")
        self.assertEqual(page(self.m2, "P01")["hero"][1]["fmt"], "R$ 33,10")
        self.assertEqual(page(self.m2, "P10")["ladder"]["price"]["fmt"], "R$ 33,10")
        self.assertIn("R$ 33,10", self.h2)
        self.assertNotIn("R$ 33,10", self.h1)

    def test_same_structure_and_lineage(self):
        self.assertEqual([p["id"] for p in self.m1["pages"]], [p["id"] for p in self.m2["pages"]])
        self.assertEqual(len(self.m1["pages"]), 10)
        self.assertNotEqual(self.m1["bundle_id"], self.m2["bundle_id"])
        self.assertIn(self.m2["bundle_id"], self.h2)

    def test_waterfall_closes(self):
        for m in (self.m1, self.m2):
            for e, comp in page(m, "P07")["companies"].items():
                items = comp["items"]
                gap = items[0]["num"] + sum(i.get("effect_num", 0) for i in items[1:-1]) - items[-1]["num"]
                self.assertLess(abs(gap), 1e-6, e)

    def test_html_offline(self):
        low = self.h1.lower()
        for marker in ('src="http', "src='http", 'href="http', "@import", "url(http"):
            self.assertNotIn(marker, low)

    def test_every_page_has_sources_and_refs_resolve(self):
        for p in self.m1["pages"]:
            self.assertTrue(p["sources"], p["id"])
            for ref in p["value_refs"]:
                self.assertIn(ref, self.v1.obs, (p["id"], ref))


class IncompatibleStates(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="prod_state_")
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_unresolved_decision_refuses_deck(self):
        def fn(o):
            o["decision"].update(status="unresolved", entity_id=None, instrument_id=None)
        b = load_fx(make(self.tmp, "unresolved", mutate=lambda d: edit_json(d, "results/recommendation.json", fn)))
        with self.assertRaises(consumer.IncompatibleState):
            deck_model.build(b)

    def test_decision_without_target_refuses_deck(self):
        def fn(o):
            c = next(c for c in o["cases"] if c["case_id"] == "sanepar.base")
            c.update(target_validity="no_meaningful_target", paper_value=None)
        b = load_fx(make(self.tmp, "notarget", mutate=lambda d: edit_json(d, "results/valuation.json", fn)))
        with self.assertRaises(consumer.IncompatibleState):
            deck_model.build(b)

    def test_non_positive_residual_shows_na_not_zero(self):
        def fn(o):
            c = next(c for c in o["cases"] if c["case_id"] == "copasa.base")
            c.update(target_validity="no_meaningful_target", paper_value=None)
        b = load_fx(make(self.tmp, "copasa_na", mutate=lambda d: edit_json(d, "results/valuation.json", fn)))
        m = deck_model.build(b)
        cop = next(c for c in page(m, "P01")["compare"] if c["entity"] == "copasa")
        self.assertEqual(cop["value"]["fmt"], "N/D")
        self.assertIsNone(cop["value"]["num"])
        self.assertIn("Resíduo", cop["value"]["why"])

    def test_real_bundle_has_na_case_in_scenarios(self):
        m = deck_model.build(consumer.load(consumer.resolve("latest")))
        vals = [v for sc in page(m, "P09")["scenarios"].values() for v in sc["values"].values()]
        self.assertTrue(all((v["num"] is None) == (v["fmt"] == "N/D") for v in vals))


if __name__ == "__main__":
    unittest.main()
