import argparse, contextlib, json, os, subprocess, tempfile
from pathlib import Path
from datetime import date

p=argparse.ArgumentParser();p.add_argument('--type',choices=['tech','market','weekly'],required=True);p.add_argument('--date',required=True);p.add_argument('--file',required=True);p.add_argument('--title',required=True);p.add_argument('--publish',action='store_true');a=p.parse_args()
date.fromisoformat(a.date)
content=Path(a.file).read_text(encoding='utf-8-sig').strip()
if content.startswith('【补发：今日早上发布，数据截至文内时间】'): content=content.split('\n',1)[1].strip()
if not content: raise SystemExit('报告内容为空')
root=Path(__file__).resolve().parent; target=root/'reports.json'; lock_path=root/'.git'/'report-update.lock'
@contextlib.contextmanager
def lock():
 with lock_path.open('a+b') as f:
  if os.name=='nt':
   import msvcrt
   f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1)
  else:
   import fcntl
   fcntl.flock(f,fcntl.LOCK_EX)
  try: yield
  finally:
   if os.name=='nt': f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
   else: fcntl.flock(f,fcntl.LOCK_UN)
def git(*args,check=True):
 return subprocess.run(['git',*args],cwd=root,text=True,capture_output=True,timeout=55,check=check)
with lock():
 data=json.loads(target.read_text(encoding='utf-8-sig')) if target.exists() else {'reports':[]}
 data['reports']=[x for x in data['reports'] if (x.get('type'),x.get('date'))!=(a.type,a.date)];data['reports'].append({'type':a.type,'date':a.date,'title':a.title,'content':content})
 fd,tmp=tempfile.mkstemp(prefix='reports-',suffix='.tmp',dir=root)
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
  os.replace(tmp,target)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
 if a.publish:
  git('add','reports.json')
  diff=git('diff','--cached','--quiet','--','reports.json',check=False)
  if diff.returncode==1: git('-c','user.name=MausBot','-c','user.email=mausbot@users.noreply.github.com','commit','-m',f'Update {a.date} {a.type} report','--','reports.json')
  elif diff.returncode!=0: raise SystemExit('无法检查报告更新状态')
  result=git('push','origin','main',check=False)
  if result.returncode!=0: raise SystemExit('报告已保存，但网站更新失败，请检查版本同步后再重试')
 print('报告已更新到网站' if a.publish else '报告已保存',a.date,a.title)
