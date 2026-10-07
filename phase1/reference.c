#include "engine.h"
static const char input_state[]="21345671111111";
static const char *const names[]={"R","R2","R'","B","B2","B'","D","D2","D'"};
static void print(const char*s){register const char*a0 __asm__("a0")=s;register unsigned a7 __asm__("a7")=4;__asm__ volatile("ecall" : "+r"(a0) : "r"(a7) : "memory");}
int main(void){uint8_t z[7],path[11];unsigned seen=0,sum=0;for(unsigned i=0;i<7;i++){unsigned p=input_state[i]-'1',o=input_state[i+7]-'1';if(p>=7||o>=3||(seen&(1u<<p)))return 2;seen|=1u<<p;sum+=o;z[p]=i|(o<<3);}while(sum>=3)sum-=3;if(sum)return 2;uint32_t a=z[0]|(z[1]<<8)|(z[2]<<16)|((uint32_t)z[3]<<24),b=z[3]|(z[4]<<8)|(z[5]<<16)|((uint32_t)z[6]<<24);uint64_t nodes;int n=search(a,b,path,&nodes);if(n<0)return 1;for(int i=0;i<n;i++){print(names[path[i]]);print(" ");unsigned face=path[i]<3?0:path[i]<6?1:2,turns=path[i]-face*3+1;while(turns--){a=turn4(a,face);b=turn4(b,face);}}print("\n");return a!=GOAL_A||b!=GOAL_B;}
