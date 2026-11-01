"""Second-engine recalculation of the generated Excel formulas, preserving delivery bytes."""
from __future__ import annotations

import subprocess

import openpyxl

from common import ROOT,now,read_json,sha256,write_json


def recalculate():
    source=ROOT/'outputs/draft/base_modelo_auditavel.xlsx'
    folder=ROOT/'outputs/qa/recalculated';folder.mkdir(parents=True,exist_ok=True)
    executable=r'C:\Program Files\LibreOffice\program\soffice.exe'
    profile=(ROOT/'outputs/qa/lo_calc_profile').as_uri()
    p=subprocess.run([executable,f'-env:UserInstallation={profile}','--headless','--convert-to','xlsx',
        '--outdir',str(folder),str(source)],capture_output=True,text=True,timeout=90,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    target=folder/source.name
    if p.returncode or not target.is_file():raise RuntimeError(p.stdout+p.stderr)
    book=openpyxl.load_workbook(target,data_only=True,read_only=True)
    vals=read_json('data/processed/valuation.json');errors=[];checks=0;max_abs_error=0
    for i,(entity,r) in enumerate(vals.items(),2):
        for col,key in [(6,'terminal_fcff'),(9,'pv_terminal'),(10,'pv_explicit'),(11,'enterprise_value'),
                        (15,'equity_residual_before_floor'),(16,'equity_value'),(18,'average_share_value')]:
            value=book['Terminal'].cell(i,col).value
            if not isinstance(value,(int,float)):errors.append((entity,key,str(value)));continue
            error=abs(value-r['common_base'][key]);max_abs_error=max(max_abs_error,error)
            if error>1e-7:errors.append((entity,key,error))
            checks+=1
    for row in book['Projecoes'].iter_rows(min_row=2):
        f=next(f for f in vals[row[0].value]['common_base']['flows'] if f['year']==row[1].value)
        for col,key in [(12,'nopat'),(13,'full_fcff'),(14,'fcff'),(15,'discounted_fcff')]:
            value=row[col].value
            if not isinstance(value,(int,float)):errors.append((row[0].value,row[1].value,key,str(value)));continue
            error=abs(value-f[key]);max_abs_error=max(max_abs_error,error)
            if error>1e-7:errors.append((row[0].value,row[1].value,key,error))
            checks+=1
    book.close()
    report=dict(created_at=now(),status='passed' if not errors else 'failed',checks=checks,max_absolute_error=max_abs_error,
        errors=errors,delivery_workbook_sha256=sha256(source),recalculated_copy=target.relative_to(ROOT).as_posix(),
        engine='LibreOffice Calc',scope='Recalculable Excel FCFF/terminal formulas vs independent Python values; not economic certification')
    write_json('outputs/qa/workbook_recalculation.json',report)
    print('Independent spreadsheet recalculation',report['status'],checks,'checks; maximum error',max_abs_error)
    if errors:raise ValueError(errors)


if __name__=='__main__':recalculate()
