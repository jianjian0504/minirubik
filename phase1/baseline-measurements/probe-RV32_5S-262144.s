.equ NWORDS,262144
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
