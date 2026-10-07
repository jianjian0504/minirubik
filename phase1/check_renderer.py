"""Checks sticker mapping against independent 3D face rotations."""
import random
from renderer import orders,faces
pos=[(-1,1,1),(1,1,1),(1,-1,1),(-1,-1,1),(1,1,-1),(1,-1,-1),(-1,-1,-1),(-1,1,-1)]
norm=[(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(-1,0,0),(1,0,0)]
sources=[[1,4,2,0,3,5,6],[0,1,2,4,5,6,3],[0,2,5,3,1,4,6]]
twists=[[1,2,0,2,1,0,0],[0,0,0,1,2,1,2],[0]*7]
def model(p,o):
 d={}
 for i in range(8):
  cubie=0 if i==0 else p[i-1]+1;ori=0 if i==0 else o[i-1]
  for slot,f in enumerate(orders[i]):d[pos[i],norm[f]]=orders[cubie][(slot-ori)%3]
 return d
def rotate(v,f):
 x,y,z=v
 return [(x,z,-y),(-y,x,z),(z,y,-x)][f]
def geometric(d,f):
 out={}
 for (v,n),c in d.items():
  affected=[v[0]==1,v[2]==-1,v[1]==-1][f]
  out[(rotate(v,f),rotate(n,f)) if affected else (v,n)]=c
 return out
p=list(range(7));o=[0]*7;d=model(p,o);rng=random.Random(42)
for i in range(10000):
 f=rng.randrange(3);p=[p[j] for j in sources[f]];o=[(o[j]+twists[f][k])%3 for k,j in enumerate(sources[f])];d=geometric(d,f);assert model(p,o)==d,(i,f)
print('Renderer sticker mapping PASS: 10,000 independent geometric quarter turns')
