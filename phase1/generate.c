#define main original_main
#include "original/solver.c"
#undef main
#include <assert.h>
static uint16_t pr[4096],rev[840];
static uint8_t om[256],tm[96],pa[68040],pb[68040];
static unsigned ix(uint32_t s){unsigned p=(s&7)|((s>>5)&56)|((s>>10)&448)|((s>>15)&3584);unsigned o=((s>>3)&3)|((s>>9)&12)|((s>>15)&48)|((s>>21)&192);return pr[p]*81+om[o];}
static uint32_t dec(unsigned idx){unsigned p=rev[idx/81],o=idx%81;uint32_t s=0;for(int k=0;k<4;k++){s|=((p>>(3*k)&7)|((o%3)<<3))<<(8*k);o/=3;}return s;}
static uint32_t tr(uint32_t s,unsigned f){uint32_t r=0;for(int k=0;k<4;k++)r|=(uint32_t)tm[f*32+(s>>(8*k)&31)]<<(8*k);return r;}
static void bfs(uint8_t *t,uint32_t goal){uint32_t q[68040];unsigned h=0,n=1;t[ix(goal)]=0;q[0]=ix(goal);while(h<n){unsigned i=q[h++];uint32_t s=dec(i);for(unsigned f=0;f<3;f++){uint32_t z=s;for(unsigned k=0;k<3;k++){z=tr(z,f);unsigned j=ix(z);if(t[j]==255){t[j]=t[i]+1;q[n++]=j;}}}}assert(n==68040);unsigned max=0;for(unsigned i=0;i<n;i++){assert(t[i]<15);if(t[i]>max)max=t[i];}printf("PDB: %u entries, maximum %u, solved %u\n",n,max,t[ix(goal)]);}
static void emit(FILE*c,FILE*s,const char*name,const void*v,unsigned n,int half,int packed){fprintf(c,"const %s %s[%u]={\n",half?"uint16_t":"uint8_t",name,packed?(n+1)/2:n);fprintf(s,".align %u\n%s:\n",half?1:0,name);unsigned len=packed?(n+1)/2:n;for(unsigned i=0;i<len;i++){unsigned x=half?((const uint16_t*)v)[i]:packed?((const uint8_t*)v)[i*2]|(((const uint8_t*)v)[i*2+1]<<4):((const uint8_t*)v)[i];fprintf(c,"%u%s",x,i+1==len?"":",");if(i%16==0)fprintf(s,"%s ",half?".half":".byte");fprintf(s,"%u%s",x,i%16==15||i+1==len?"\n":",");if(i%16==15)fputc('\n',c);}fprintf(c,"\n};\n");}
int main(void){memset(pr,255,sizeof pr);unsigned r=0;for(unsigned a=0;a<7;a++)for(unsigned b=0;b<7;b++)for(unsigned c=0;c<7;c++)for(unsigned d=0;d<7;d++)if(a!=b&&a!=c&&a!=d&&b!=c&&b!=d&&c!=d){unsigned p=a|(b<<3)|(c<<6)|(d<<9);pr[p]=r;rev[r++]=p;}assert(r==840);memset(om,255,sizeof om);for(unsigned x=0;x<256;x++){unsigned n=0;int ok=1;for(int k=3;k>=0;k--){unsigned o=x>>(k*2)&3;if(o==3)ok=0;n=n*3+o;}if(ok)om[x]=n;}
memset(tm,255,sizeof tm);for(unsigned f=0;f<3;f++)for(unsigned pos=0;pos<7;pos++)for(unsigned o=0;o<3;o++)for(unsigned dest=0;dest<7;dest++)if(source[f][dest]==pos)tm[f*32+pos+(o<<3)]=dest+(((o+twist[f][dest])%3)<<3);
memset(pa,255,sizeof pa);memset(pb,255,sizeof pb);bfs(pa,0x03020100);bfs(pb,0x06050403);
FILE*ref=fopen("pdb_reference.bin","wb");assert(ref);assert(fwrite(pa,1,sizeof pa,ref)==sizeof pa);assert(fwrite(pb,1,sizeof pb,ref)==sizeof pb);fclose(ref);
FILE*c=fopen("tables.c","w"),*s=fopen("tables.inc","w");assert(c&&s);fputs("#include <stdint.h>\n",c);emit(c,s,"pos_rank",pr,4096,1,0);emit(c,s,"ori_rank",om,256,0,0);emit(c,s,"turn_map",tm,96,0,0);emit(c,s,"pdb_a",pa,68040,0,1);emit(c,s,"pdb_b",pb,68040,0,1);fclose(c);fclose(s);return 0;}
