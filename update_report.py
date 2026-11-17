import argparse, json, os, tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--type',choices=['tech','market'],required=True);p.add_argument('--date',required=True);p.add_argument('--file',required=True);p.add_argument('--title',required=True);a=p.parse_args()
from datetime import date
date.fromisoformat(a.date)
content=Path(a.file).read_text(encoding='utf-8-sig').strip()
if not content: raise SystemExit('报告内容为空')
root=Path(__file__).resolve().parent; target=root/'reports.json'; data=json.loads(target.read_text(encoding='utf-8-sig')) if target.exists() else {'reports':[]}
data['reports']=[x for x in data['reports'] if (x.get('type'),x.get('date'))!=(a.type,a.date)];data['reports'].append({'type':a.type,'date':a.date,'title':a.title,'content':content})
fd,tmp=tempfile.mkstemp(prefix='reports-',suffix='.tmp',dir=root)
try:
 with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
 os.replace(tmp,target)
finally:
 if os.path.exists(tmp): os.unlink(tmp)
print('已更新',a.date,a.title)
