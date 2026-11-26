"""Reference fixture validation only; not a test of the Development toolkit."""
import csv, collections
from pathlib import Path
from datetime import date
p=Path(__file__).resolve().parent
read=lambda n:list(csv.DictReader((p/(n+'.csv')).open()))
v,a,q,r,e,sv,links,f,act,d,c,au=[read(n) for n in ['vendor','assessment','question','response','evidence_item','business_service','vendor_service_link','finding','corrective_action','decision','change_event','reviewer_audit_entry']]
def unique(rows,*keys):
    k=[tuple(x[y] for y in keys) for x in rows]; assert len(k)==len(set(k)); return set(k)
for rows,key in [(v,'vendor_id'),(a,'assessment_id'),(q,'question_id'),(e,'evidence_id'),(sv,'service_id'),(f,'finding_id'),(act,'action_id'),(d,'decision_id'),(c,'change_id'),(au,'audit_id')]: unique(rows,key)
unique(links,'vendor_id','service_id'); unique(r,'assessment_id','question_id'); unique(e,'assessment_id','question_id')
V={x['vendor_id']:x for x in v}; A={x['assessment_id']:x for x in a}; Q={x['question_id']:x for x in q}; S={x['service_id']:x for x in sv}; F={x['finding_id']:x for x in f}; E={(x['assessment_id'],x['question_id']):x for x in e}
assert len(v)==10 and len(a)==11 and len(q)==24 and len(r)==len(e)==264
assert sorted(collections.Counter(x['category'] for x in v).values())==[2]*5
assert all(x['vendor_id'] in V for x in a) and all(A[x['current_assessment_id']]['vendor_id']==x['vendor_id'] for x in v)
assert all(x['vendor_id'] in V and x['service_id'] in S for x in links)
assert all(x['assessment_id'] in A and x['question_id'] in Q for x in r+e+f)
assert all(A[F[x['finding_id']]['assessment_id']]['vendor_id']==x['vendor_id'] for x in act)
assert all(x['assessment_id'] in A and x['decision_maker_role']!=A[x['assessment_id']]['assessor_role'] and x['decision_date']<=x['review_date']<=x['expiry_date'] and x['decision_date']<x['expiry_date'] for x in d)
assert all(A[x['reassessment_assessment_id']]['vendor_id']==x['vendor_id'] for x in c)
assert all(x['status'] in {'Missing','Received','Accepted','Rejected','Expired'} for x in e)
assert all(x['reviewer_role'] and x['expiry_date'] for x in e if x['status']=='Accepted')
assert all(x['reason'] for x in e if x['status']=='Rejected')
assert all(x['vendor_claim']=='Blank' or x['vendor_claim'] in {z.rsplit(' = ',1)[0] for z in Q[x['question_id']]['response_options'].split(' | ')} for x in r)
assert all(x['reviewer_verified']!='Yes' or E[(x['assessment_id'],x['question_id'])]['status']=='Accepted' for x in r)
assert all(x['status']!='Closed' or x['closed_date'] for x in act)
assert all(x['condition_deadline'] and x['conditions'] and x['review_date']<=x['condition_deadline'] for x in d if x['outcome']=='Conditionally Approved')
expected={x['assessment_id']:x for x in read('expected_risk')}; denominator=sum(4*int(x['weight']) for x in q); assert denominator==344
for aid,assessment in A.items():
    rr=[x for x in r if x['assessment_id']==aid]; assert len(rr)==24; points=0; verified=0; failures=[]; unresolved=[]
    asof=assessment['assessment_date'] if assessment['status']=='Superseded' else '2026-11-18'
    for x in rr:
        qid=x['question_id']; qq=Q[qid]; ee=E[(aid,qid)]; options={k:int(val) for k,val in (option.rsplit(' = ',1) for option in qq['response_options'].split(' | '))}; good=ee['status']=='Accepted' and ee['expiry_date']>=asof and x['reviewer_verified']=='Yes' and x['vendor_claim']!='Blank'; value=options[x['verified_answer']] if good else 4
        if qq['critical_failure_flag']=='Yes':
            if not good: unresolved.append(qid)
            elif value>=3: failures.append(qid); value=4
        verified+=good; points+=int(qq['weight'])*value
    pct=points*100/denominator; band='Low' if pct<20 else 'Medium' if pct<40 else 'High' if pct<60 else 'Critical'; final='Incomplete' if verified<24 else 'High' if failures and band in ('Low','Medium') else band
    z=expected[aid]; assert (points,verified,final,band,';'.join(failures),';'.join(unresolved))==(int(z['weighted_points']),int(z['verified_count']),z['final_rating'],z['raw_band'],z['confirmed_critical_failures'],z['unresolved_critical_questions']); assert abs(pct-float(z['risk_percent']))<0.000001
print('PASS: 12 source tables; unique keys, tested FKs, option labels, decision date constraints, evidence states, 264 response/evidence pairs and all 11 expected risk calculations.')
print('PASS: 10 vendors, 5 categories, 24 rows per assessment; fixed report date and history selection.')
print('LIMIT: fixture verification only. Independent review, complete schema/policy approval and toolkit acceptance execution pending.')
# Supplemental Day 3 cross-checks against Day 1 dictionary and Day 2 draft methods.
from collections import Counter, defaultdict
assert all(x['reviewer_verified'] in {'Yes','No','Not reviewed'} and (x['reviewer_verified']!='Yes' or x['verified_answer'] in {z.rsplit(' = ',1)[0] for z in Q[x['question_id']]['response_options'].split(' | ')}) for x in r)
assert all(x['received_date'] and x['reference_path'] for x in e if x['status']!='Missing')
assert all(x['review_period_end'] and x['expiry_date'] and x['reviewer_role'] for x in e if x['status'] in {'Accepted','Expired'})
assert all(x['reviewer_role'] and x['reason'] for x in e if x['status']=='Rejected')
assert all(x['expiry_date']>=x['received_date'] for x in e if x['status'] in {'Accepted','Expired'})
assert Counter(z['question_id'].split('-')[0] for z in q)==dict.fromkeys(['AM','DP','IN','BC','SC','GV'],4)
assert all(int(z['weight']) in range(1,6) for z in q)
crit=read('expected_criticality'); crit_by_a={x['assessment_id']:x for x in crit}
svc_by_v=defaultdict(set)
for link in links: svc_by_v[link['vendor_id']].add(link['service_id'])
for z in crit:
    aa=A[z['assessment_id']]; vv=V[z['vendor_id']]; assert aa['vendor_id']==vv['vendor_id']
    fields=['data_sensitivity','system_access','dependency_impact','replaceability']
    if aa['status']!='Superseded': assert all(z[k]==vv[k] for k in fields)
    dp=['None','Internal','Confidential','Regulated'].index(z['data_sensitivity']); ap=['None','Standard','Privileged'].index(z['system_access']); ip=int(z['dependency_impact']); rp=['Easy','Moderate','Hard','Very hard'].index(z['replaceability'])+1
    total=dp+ap+ip+rp; base='Low' if total<=3 else 'Medium' if total<=6 else 'High' if total<=9 else 'Critical'; final=base
    if any(S[s]['service_tier']=='Business-critical' for s in svc_by_v[vv['vendor_id']]) and final in ('Low','Medium'): final='High'
    if (dp==3 and ap==2) or (ip==4 and rp==4): final='Critical'
    assert (dp,ap,ip,rp,total,base,final)==tuple(int(z[k]) for k in ['data_points','access_points','dependency_points','replaceability_points','total_points'])+(z['base_band'],z['final_band'])
# Independently recompute each per-question score and domain summary.
expq={(z['assessment_id'],z['question_id']):z for z in read('expected_question_scores')}; expdom={(z['assessment_id'],z['domain']):z for z in read('expected_domain_completeness')}
assert len(expq)==264 and len(expdom)==66
for aid,aa in A.items():
    asof=aa['assessment_date'] if aa['status']=='Superseded' else '2026-11-18'; bydom=defaultdict(list)
    for z in (z for z in r if z['assessment_id']==aid):
        qid=z['question_id']; qq=Q[qid]; ee=E[(aid,qid)]; good=ee['status']=='Accepted' and ee['expiry_date']>=asof and z['reviewer_verified']=='Yes' and z['vendor_claim']!='Blank'; weight=int(qq['weight']); opts=dict((k,int(val)) for k,val in (o.rsplit(' = ',1) for o in qq['response_options'].split(' | '))); value=opts[z['verified_answer']] if good else 4; failure=good and qq['critical_failure_flag']=='Yes' and value>=3; unresolved=not good and qq['critical_failure_flag']=='Yes'; value=4 if failure else value
        t=expq[(aid,qid)]; assert [int(t[k]) for k in ('weight','assigned_value','weighted_points','maximum_points')]==[weight,value,weight*value,4*weight]; assert t['confirmed_failure']==('Yes' if failure else 'No') and t['unresolved_critical']==('Yes' if unresolved else 'No')
        bydom[qid.split('-')[0]].append((z['vendor_claim']!='Blank',good))
    for domain,rows in bydom.items():
        t=expdom[(aid,domain)]; n=sum(b for a,b in rows); assert (int(t['total_questions']),int(t['answered_count']),int(t['verified_count']),float(t['completeness_percent']))==(4,sum(a for a,b in rows),n,25*n)
current={z['current_assessment_id']:z['vendor_id'] for z in v}; decision={z['assessment_id']:z for z in d}; groups=defaultdict(set)
for vv in v:
    vid=vv['vendor_id']; aid=vv['current_assessment_id']; groups['category',vv['category']].add(vid); groups['criticality',crit_by_a[aid]['final_band']].add(vid); dd=decision.get(aid); groups['decision',dd['outcome'] if dd else 'Awaiting decision'].add(vid); zz=expected[aid]
    if zz['completeness']=='Incomplete':groups['flag','Incomplete'].add(vid)
    if zz['confirmed_critical_failures']:groups['flag','Confirmed critical failure'].add(vid)
    if zz['unresolved_critical_questions']:groups['flag','Unresolved critical question'].add(vid)
    if vv['next_review_date']<'2026-11-18':groups['flag','Overdue review'].add(vid)
    if dd and dd['outcome'] in {'Approved','Conditionally Approved'} and dd['expiry_date']<'2026-11-18':groups['flag','Expired approval'].add(vid)
    if dd and dd['outcome']=='Approved' and dd['expiry_date']>='2026-11-18':groups['flag','Unexpired Approved outcome'].add(vid)
    if dd and dd['outcome']=='Conditionally Approved':groups['flag','Open condition'].add(vid)
    if any(x['assessment_id']==aid and x['status']=='Open' for x in f):groups['flag','Open finding'].add(vid)
    if any(x['vendor_id']==vid and x['status']!='Closed' and x['due_date']<'2026-11-18' for x in act):groups['flag','Overdue action'].add(vid)
    for st in ['Expired','Rejected','Received','Missing']:
        if any(x['assessment_id']==aid and x['status']==st for x in e):groups['flag',st+' evidence'].add(vid)
    if int(zz['answered_count'])<24:groups['flag','Unanswered'].add(vid)
    if any(S[s]['service_tier']=='Business-critical' for s in svc_by_v[vid]):groups['service dependency','Business-critical vendor'].add(vid)
    if len(svc_by_v[vid])>1:groups['vendor concentration','Multiple services'].add(vid)
for sid in S:
    ids={vid for vid in V if sid in svc_by_v[vid]}
    if len(ids)>1:groups['service concentration',sid]=ids
for t in read('expected_management'):
    ids=groups[t['breakdown'],t['group']]; assert len(ids)==int(t['count']) and ids==set(t['vendor_ids'].split(';'))
assert len(groups)==len(read('expected_management'))
# Audit references and version relationships.
parents={'assessment':A,'evidence_item':{z['evidence_id']:z for z in e},'decision':{z['decision_id']:z for z in d}}
assert all(x['record_id'] in parents[x['table_name']] for x in au)
for z in a:
    if z['supersedes_id']:
        pred=A[z['supersedes_id']];assert pred['vendor_id']==z['vendor_id'] and int(pred['version_no'])+1==int(z['version_no']) and pred['status']=='Superseded' and pred['assessment_date']<z['assessment_date']
print('PASS: independently recalculated 11 criticality classifications, 264 question scores, 66 domain completeness results and all management count/source-ID expectations; checked audit references and version links.')
