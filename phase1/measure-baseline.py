#!/usr/bin/env python3
"""macOS Ripes memory-slope and instruction-rate benchmark; standard library only."""
import argparse,csv,hashlib,json,re,statistics,subprocess,sys
from pathlib import Path

ASM='''.equ NWORDS,{words}
.text
.globl main
main:
 li t0,0x20000000
 li t1,NWORDS
 li t2,0x12345678
loop:
 sw t2,0(t0)
 addi t0,t0,4
 addi t1,t1,-1
 bnez t1,loop
 li a0,0
 li a7,93
 ecall
'''

def parse(text):
 def stat(name):
  m=re.search(r'^=+\s*'+name+r'\s*\r?\n\s*(\d+)',text,re.M|re.I)
  return int(m[1]) if m else None
 rss=re.search(r'(\d+)\s+maximum resident set size',text)
 return stat('instructions retired'),stat(r'wall-clock model execution time \(ms\)'),int(rss[1]) if rss else None

def main():
 p=argparse.ArgumentParser();p.add_argument('--ripes',required=True)
 p.add_argument('--processor',choices=['RV32_ISS','RV32_5S','both'],default='both')
 p.add_argument('--repeats',type=int,default=3)
 a=p.parse_args()
 if sys.platform!='darwin':raise SystemExit('This benchmark uses macOS /usr/bin/time -l RSS in bytes.')
 if a.repeats<1:raise SystemExit('--repeats must be positive')
 binary=Path(a.ripes).expanduser().resolve()
 if not binary.is_file():raise SystemExit('Ripes executable not found: '+str(binary))
 out=Path('baseline-measurements');out.mkdir(exist_ok=True)
 processors=['RV32_ISS','RV32_5S'] if a.processor=='both' else [a.processor]
 meta={'binary_path':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
       'processors':processors,'repeats':a.repeats,'host_rss_units':'bytes (macOS)',
       'guest_baseline_bytes':18405414,'notes':'RSS is whole-process peak; model time excludes process startup.'}
 (out/'build.json').write_text(json.dumps(meta,indent=2)+'\n')
 fields=['processor','guest_bytes','repeat','instructions_retired','model_ms','host_peak_rss_bytes','instructions_per_second']
 rows=[];summary=[]
 with (out/'samples.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for proc in processors:
   for words in [16384,262144]:
    src=out/f'probe-{proc}-{words}.s';src.write_text(ASM.format(words=words))
    for rep in range(1,a.repeats+1):
     cmd=['/usr/bin/time','-l',str(binary),'--mode','cli','--src',str(src),'-t','asm',
          '--proc',proc,'--iret','--exectime','--runinfo']
     r=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
     text=r.stdout+'\n'+r.stderr
     (out/f'{proc}-{words}-{rep}.log').write_text(text+f'\nHost exit code: {r.returncode}\n')
     count,ms,rss=parse(text)
     if (r.returncode<0 or 'Program exited with code: 0' not in text
         or count is None or ms is None or rss is None):
      raise SystemExit('Incomplete run; inspect '+str(out/f'{proc}-{words}-{rep}.log'))
     rate=count*1000/ms if ms else None
     row=dict(zip(fields,[proc,words*4,rep,count,ms,rss,rate]));rows.append(row)
     writer.writerow(row);f.flush()
     print(f'{proc} guest={words*4} bytes repeat={rep}/{a.repeats} iret={count} model_ms={ms} RSS={rss}',flush=True)
   small=[r for r in rows if r['processor']==proc and r['guest_bytes']==65536]
   large=[r for r in rows if r['processor']==proc and r['guest_bytes']==1048576]
   lo=statistics.median(r['host_peak_rss_bytes'] for r in small)
   hi=statistics.median(r['host_peak_rss_bytes'] for r in large)
   slope=(hi-lo)/(1048576-65536)
   rates=[r['instructions_per_second'] for r in large if r['instructions_per_second'] is not None]
   rate=statistics.median(rates) if rates else None
   projection=lo+slope*(18405414-65536) if slope>0 else None
   item={'processor':proc,'host_bytes_per_guest_byte_slope':slope,
         'projected_peak_rss_bytes_for_baseline':projection,
         'median_large_probe_instructions_per_second':rate,
         'idealized_seconds_for_1e9_instructions':1e9/rate if rate else None,
         'small_median_rss_bytes':lo,'large_median_rss_bytes':hi}
   summary.append(item)
   print('\n'+proc+' SUMMARY',flush=True)
   print(f'RSS slope: {slope:.4f} host bytes per guest byte',flush=True)
   if projection is not None:print(f'Projected full-baseline process RSS: {projection/1048576:.2f} MiB',flush=True)
   else:print('Nonpositive slope: measurement noise is too large; repeat with a larger probe.',flush=True)
   if rate:print(f'Rate: {rate:,.0f} retired instructions/sec; idealized 1e9 time: {1e9/rate:.2f} sec',flush=True)
   print('',flush=True)
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print('Saved raw logs, samples.csv, summary.json and build.json in baseline-measurements/.')
 print('RSS extrapolation is empirical, not an exact allocation guarantee; speed is workload-dependent.')

if __name__=='__main__':
 try:main()
 except KeyboardInterrupt:raise SystemExit('Stopped; partial raw logs are retained. Re-run to repeat the measurements.')
