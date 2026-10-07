#include <assert.h>
#include <stdio.h>
#include "engine.h"
int main(void){FILE*f=fopen("pdb_reference.bin","rb");assert(f);for(unsigned g=0;g<2;g++){const uint8_t*t=g?pdb_b:pdb_a;unsigned max=0;for(unsigned i=0;i<68040;i++){int x=fgetc(f);unsigned got=(t[i>>1]>>((i&1)*4))&15;assert(x>=0&&x==got);if(got>max)max=got;}assert(max==8);assert(get4(t,g?GOAL_B:GOAL_A)==0);}assert(fgetc(f)==EOF);fclose(f);puts("H2/H4 PASS: full PDBs, maximum 8, solved 0; all even/odd packed entries equal unpacked BFS references");return 0;}
