"""Motor FCFF revisado, ponte EV→acionista e convenções de data (solução conhecida)."""
import unittest
from datetime import date

from analysis import dcf


def params(**kw):
    infl = {y: 0.0 for y in range(2024, 2036)}
    base = dict(entity="x", ebitda0=150.0, da0=50.0, revenue0=300.0, wc_ratio=0.0, r_pre=0.10, r_post=0.10, tax=0.0, lag=1, share=1.0,
                opex_shock=0.0, eligible=1.0, capex_plan={}, capex_hist={2023: 50.0, 2024: 50.0, 2025: 50.0}, infl=infl, g_real=0.0, wacc=0.10)
    base.update(kw)
    return dcf.Params(**base)


class EngineTests(unittest.TestCase):
    def test_steady_state_known_solution(self):
        # B0 = EBIT/r = 1000; δ = 5%; capex = δ·K mantém a base constante: FCFF = r·B0 = 100 em todos os anos.
        out = dcf.run(params())
        self.assertAlmostEqual(out["b0"], 1000.0)
        self.assertAlmostEqual(out["delta"], 0.05)
        for r in out["rows"]:
            self.assertAlmostEqual(r["fcff"], 100.0, places=9)
        times = [dcf.STUB_FRACTION / 2] + [(date(y, 7, 1) - dcf.VALUATION).days / 365 for y in range(2027, 2036)]
        weights = [dcf.STUB_FRACTION] + [1.0] * 9
        explicit = sum(100 * w / 1.1 ** t for w, t in zip(weights, times))
        t_end = (date(2035, 12, 31) - dcf.VALUATION).days / 365
        self.assertAlmostEqual(out["pv_explicit"], explicit, places=9)
        self.assertAlmostEqual(out["pv_terminal"], (100 / 0.10) / 1.1 ** t_end, places=9)
        # Retorno regulado igual ao WACC: R$ 1 de base vale R$ 1.
        self.assertAlmostEqual(out["rab_value_ratio"], 1.0)

    def test_regulated_capex_value_neutral_when_return_equals_wacc(self):
        # Capex extra (ano cheio, 2027) remunerado a r = WACC tem VPL pequeno frente ao investimento; com r < WACC, VPL negativo.
        neutral = dcf.run(params(capex_plan={2027: 500.0}))
        base = dcf.run(params())
        self.assertLess(abs(neutral["enterprise_value"] - base["enterprise_value"]) / 500.0, 0.10)
        low = dcf.run(params(capex_plan={2027: 500.0}, wacc=0.12))
        low_base = dcf.run(params(wacc=0.12))
        self.assertLess(low["enterprise_value"], low_base["enterprise_value"])

    def test_wacc_must_exceed_growth(self):
        with self.assertRaises(ValueError):
            dcf.run(params(wacc=0.02, g_real=0.03))

    def test_finite_requires_horizon(self):
        with self.assertRaises(ValueError):
            dcf.run(params(terminal="finite", finite_years=None))
        finite = dcf.run(params(terminal="finite", finite_years=200, indemnity=0.0))
        perp = dcf.run(params())
        self.assertAlmostEqual(finite["terminal_value"], perp["terminal_value"], delta=1e-3 * perp["terminal_value"])

    def test_nonpositive_ebit_is_refused(self):
        with self.assertRaises(ValueError):
            dcf.run(params(ebitda0=40.0))

    def test_bridge_arithmetic_and_dates(self):
        self.assertAlmostEqual(dcf.STUB_FRACTION, 62 / 365)
        self.assertAlmostEqual(dcf.ROLLFORWARD_FRACTION, 122 / 365)
        b = dcf.bridge(ev=1000, fcff_2026_full=-365, net_debt_june=300, debt_like=50, grantor=100, grantor_ratio=0.9, obligation_pv=20)
        self.assertAlmostEqual(b["net_debt_october_estimate"], 300 + 122)
        self.assertAlmostEqual(b["equity_residual"], 1000 - 422 - 50 - 100 + 90 - 20)


if __name__ == "__main__":
    unittest.main()
