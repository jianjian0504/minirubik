import subprocess
from pathlib import Path
sources=[[1,4,2,0,3,5,6],[0,1,2,4,5,6,3],[0,2,5,3,1,4,6]]
twist=[[1,2,0,2,1,0,0],[0,0,0,1,2,1,2],[0]*7]
names=['R','R2',"R'",'B','B2',"B'",'D','D2',"D'"]
vectors=[('12345671111111',0),('25314763213211',1)]
# Derive a one-R scramble from solved with the model; no guessed vector.
p=sources[0];o=twist[0];vectors[1]=(''.join(str(v+1) for v in p+o),1)
Path('tests/basic.txt').write_text('\n'.join([vectors[0][0],vectors[1][0],'21345671111111'])+'\n')
for line in Path('tests/solutions.txt').read_text().splitlines():
 if line and not line.startswith('#'):
  s,answer=line.split('|');vectors.append((s,len(answer.split())))
for s,n in vectors:
 r=subprocess.run(['./compact',s],text=True,capture_output=True,check=True);moves=r.stdout.split();assert len(moves)==n
 p=[int(x)-1 for x in s[:7]];o=[int(x)-1 for x in s[7:]]
 for m in moves:
  f=names.index(m)//3
  for _ in range(names.index(m)%3+1):p=[p[j] for j in sources[f]];o=[(o[j]+twist[f][i])%3 for i,j in enumerate(sources[f])]
 assert p==list(range(7)) and o==[0]*7
 print(s,n,'PASS')
print('All provided vector lengths and replayed paths PASS; exact move sequence may differ.')
