"""Run real Ripes CLI measurements. No substitute-emulator numbers are used."""
import argparse,csv,hashlib,re,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--ripes',required=True);p.add_argument('--processor',default='RV32_ISS');p.add_argument('--all-hard',action='store_true');p.add_argument('--source',default='solver-cli.s');p.add_argument('--output',default='ripes-results.csv');p.add_argument('--timeout',type=int,default=300);args=p.parse_args()
ripes=Path(args.ripes).expanduser().resolve();src=Path(args.source);base=src.read_text();help_run=subprocess.run([str(ripes),'--help'],capture_output=True,text=True);Path('ripes-help.txt').write_text(help_run.stdout+help_run.stderr)
if '--iret' not in help_run.stdout+help_run.stderr:raise SystemExit('This Ripes executable does not advertise --iret; inspect ripes-help.txt.')
Path('ripes-build.txt').write_text(f'executable={ripes}\nsha256={hashlib.sha256(ripes.read_bytes()).hexdigest()}\nprocessor={args.processor}\n')
states=Path('tests/hard11.txt' if args.all_hard else 'tests/basic.txt').read_text().splitlines();Path('ripes-logs').mkdir(exist_ok=True)
with open(args.output,'w',newline='') as f:
 w=csv.writer(f);w.writerow(['state','processor','retired_instructions','wall_seconds_including_startup','status'])
 for i,state in enumerate(states):
  s=re.sub(r'(input_state:\s*\.asciz\s*")[^"]+(\")',lambda m:m[1]+state+m[2],base)
  case=Path('ripes-logs/current.s');case.write_text(s)
  cmd=[str(ripes),'--mode','cli','--src',str(case),'--srctype','asm','--proc',args.processor,'--iret']
  start=time.perf_counter()
  try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=args.timeout);out=r.stdout+r.stderr;rc=r.returncode
  except subprocess.TimeoutExpired as e:out=str(e);rc=-1
  sec=time.perf_counter()-start;Path(f'ripes-logs/{args.processor}-{state}.txt').write_text(out)
  matches=re.findall(r'(?:instructions\s+retired|retired\s+instructions|iret)\s*[:=]?\s*([\d,]+)',out,re.I)
  count=int(matches[-1].replace(',','')) if matches else None
  status='PASS' if rc==0 and 'PASS: path reaches solved state' in out and count is not None else 'CHECK_LOG'
  if args.all_hard and count is not None and count>50000000:status='OVER_BUDGET'
  w.writerow([state,args.processor,count,f'{sec:.6f}',status]);f.flush();print(f'{i+1}/{len(states)} {state} {count} {status}',flush=True)
  if status=='CHECK_LOG':raise SystemExit('Check the saved log and ripes-help.txt. CLI syntax or statistics format may differ on your pinned build.')
print('Real Ripes measurements saved. Review all rows; do not infer worst-case performance from a sample.')
