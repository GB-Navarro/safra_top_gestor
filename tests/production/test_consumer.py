"""EN02 — consumidor do contrato 1.0: aceita o pacote publicado e rejeita versões/arquivos/referências inválidos."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from fixture_bundle import edit_csv, edit_json, make, rehash, set_value
from production import consumer
from production.consumer import format_value

PRICE = "V.SAPR11.close.2026-10-30"


class PublishedBundle(unittest.TestCase):
    def test_latest_is_valid_analysis(self):
        path = consumer.resolve("latest")
        self.assertEqual(consumer.validate(path), [])
        b = consumer.load(path)
        self.assertEqual(b.manifest["kind"], "analysis")
        self.assertIn(b.manifest["state"], consumer.STATES)

    def test_pointer_hash_checked(self):
        # resolve('latest') compara o hash do manifesto com o ponteiro; o pacote atual precisa conferir
        self.assertTrue((consumer.resolve("latest") / "manifest.json").is_file())


class Rejections(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="prod_fx_")
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def errs(self, path, kinds=("fixture",)):
        return " | ".join(consumer.validate(path, allow_kinds=kinds))

    def test_fixture_refused_by_default_loader(self):
        p = make(self.tmp, "ok")
        self.assertEqual(consumer.validate(p, allow_kinds=("fixture",)), [])
        self.assertIn("kind 'fixture' não aceito", self.errs(p, ("analysis",)))
        with self.assertRaises(consumer.BundleRejected):
            consumer.load(p)

    def test_major_version_refused(self):
        p = make(self.tmp, "v2", schema_version="2.0")
        self.assertIn("versão major incompatível", self.errs(p))

    def test_tampered_file_refused(self):
        p = make(self.tmp, "tamper")
        with open(p / "tables/observations.csv", "a", encoding="utf-8") as f:
            f.write("\n")
        self.assertIn("hash/bytes divergentes: tables/observations.csv", self.errs(p))

    def test_path_escape_refused(self):
        p = make(self.tmp, "escape")
        man = json.loads((p / "manifest.json").read_text(encoding="utf-8"))
        man["files"].append({"path": "../fora.csv", "bytes": 0, "sha256": "0" * 64})
        (p / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
        self.assertIn("caminho fora da raiz", self.errs(p))

    def test_missing_file_refused(self):
        p = make(self.tmp, "missing", mutate=lambda d: (d / "results/narrative.json").unlink())
        self.assertIn("arquivo ausente: results/narrative.json", self.errs(p))

    def test_slot_claim_missing_refused(self):
        def drop(d):
            slot_claim = json.loads((d / "results/narrative.json").read_text(encoding="utf-8"))["slots"]["lead"][0]
            edit_csv(d, "tables/claims.csv", lambda rows: [r for r in rows if r["claim_id"] != slot_claim])
        p = make(self.tmp, "noclaim", mutate=drop)
        self.assertIn("slot lead: claim", self.errs(p))

    def test_source_missing_refused(self):
        def drop(d):
            price = next(r for r in consumer._csv(d / "tables/observations.csv") if r["value_id"] == PRICE)
            used = consumer._jl(price["source_refs"])[0]
            edit_csv(d, "tables/sources.csv", lambda rows: [r for r in rows if r["source_id"] != used])
        p = make(self.tmp, "nosource", mutate=drop)
        self.assertIn(f"{PRICE}: fonte", self.errs(p))

    def test_missing_column_refused(self):
        def drop(d):
            rows = consumer._csv(d / "tables/claims.csv")
            header = [k for k in rows[0] if k != "source_refs"]
            with open(d / "tables/claims.csv", "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore", lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
        p = make(self.tmp, "nocol", mutate=drop)
        self.assertIn("tables/claims.csv: colunas ausentes ['source_refs']", self.errs(p))

    def test_bad_number_format_refused(self):
        p = make(self.tmp, "badnum", mutate=set_value(PRICE, "30,85"))
        self.assertIn(f"{PRICE}: valor inválido", self.errs(p))

    def test_missing_state_with_number_refused(self):
        p = make(self.tmp, "missnum", mutate=set_value(PRICE, "30.85", value_state="missing"))
        self.assertIn(f"{PRICE}: ausente com número", self.errs(p))

    def test_display_value_without_validity_refused(self):
        def flip(d):
            def fn(o):
                c = next(c for c in o["cases"] if c["case_id"] == "copasa.base")
                c["target_validity"] = "no_meaningful_target"  # paper_value continua numérico: deve ser recusado
            edit_json(d, "results/valuation.json", fn)
        p = make(self.tmp, "validity", mutate=flip)
        self.assertIn("copasa.base: valor exibível sem validade", self.errs(p))

    def test_adopted_without_human_records_refused(self):
        def adopt(d):
            def fn(o):
                o["decision"]["status"], o["decision"]["human_record_refs"] = "adopted", []
            edit_json(d, "results/recommendation.json", fn)
        p = make(self.tmp, "adopt", mutate=adopt)
        self.assertIn("decisão adotada sem registros humanos", self.errs(p))

    def test_rehash_restores_validity(self):
        p = make(self.tmp, "rehash")
        (p / "LEIA_PRIMEIRO.md").write_text("alterado\n", encoding="utf-8")
        self.assertTrue(self.errs(p))
        rehash(p)
        self.assertEqual(self.errs(p), "")


class Formatting(unittest.TestCase):
    def test_pt_br_formats(self):
        self.assertEqual(format_value(4577.8, "BRL", 1e6), "R$ 4,6 bi")
        self.assertEqual(format_value(4577.8, "BRL", 1e6, "precise"), "R$ 4.577,8 mi")
        self.assertEqual(format_value(-1180.1, "BRL", 1e6, "precise"), "R$ −1.180,1 mi")  # sinal tipográfico de menos
        self.assertEqual(format_value(-0.354, "ratio", style="signed1"), "−35,4%")
        self.assertEqual(format_value(30.85, "BRL/unit"), "R$ 30,85")
        self.assertEqual(format_value(0.1325, "ratio"), "13,25%")
        self.assertEqual(format_value(0.388, "ratio", style="signed1"), "+38,8%")
        self.assertEqual(format_value(2, "years"), "2 anos")
        self.assertEqual(format_value(1, "years"), "1 ano")
        self.assertEqual(format_value(None, "BRL/unit"), "N/D")
        self.assertEqual(format_value(2026, "year"), "2026")


if __name__ == "__main__":
    unittest.main()
