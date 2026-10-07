"""Independent RV32I interpreter harness builder; not a replacement for Ripes."""
import ast,re,struct,sys
from pathlib import Path
regs={'zero':0,'ra':1,'sp':2,'gp':3,'tp':4,**{f't{i}':r for i,r in enumerate([5,6,7,28,29,30,31])},**{f's{i}':r for i,r in enumerate([8,9,18,19,20,21,22,23,24,25,26,27])},**{f'a{i}':10+i for i in range(8)}}
labels={};fix=[];ins=[];data=bytearray(65536);section='data'
def reg(x):return regs[x] if x in regs else int(x[1:])
def raw(op,args):ins.append((op,args))
def li(rd,v):
 v=int(v,0) if isinstance(v,str) else v
 v=v&0xffffffff;v=v if v<0x80000000 else v-0x100000000
 if -2048<=v<=2047:raw('addi',[rd,'zero',v])
 else:
  hi=(v+2048)>>12;lo=v-(hi<<12);raw('lui',[rd,hi&0xfffff]);raw('addi',[rd,rd,lo])
source=sys.argv[sys.argv.index('--source')+1] if '--source' in sys.argv else 'solver-gui.s' if '--gui' in sys.argv else 'solver-cli.s'
text=Path(source).read_text()
for symbol,value in [('LED_MATRIX_0_BASE','262144'),('LED_MATRIX_0_WIDTH','35'),('LED_MATRIX_0_HEIGHT','25')]:text=text.replace(symbol,value)
for line in text.splitlines():
 line=line.split('#')[0].strip()
 if not line:continue
 if line in ['.data','.text']:section=line[1:];continue
 if line.startswith('.globl'):continue
 if ':' in line:
  lab,line=line.split(':',1);labels[lab.strip()]=len(data) if section=='data' else len(ins)*4;line=line.strip()
  if not line:continue
 if section=='data':
  directive,_,arg=line.partition(' ')
  if directive=='.align':
   align=1<<int(arg);data.extend(b'\0'*((-len(data))%align))
  elif directive=='.space':data.extend(b'\0'*int(arg))
  elif directive=='.asciz':data.extend(ast.literal_eval(arg).encode()+b'\0')
  elif directive in ['.byte','.half','.word']:
   width={'.byte':1,'.half':2,'.word':4}[directive]
   for x in arg.split(','):
    try:v=int(x.strip(),0)
    except ValueError:fix.append((len(data),x.strip()));v=0
    data.extend(v.to_bytes(width,'little'))
  else:raise ValueError(line)
  continue
 op,_,arg=line.partition(' ');args=[x.strip() for x in arg.split(',')] if arg else []
 if op=='li':li(*args)
 elif op=='la':raw('lui',[args[0],('hi',args[1])]);raw('addi',[args[0],args[0],('lo',args[1])])
 elif op=='mv':raw('addi',[args[0],args[1],0])
 elif op=='j':raw('jal',['zero',args[0]])
 elif op=='ret':raw('jalr',['zero','ra',0])
 elif op in ['beqz','bnez']:raw('beq' if op=='beqz' else 'bne',[args[0],'zero',args[1]])
 else:raw(op,args)
for off,lab in fix:data[off:off+4]=struct.pack('<I',labels[lab])
ops=['addi','lui','add','sub','or','and','sll','srl','slli','srli','andi','lbu','lhu','lw','sb','sw','beq','bne','bltu','bgeu','jal','jalr','ecall','bge','sltu','xor']
out=[]
for op,args in ins:
 vals=[]
 if op=='ecall':vals=[0,0,0]
 elif op in ['lbu','lhu','lw','sb','sw']:
  off,base=re.fullmatch(r'(-?\d+)\((\w+)\)',args[1]).groups();vals=[reg(args[0]),reg(base),int(off)]
 elif op in ['beq','bne','bltu','bgeu','bge']:vals=[reg(args[0]),reg(args[1]),labels[args[2]]//4]
 elif op=='jal':vals=[reg(args[0]),0,labels[args[1]]//4]
 elif op=='lui':
  v=args[1];v=(labels[v[1]]+2048)>>12 if isinstance(v,tuple) else int(v,0) if isinstance(v,str) else v;vals=[reg(args[0]),0,v]
 else:
  vals=[reg(args[0]),reg(args[1])];v=args[2]
  if isinstance(v,tuple):address=labels[v[1]];v=address-(((address+2048)>>12)<<12)
  elif op in ['add','sub','or','and','sll','srl','sltu','xor']:v=reg(v)
  elif isinstance(v,str):v=int(v,0)
  vals.append(v)
 out.append((ops.index(op),*vals))
Path('qa_program.h').write_text('static const int prog[][4]={\n'+''.join('{'+','.join(map(str,x))+'},\n' for x in out)+'};\n'+f'#define INPUT_ADDR {labels["input_state"]}\n#define START_PC {labels["main"]//4}\n')
Path('qa_data.bin').write_bytes(data)
print(f'RV32I text: {len(out)*4} bytes; static data: {len(data)-65536} bytes')
