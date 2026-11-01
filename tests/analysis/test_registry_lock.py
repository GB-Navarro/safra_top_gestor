"""Regras de estado/tipo dos valores, claims, trava documental e raízes de escrita."""
import json
import tempfile
import unittest
from pathlib import Path

from analysis import common, lock
from analysis.data import Registry


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.r = Registry("t")

    def test_observed_requires_source(self):
        with self.assertRaises(ValueError):
            self.r.value("V.x", metric_id="m", value=1.0, unit="BRL", value_state="observed", fact_type="fact")

    def test_missing_requires_null_and_reason(self):
        with self.assertRaises(ValueError):
            self.r.value("V.y", metric_id="m", value=0.0, unit="BRL", value_state="missing", fact_type="fact", note="x")
        with self.assertRaises(ValueError):
            self.r.value("V.y", metric_id="m", value=None, unit="BRL", value_state="missing", fact_type="fact")
        self.r.value("V.y", metric_id="m", value=None, unit="BRL", value_state="missing", fact_type="fact", note="não divulgado")

    def test_non_finite_and_conflicting_ids_refused(self):
        with self.assertRaises(ValueError):
            self.r.value("V.z", metric_id="m", value=float("nan"), unit="BRL", value_state="derived", fact_type="derived", calculation_ref="c")
        self.r.value("V.z", metric_id="m", value=1.0, unit="BRL", value_state="derived", fact_type="derived", calculation_ref="c")
        with self.assertRaises(ValueError):
            self.r.value("V.z", metric_id="m", value=2.0, unit="BRL", value_state="derived", fact_type="derived", calculation_ref="c")

    def test_claim_tokens_must_resolve(self):
        with self.assertRaises(KeyError):
            self.r.claim("CL.x", claim_type="inference", text_template="Valor {{value:V.none}}")
        with self.assertRaises(ValueError):
            self.r.claim("CL.f", claim_type="fact", text_template="Sem fonte")

    def test_strict_json_rejects_nan(self):
        with self.assertRaises(ValueError):
            common.dumps({"a": float("inf")})


class LockAndRootTests(unittest.TestCase):
    def test_lock_exclusive_and_owner_release(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "documentation.lock"
            tok = lock.acquire("analysis", "teste", p)
            with self.assertRaises(lock.LockBusy):
                lock.acquire("production", "outra", p)
            forged = dict(tok, pid=-1)
            with self.assertRaises(lock.LockBusy):
                lock.release(forged, p)
            self.assertTrue(p.exists(), "trava ativa de outro dono não pode ser apagada")
            lock.release(tok, p)
            self.assertFalse(p.exists())
            with lock.documentation_lock("analysis", "ctx", p):
                self.assertEqual(json.loads(p.read_text(encoding="utf-8"))["operation"], "ctx")
            self.assertFalse(p.exists())

    def test_writes_outside_exclusive_roots_refused(self):
        for rel in ("data/processed/valuation.json", "ESTADO_DO_PROJETO.md", "resources/modelos_originais/x.xlsx", "scripts/model.py"):
            with self.assertRaises(PermissionError):
                common.assert_writable(common.REPO / rel)
        common.assert_writable(common.REPO / "outputs/qa/analysis/x.json")
        common.assert_writable(common.REPO / "data/catalog/parallel_progress/analysis.json")


if __name__ == "__main__":
    unittest.main()
