"""Validador do contrato 1.0: aceita o último pacote publicado e recusa cópias corrompidas (sandbox temporária).

Roda sobre o pacote publicado mais recente (latest.json); sem pacote, os testes são pulados.
Cópias são modificadas apenas em diretório temporário; o pacote publicado não é alterado.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from analysis import contract
from analysis.common import REPO

LATEST = REPO / "outputs/draft/analysis_bundle/latest.json"


def published():
    if not LATEST.is_file():
        return None
    p = REPO / json.loads(LATEST.read_text(encoding="utf-8"))["path"]
    return p if (p / "manifest.json").is_file() else None


@unittest.skipIf(published() is None, "nenhum pacote publicado")
class ContractTests(unittest.TestCase):
    def setUp(self):
        self.src = published()
        self.tmp = tempfile.TemporaryDirectory()
        self.copy = Path(self.tmp.name) / self.src.name
        shutil.copytree(self.src, self.copy)

    def tearDown(self):
        self.tmp.cleanup()

    def _manifest(self):
        return json.loads((self.copy / "manifest.json").read_text(encoding="utf-8"))

    def _rehash(self, rel):
        from analysis.common import sha256_file
        man = self._manifest()
        for f in man["files"]:
            if f["path"] == rel:
                f["sha256"] = sha256_file(self.copy / rel)
                f["bytes"] = (self.copy / rel).stat().st_size
        (self.copy / "manifest.json").write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")

    def assertRejected(self, needle):
        rep = contract.validate(self.copy)
        self.assertEqual(rep["status"], "failed")
        self.assertTrue(any(needle in e for e in rep["errors"]), rep["errors"][:5])

    def test_published_bundle_passes(self):
        self.assertEqual(contract.validate(self.src)["status"], "passed")

    def test_missing_file(self):
        (self.copy / "tables/claims.csv").unlink()
        self.assertRejected("ausente")

    def test_tampered_file_hash(self):
        p = self.copy / "LEIA_PRIMEIRO.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nalterado", encoding="utf-8")
        self.assertRejected("hash/bytes divergentes")

    def test_fixture_kind_refused_by_research_loader(self):
        man = self._manifest()
        man["kind"] = "fixture"
        (self.copy / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
        self.assertRejected("recusado")

    def test_unknown_major_version_refused(self):
        man = self._manifest()
        man["schema_version"] = "2.0"
        (self.copy / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
        self.assertRejected("schema_version")

    def test_paper_value_on_invalid_case_refused(self):
        rel = "results/valuation.json"
        d = json.loads((self.copy / rel).read_text(encoding="utf-8"))
        bad = next(c for c in d["cases"] if c["target_validity"] != "conditional_value")
        bad["paper_value"] = 0.0
        (self.copy / rel).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        self._rehash(rel)
        self.assertRejected("paper_value deve ser null")

    def test_nan_rejected(self):
        rel = "results/esg_bridge.json"
        txt = (self.copy / rel).read_text(encoding="utf-8").replace('"schema_version"', '"x": NaN, "schema_version"', 1)
        (self.copy / rel).write_text(txt, encoding="utf-8")
        self._rehash(rel)
        with self.assertRaises(ValueError):
            contract.validate(self.copy)

    def test_unresolved_claim_token(self):
        rel = "tables/claims.csv"
        txt = (self.copy / rel).read_text(encoding="utf-8").replace("{{value:OBS_002588}}", "{{value:V.nao.existe}}", 1)
        (self.copy / rel).write_text(txt, encoding="utf-8")
        self._rehash(rel)
        self.assertRejected("token sem valor")

    def test_adopted_without_human_records(self):
        rel = "results/recommendation.json"
        d = json.loads((self.copy / rel).read_text(encoding="utf-8"))
        d["decision"]["status"] = "adopted"
        (self.copy / rel).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        self._rehash(rel)
        self.assertRejected("registros reais H08/H09")

    def test_missing_narrative_slot(self):
        rel = "results/narrative.json"
        d = json.loads((self.copy / rel).read_text(encoding="utf-8"))
        d["slots"].pop("swot")
        (self.copy / rel).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        self._rehash(rel)
        self.assertRejected("slots devem ser exatamente")


if __name__ == "__main__":
    unittest.main()
