"""Rebuild exact dictionary-format question.csv from the repository's canonical question bank."""
import csv
from pathlib import Path
p=Path(__file__).resolve().parent
source=p.parent/'01-research-and-risk-assessment'/'question_bank.csv'
with source.open(encoding='utf-8-sig',newline='') as f:
    bank=list(csv.DictReader(f))
assert len(bank)==24 and len({x['question_id'] for x in bank})==24
with (p/'question.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow('question_id domain question_text response_options weight evidence_required evidence_description acceptance_criteria critical_failure_flag'.split())
    for q in bank:
        w.writerow([q['question_id'],q['Domain'],q['Wording'],q['Answer choices'],q['Weight / severity'],'Yes',q['Evidence artifact and period'],q['Reviewer acceptance criteria'],q['Critical failure?']])
