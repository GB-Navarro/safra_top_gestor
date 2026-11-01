"""Persist actual completion, gaps and human dependencies across sessions."""
from common import ROOT, acquisitions, now, read_csv, read_json, write_csv, write_json


def initialize_status(row,status,note=None):
    """Seed legacy templates, preserving later evidence and human decisions."""
    placeholders={'','not_started','requires_human','awaiting_export','awaiting_agent_draft',
        'awaiting_presentation_draft','awaiting_rehearsal','conditional_not_requested',
        'awaiting_final_video','method_redefined_pending_data','discovery_only'}
    if row.get('status','') in placeholders:
        row['status']=status
        if note is not None:row['execution_note']=note
    elif note is not None and row.get('status')==status and not row.get('execution_note'):
        row['execution_note']=note


def update():
    acquired=acquisitions()
    write_json('outputs/qa/acquisition_status.json',dict(downloaded=sum(s['status']=='downloaded' for s in acquired),
        failed=[s for s in acquired if s['status']!='downloaded'],note='Safra HTTP403 is separate from successful official PDF verification via web tool.'))
    notes={
    'D00':('public_rules_verified_private_pending','Regulamento 2026 verificado via ferramenta web; horário/canal/orientações privadas H07 pendentes.'),
    'D01':('completed_scope','Originais ativos do inventário preservados; modelos, cartas e contexto inventariados; áudio excluído a pedido do usuário.'),
    'D02':('acquired_extracted','Três CNPJs/códigos conferidos no cadastro CVM; cinco instrumentos separados.'),
    'D03':('acquired_extracted','DFP 2021–25 baixadas; versão, conta, linha, moeda e data registradas.'),
    'D04':('acquired_extracted','ITR 2025–26 baixadas; último balanço elegível usado: junho/2026.'),
    'D05':('partial_reconciled','Sabesp: entradas confrontadas; construção, ativo financeiro e EBITDA ajustado exigem ponte econômica.'),
    'D06':('partial_reconciled','Copasa: receita, construção, impostos e saldos conferidos; capex físico vs caixa e receita regulatória parciais.'),
    'D07':('partial_reconciled','Sanepar: contas individuais, itens não recorrentes e capex não caixa identificados; base recorrente parcial.'),
    'D08':('identified_not_economically_reconciled','PPP/derivativos/outorgas identificados; valor nominal não promovido a PV incremental sem reconciliar fluxos.'),
    'D09':('verified_june_october_confirmation_pending','Capital por classe em junho e estatuto conferidos; evento posterior a junho não certificado.'),
    'D10':('public_reference_available','Cinco fechamentos 30/10 capturados em HTML de provedor público; H01 serve à confirmação e eventos de capital.'),
    'D11':('partial_source_qualified','Sabesp sustentabilidade 2024 e release 2T26; KPI de perdas com definição e data.'),
    'D12':('partial_source_qualified','Copasa release 2T26: perdas, esgoto, tecnologia, regulação e escopo controladora+Patos.'),
    'D13':('partial_source_qualified','Sanepar release/ITR 2T26: perdas, esgoto, inadimplência, precatório e classes.'),
    'D14':('partial_contract_coverage','Regulação e prazo URAE-1 obtidos no RI; não se afirma leitura de todos os anexos municipais.'),
    'D15':('partial_contract_coverage','RTP e reconhecimento anual de investimentos no release; modelo tarifário anual completo não implementado.'),
    'D16':('partial_contract_coverage','ITR nota 20, concessões e Agepar: regra e exceções documentadas.'),
    'D17':('rule_verified_incremental_pv_unresolved','Passivo R$4.407,957mi e regra coletados; PV incremental depende de cronograma e sobreposição com fluxos.'),
    'D18':('acquired_extracted','Relatórios e planilhas SINISA base2024; 271.856 registros municipais; sem média simples de razões.'),
    'D19':('partial_contract_coverage','Metas nacionais, URAE-1 e concessões materiais; não generalizar prazo para todos os contratos.'),
    'D20':('completed_scope','Aegea Pará e tecnologia/perdas Copasa: casos documentados, sem alegar execução do investimento anunciado.'),
    'D21':('partial_calendar_coverage','Calendário Sanepar 2026 salvo: ITR 12/11, reunião 13/11. Demais datas não certificadas.'),
    'D22':('acquired_extracted','Selic SGS432 e IPCA SGS433; taxas em razão decimal; datas reais preservadas.'),
    'D23':('acquired_extracted','Focus IPCA 2026–30: snapshot efetivo 23/10; anos posteriores são hipótese, não consenso.'),
    'D24':('acquired_extracted','Tesouro 30/10: título, vencimento, taxa compra/venda e janela identificados; não equivale a retorno de ação.'),
    'D25':('public_substitute_used','CVM e RI usados; exportação Bloomberg complementar não realizada.'),
    'D26':('optional_not_acquired_not_used','Não há consenso Bloomberg no pacote; trajetórias são premissas propostas.'),
    'D27':('optional_not_acquired_not_used','Sem comparação de preços-alvo de analistas.'),
    'D28':('public_substitute_used','RI/SINISA/reguladores substituem KPIs opcionais Bloomberg.'),
    'D29':('optional_not_acquired_not_used','Omitidos índices e financiamento verde sem comprovação específica; nenhuma alegação sintética.'),
    'D30':('draft_normalized_with_explicit_gaps','Base normalizada, conciliação parcial e limites econômicos registrados; não certificada para recomendação final.'),
    'D31':('draft_package_generated','XLSX/JSON/MD/figuras/PPTX/PDF e manifesto em outputs/draft; sem promoção artificial a final.'),
    'D32':('deferred_by_scope','Regressões extras não necessárias para cobrir o conteúdo público da etapa.')}
    backlog=read_csv('data/catalog/collection_backlog.csv')
    coverage=[]
    for row in backlog:
        default_status,default_note=notes[row['task_id']]
        initialize_status(row,default_status,default_note)
        status,note=row['status'],row.get('execution_note','Estado preservado; registrar evidência da mudança.')
        coverage.append(dict(requirement_id=row['task_id'],task_id=row['task_id'],entity_id=row['entity_id'],
            metric_id='',period_required='snapshot 2026-10-31',status=status,obs_ids='',source_ids='',
            gap_reason='' if status in ['completed_scope','acquired_extracted'] else note,
            materiality=row['priority'],owner=row['owner'],fallback=row['fallback'],accepted_limitation='documented_not_human_approved',
            topic=row['title'],note=note))
    write_csv('data/catalog/collection_backlog.csv',backlog)
    write_csv('data/processed/coverage.csv',coverage)
    human=read_csv('data/catalog/manual_export_requests.csv')
    statuses={'H01':'public_references_obtained_confirmation_recommended','H02':'public_substitute_used_optional',
        'H03':'optional_not_used','H04':'optional_not_used','H05':'public_substitute_used_optional','H06':'public_substitute_used_optional',
        'H07':'public_rules_verified_private_instructions_pending','H08':'proposal_and_evidence_ready_human_review_pending',
        'H09':'conditional_thesis_ready_group_decision_pending','H10':'script_and_slides_ready_real_rehearsals_pending',
        'H11':'recording_material_ready_real_clips_missing','H12':'technical_tools_ready_no_manual_action_requested',
        'H13':'awaiting_real_video_review_and_submission'}
    for row in human:initialize_status(row,statuses.get(row['request_id'],'not_started'))
    write_csv('data/catalog/manual_export_requests.csv',human)
    n=read_csv('data/processed/n_status.csv')
    stat={'N01':'inputs_ready','N02':'inputs_ready','N03':'inputs_ready','N05':'conditional_analysis_economic_review_pending',
        'N06':'inputs_ready','N07':'partial_regulatory_context_not_market_wacc','N08':'inputs_ready_not_automatic_ranking',
        'N09':'inputs_ready_source_definitions_differ','N10':'partial_contract_coverage','N11':'cash_semantics_review_pending',
        'N12':'method_redefined_energy_sensitivity_calculated','N13':'conditional_scenarios_calculated',
        'N14':'inputs_ready','N15':'omitted_not_acquired','N16':'omitted_not_acquired','N17':'omitted_not_acquired',
        'N18':'partial_definitions_and_tariff_compensation','N19':'inputs_ready','N20':'partial_calendar_coverage',
        'N24':'omitted_causality_not_measured','N25':'conditional_scenarios_calculated'}
    for row in n:
        initialize_status(row,stat.get(row['n_id'],'deferred_by_scope'))
        if not row.get('final_use'):
            row['final_use']='draft' if row['status'] not in ['deferred_by_scope','omitted_not_acquired','omitted_causality_not_measured'] else 'omitted'
        if not row.get('omission_reason') and row['final_use']=='omitted':
            row['omission_reason']='No unsupported figure or causal claim used'
    write_csv('data/processed/n_status.csv',n)
    registry=read_csv('data/catalog/source_registry.csv')
    for row in registry:
        key=row['registry_id']
        if row.get('collection_status','') in ['','discovery_only']:
            row['collection_status']='public_support_acquired_partial_scope'
            if key in ['BLOOMBERG','B3_MANUAL']:row['collection_status']='not_imported_public_substitute_used'
            if key=='SAFRA_2026':row['collection_status']='verified_official_pdf_via_web_original_http_403'
    write_csv('data/catalog/source_registry.csv',registry)
    cfg=read_json('config/collection.json')
    if cfg.get('status','') in ['','implementation_in_progress']:
        cfg['status']='draft_implemented_technical_checks_pass_economic_review_pending'
    execution=cfg.setdefault('execution',{})
    execution.update(updated_at=now(),draft_directory='outputs/draft',review_report='outputs/qa/execution_validation.json',human_actions='data/catalog/manual_export_requests.csv')
    execution.setdefault('economic_certification',False);execution.setdefault('submission_completed',False)
    write_json('config/collection.json',cfg)
    # EXECUTION_CONTEXT.md is a manual handoff: never replace it with a fixed snapshot.
    from sync_project_docs import sync
    sync()
    print('Execution status synchronized; manual handoff and existing decisions preserved.')


if __name__=='__main__':update()
