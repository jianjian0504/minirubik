"""macOS host RSS slope; real user measurements only. CLI startup is included."""
import argparse,re,subprocess,time,csv
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--ripes',required=True);p.add_argument('--processor',default='RV32_ISS');a=p.parse_args();rows=[]
for words in [16384,262144]:
 src=Path('memory_probe.s').read_text().replace('NWORDS,262144',f'NWORDS,{words}');Path('probe-current.s').write_text(src)
 cmd=['/usr/bin/time','-l',str(Path(a.ripes).expanduser()),'--mode','cli','--src','probe-current.s','--srctype','asm','--proc',a.processor,'--iret'];start=time.perf_counter();r=subprocess.run(cmd,capture_output=True,text=True,check=True);wall=time.perf_counter()-start;out=r.stdout+r.stderr;Path(f'probe-{a.processor}-{words}.log').write_text(out)
 m=re.search(r'(\d+)\s+maximum resident set size',out);assert m,'macOS time -l RSS field missing'
 rows.append((words*4,int(m[1]),wall))
slope=(rows[1][1]-rows[0][1])/(rows[1][0]-rows[0][0]);projection=rows[0][1]+slope*(18405414-rows[0][0]);print('guest_bytes,host_peak_RSS_bytes,wall_seconds');print(*rows,sep='\n');print(f'RSS slope={slope:.6f} host bytes/guest byte; projected baseline RSS={projection:.0f} bytes')
print('This slope is build-dependent. Wall time includes startup; use real simulator execution-time statistics for instruction rate when available.')
