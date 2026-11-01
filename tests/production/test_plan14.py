"""Plano 14 — apresentação final de 12 slides planos, com origem na 2ª carta e texto ancorado no pacote."""
import re
import tempfile
import unittest
from pathlib import Path

from production import consumer, content, deck_model, html_deck


class FinalDeck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = consumer.load(consumer.resolve("latest"))
        cls.m = deck_model.build(cls.b)
        cls._tmp = tempfile.TemporaryDirectory(prefix="prod_p14_")
        cls.html = html_deck.build(cls.m, Path(cls._tmp.name) / "deck.html").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_twelve_pages_in_order_with_voices(self):
        self.assertEqual([p["id"] for p in self.m["pages"]], [f"S{i:02d}" for i in range(1, 13)])
        self.assertEqual([p["voice"] for p in self.m["pages"]], [p["voice"] for p in content.PAGES])
        self.assertLessEqual(sum(p["seconds"] for p in content.PAGES), 600)
        self.assertEqual(len(re.findall(r'<section class="slide', self.html)), 12)

    def test_slides_are_flat(self):
        low = self.html.lower()
        low = low[low.index("<main"):low.index("</main>")]  # marcação dos slides (o autoteste do script cita seletores)
        for tag in ("<button", "<nav", "<input", "<select", "<a ", 'role="button"', "tabindex", "drawer", "tooltip"):
            self.assertNotIn(tag, low, tag)

    def test_origin_matches_letter(self):
        page = next(p for p in self.m["pages"] if p["kind"] == "origin")
        weights = {s["slug"]: (s["fmt"], s["group"]) for s in page["stocks"]}
        self.assertEqual(weights, {"petrobras": ("5%", "view"), "vale": ("5%", "view"), "weg": ("5%", "view"), "suzano": ("5%", "view"),
                                   "bradesco": ("3%", "model"), "sabesp": ("2%", "model")})
        self.assertEqual(page["reason"], "Escolha do modelo (prêmio de risco)")
        self.assertIn("SRC_carta_2a_asset_dev", [s["id"] for s in page["sources"]])

    def test_titles_hold_against_bundle(self):
        self.assertEqual(deck_model.guards(self.b), [])

    def test_model_named_only_in_intro(self):
        for p in self.m["pages"][2:]:
            text = " ".join([p["title"], p["subtitle"], content.SPEECH[p["block"]]])
            self.assertNotRegex(text, r"(?i)black-litterman|modelo de aloca|o modelo\b", p["id"])

    def test_every_number_on_screen_comes_from_bundle(self):
        for p in self.m["pages"]:
            for ref in p["value_refs"]:
                self.assertIn(ref, self.b.obs, (p["id"], ref))


if __name__ == "__main__":
    unittest.main()
