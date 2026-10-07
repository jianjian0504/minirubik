#include <stdio.h>
#include <string.h>
#include "engine.h"
int main(int argc,char**argv){if(argc!=2||strlen(argv[1])!=14)return 2;uint8_t z[7],path[11];unsigned seen=0,sum=0;for(unsigned i=0;i<7;i++){unsigned p=argv[1][i]-'1',o=argv[1][i+7]-'1';if(p>=7||o>=3||(seen&(1<<p)))return 2;seen|=1<<p;sum+=o;z[p]=i|(o<<3);}if(sum%3)return 2;uint32_t a=z[0]|(z[1]<<8)|(z[2]<<16)|((uint32_t)z[3]<<24),b=z[3]|(z[4]<<8)|(z[5]<<16)|((uint32_t)z[6]<<24);uint64_t nodes;int n=search(a,b,path,&nodes);if(n<0)return 1;const char *names[]={"R","R2","R'","B","B2","B'","D","D2","D'"};for(int i=0;i<n;i++)printf("%s%s",i?" ":"",names[path[i]]);puts("");fprintf(stderr,"length=%d candidates=%llu\n",n,(unsigned long long)nodes);return fflush(stdout)!=0;}
