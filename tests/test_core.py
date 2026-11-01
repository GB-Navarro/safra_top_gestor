"""Material regressions: provenance, dates, class allocation and DCF mathematics."""
import sys
import unittest
from copy import deepcopy
from datetime import date
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from common import read_csv,read_json
from model import account,allocate_sanepar,value,MODEL_NAMES
from prepare_analysis import brnumber


def legacy_processed_json(test,name):
    """Saída do pipeline legado. Depois da publicação do contrato 1.0 (CANONICAL_SOURCE.json), data/processed
    passa a ter o esquema do pacote; o esquema legado continua testado na fotografia preservada da Parte 2."""
    root=Path(__file__).resolve().parents[1]
    if not (root/'data/processed/CANONICAL_SOURCE.json').is_file():return read_json(f'data/processed/{name}')
    snaps=sorted((root/'data/interim/production/baseline').glob(f'legacy_*/files/data/processed/{name}'))
    if not snaps:test.skipTest('fonte canônica é o contrato 1.0 e a fotografia legada não está nesta cópia')
    return read_json(snaps[0].relative_to(root).as_posix())


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models=read_json("data/interim/original_models.json")

    def test_reproduce_three_original_calculations(self):
        for name in MODEL_NAMES.values():
            model=self.models[name]
            result=value(model)
            self.assertAlmostEqual(result['average_share_value'],model['cells']['TIR']['B42']['cached'],places=8)

    def test_constant_cash_flow_known_solution(self):
        model=deepcopy(self.models[MODEL_NAMES['sanepar']])
        def put(sheet,cell,v):model['cells'][sheet][cell]={'cached':v}
        for cell,v in [('C9',.10),('C10',0),('C8',0),('C13',1),('C6','2025-12-31T00:00:00'),('C7',1)]:put('Premissas',cell,v)
        for cell,v in [('G21',100),('G27',0),('C44',0),('C42',0),('C39',10)]:put('Dados_RI',cell,v)
        for col in 'CDEFGHIJKL':
            for row,v in [(17,0),(18,0),(19,0),(20,.2),(21,.1),(22,.1),(23,0)]:put('Premissas',col+str(row),v)
            put('Dados_RI',col+'34',None)
        result=value(model)
        times=[(date(y,12,31)-date(2025,12,31)).days/365 for y in range(2026,2036)]
        # Revenue 100, EBITDA 20, D&A 10, capex 10, tax/WC zero:
        # FCFF = 10 + 10 - 10 = 10; terminal FCFF/growth = 10/0.10.
        expected=sum(10/1.1**t for t in times)+100/1.1**times[-1]
        self.assertAlmostEqual(result['enterprise_value'],expected,places=9)
        self.assertTrue(all(abs(r['full_fcff']-10)<1e-9 for r in result['flows']))

    def test_invalid_terminal_fails(self):
        with self.assertRaises(ValueError):value(self.models[MODEL_NAMES['sanepar']],{'wacc':.035,'g':.035})

    def test_terminal_reinvestment_identity(self):
        model=self.models[MODEL_NAMES['sanepar']]
        r=value(model,{'terminal_method':'roic','terminal_roic':.125,'g':.035})
        f=r['flows'][-1]
        ebit=(f['revenue']*f['margin']-f['depreciation'])*1.035
        nopat=ebit-max(ebit,0)*r['tax']
        self.assertAlmostEqual(r['terminal_fcff'],nopat*(1-.035/.125),places=8)

    def test_partial_year_already_implemented(self):
        for name in MODEL_NAMES.values():self.assertAlmostEqual(value(self.models[name])['flows'][0]['partial_factor'],62/365)

    def test_limited_liability_not_negative_share_price(self):
        r=value(self.models[MODEL_NAMES['sanepar']],{'extra_obligations':1e9})
        self.assertLess(r['equity_residual_before_floor'],0)
        self.assertEqual(r['equity_value'],0)
        self.assertTrue(r['equity_floor_applied'])

    def test_share_classes_conserve_equity(self):
        prices=allocate_sanepar(10000)
        self.assertAlmostEqual(prices['SAPR3']*503.735259+prices['SAPR4']*1007.470260,10000,places=8)
        self.assertAlmostEqual(prices['SAPR11'],prices['SAPR3']+4*prices['SAPR4'])

    def test_unknown_account_does_not_become_zero(self):
        with self.assertRaises(ValueError):account('sanepar','2.99.99')

    def test_brazilian_price_parser(self):
        self.assertEqual(brnumber('R$ 30,85'),30.85)
        self.assertEqual(brnumber('R$ 1.234,56'),1234.56)

    def test_cvm_per_share_subtree_is_not_currency_millions(self):
        rows=read_csv('data/processed/cvm_accounts.csv')
        eps=[r for r in rows if r['statement']=='DRE' and r['account_code'].startswith('3.99')]
        self.assertTrue(eps)
        self.assertTrue(all(r['value_brl_million']=='' and r['value_unit']=='BRL_per_share_source_raw' for r in eps))

    def test_forecast_observation_date_is_snapshot(self):
        rows=[r for r in read_csv('data/processed/observations.csv') if r['metric_id']=='ipca_expectation']
        self.assertEqual(len(rows),5)
        self.assertTrue(all(r['observed_at']=='2026-10-23' for r in rows))

    def test_selected_workbooks_match_primary_annual_checks(self):
        rows=[r for r in read_csv('outputs/qa/workbook_input_checks.csv') if r['workbook']!='TIR_Sabesp.xlsx']
        self.assertEqual(len(rows),45)
        self.assertTrue(all(abs(float(r['difference']))<=.1 for r in rows))

    def test_energy_scope_and_retention_linearity(self):
        for r in legacy_processed_json(self,'esg_bridge.json'):
            self.assertAlmostEqual(r['capex_break_even_upper'],sum(x['pv'] for x in r['years']))
            self.assertAlmostEqual(r['capex_break_even_50pct_retention'],.5*r['capex_break_even_upper'])
            self.assertEqual([x['year'] for x in r['years']],list(range(2027,2036)))
            self.assertIn('not achieved',r['interpretation'])


if __name__=='__main__':unittest.main()
