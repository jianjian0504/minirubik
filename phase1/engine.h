#ifndef ENGINE_H
#define ENGINE_H
#include <stdint.h>
extern const uint16_t pos_rank[4096];
extern const uint8_t ori_rank[256], turn_map[96], pdb_a[34020], pdb_b[34020];
static uint32_t turn4(uint32_t s, unsigned face) {
 const uint8_t *t=turn_map+(face<<5);
 return t[s&31] | ((uint32_t)t[(s>>8)&31]<<8) |
 ((uint32_t)t[(s>>16)&31]<<16) | ((uint32_t)t[s>>24]<<24);
}
static unsigned index4(uint32_t s) {
 unsigned p=(s&7)|((s>>5)&56)|((s>>10)&448)|((s>>15)&3584);
 unsigned o=((s>>3)&3)|((s>>9)&12)|((s>>15)&48)|((s>>21)&192);
 unsigned r=pos_rank[p];
 return (r<<6)+(r<<4)+r+ori_rank[o];
}
static unsigned get4(const uint8_t *t,uint32_t s) {
 unsigned i=index4(s); return (t[i>>1]>>((i&1)<<2))&15;
}
static unsigned heuristic(uint32_t a,uint32_t b) {
 unsigned x=get4(pdb_a,a),y=get4(pdb_b,b);return x>y?x:y;
}
#define GOAL_A 0x03020100u
#define GOAL_B 0x06050403u
typedef struct { uint32_t a,b,ra,rb;unsigned next,last; } frame_t;
static int search(uint32_t a,uint32_t b,uint8_t path[11],uint64_t *nodes) {
 frame_t st[12]; *nodes=0;
 for(unsigned bound=heuristic(a,b);bound<=11;bound++) {
  unsigned d=0;st[0]=(frame_t){a,b,a,b,0,3};
  for(;;) {
   frame_t *f=st+d;
   if(f->a==GOAL_A && f->b==GOAL_B)return (int)d;
   if(d==bound || f->next==9) {if(!d)break;--d;continue;}
   unsigned m=f->next++,face=m<3?0:m<6?1:2;
   if(face==f->last)continue;
   if(m==face*3){f->ra=f->a;f->rb=f->b;}
   f->ra=turn4(f->ra,face);f->rb=turn4(f->rb,face);++*nodes;
   if(heuristic(f->ra,f->rb)>bound-d-1)continue;
   path[d]=m;
   st[d+1]=(frame_t){f->ra,f->rb,f->ra,f->rb,0,face};++d;
  }
 }
 return -1;
}
#endif
