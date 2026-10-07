from pathlib import Path
p=Path('.')
a='''# Hand-written RV32I search; generated only to join immutable data and variants.
.data
.align 2
input_state: .asciz "21345671111111"
space: .asciz " "
newline: .asciz "\\n"
passmsg: .asciz "PASS: path reaches solved state\\n"
failmsg: .asciz "FAIL: invalid state or solution\\n"
'''
for i,n in enumerate(['R','R2',"R'",'B','B2',"B'",'D','D2',"D'"]):a+=f'name{i}: .asciz "{n}"\n'
a+='''.align 2
names: .word name0,name1,name2,name3,name4,name5,name6,name7,name8
coords: .space 8
path: .space 12
.align 2
frames: .space 288
'''
a+=Path('tables.inc').read_text()
a+='''
.text
.globl main
main:
 la t0,input_state
 la t1,coords
 li t2,0
 li t3,0
 li t4,0
parse_loop:
 lbu t5,0(t0)
 addi t5,t5,-49
 li t6,7
 bgeu t5,t6,fail
 li a0,1
 sll a0,a0,t5
 and a1,t3,a0
 bnez a1,fail
 or t3,t3,a0
 lbu a1,7(t0)
 addi a1,a1,-49
 li t6,3
 bgeu a1,t6,fail
 add t4,t4,a1
 slli a1,a1,3
 or a1,a1,t2
 add a0,t1,t5
 sb a1,0(a0)
 addi t0,t0,1
 addi t2,t2,1
 li t6,7
 bltu t2,t6,parse_loop
 lbu t5,7(t0)
 bnez t5,fail
mod_loop:
 li t6,3
 bltu t4,t6,mod_done
 addi t4,t4,-3
 j mod_loop
mod_done:
 bnez t4,fail
 lw s0,0(t1)
 lbu s1,3(t1)
 lbu t0,4(t1)
 slli t0,t0,8
 or s1,s1,t0
 lbu t0,5(t1)
 slli t0,t0,16
 or s1,s1,t0
 lbu t0,6(t1)
 slli t0,t0,24
 or s1,s1,t0
 mv a0,s0
 mv a1,s1
 jal ra,heuristic
 mv s2,a0
 la s5,path
bound_start:
 li t0,12
 bgeu s2,t0,fail
 li s3,0
 la s4,frames
 sw s0,0(s4)
 sw s1,4(s4)
 sw s0,8(s4)
 sw s1,12(s4)
 sw zero,16(s4)
 li t0,3
 sw t0,20(s4)
search_loop:
 lw t0,0(s4)
 li t1,0x03020100
 bne t0,t1,not_goal
 lw t0,4(s4)
 li t1,0x06050403
 beq t0,t1,found
not_goal:
 beq s3,s2,backtrack
 lw s7,16(s4)
 li t0,9
 beq s7,t0,backtrack
 addi t0,s7,1
 sw t0,16(s4)
 li s8,0
 li t0,3
 bltu s7,t0,face_ready
 li s8,1
 li t0,6
 bltu s7,t0,face_ready
 li s8,2
face_ready:
 slli t0,s8,1
 add t0,t0,s8
 sub s9,s7,t0
 lw t0,20(s4)
 beq s8,t0,search_loop
 bnez s9,rolling_ready
 lw t0,0(s4)
 sw t0,8(s4)
 lw t0,4(s4)
 sw t0,12(s4)
rolling_ready:
 lw a0,8(s4)
 mv a1,s8
 jal ra,turn4
 sw a0,8(s4)
 lw a0,12(s4)
 mv a1,s8
 jal ra,turn4
 sw a0,12(s4)
 mv a1,a0
 lw a0,8(s4)
 jal ra,heuristic
 sub t0,s2,s3
 addi t0,t0,-1
 bltu t0,a0,search_loop
 add t0,s5,s3
 sb s7,0(t0)
 lw t0,8(s4)
 lw t1,12(s4)
 addi s4,s4,24
 addi s3,s3,1
 sw t0,0(s4)
 sw t1,4(s4)
 sw t0,8(s4)
 sw t1,12(s4)
 sw zero,16(s4)
 sw s8,20(s4)
 j search_loop
backtrack:
 beqz s3,next_bound
 addi s3,s3,-1
 addi s4,s4,-24
 j search_loop
next_bound:
 addi s2,s2,1
 j bound_start
found:
 mv s10,s3
 li s11,0
 # RENDER_INITIAL
replay_loop:
 beq s11,s10,replay_done
 add t0,s5,s11
 lbu s7,0(t0)
 la t0,names
 slli t1,s7,2
 add t0,t0,t1
 lw a0,0(t0)
 li a7,4
 ecall
 la a0,space
 li a7,4
 ecall
 li s8,0
 li t0,3
 bltu s7,t0,replay_face
 li s8,1
 li t0,6
 bltu s7,t0,replay_face
 li s8,2
replay_face:
 slli t0,s8,1
 add t0,t0,s8
 sub s9,s7,t0
 addi s9,s9,1
replay_turn:
 mv a0,s0
 mv a1,s8
 jal ra,turn4
 mv s0,a0
 mv a0,s1
 mv a1,s8
 jal ra,turn4
 mv s1,a0
 addi s9,s9,-1
 bnez s9,replay_turn
 # RENDER_STEP
 addi s11,s11,1
 j replay_loop
replay_done:
 li t0,0x03020100
 bne s0,t0,fail
 li t0,0x06050403
 bne s1,t0,fail
 la a0,newline
 li a7,4
 ecall
 la a0,passmsg
 li a7,4
 ecall
 li a0,0
 li a7,93
 ecall
fail:
 la a0,failmsg
 li a7,4
 ecall
 li a0,1
 li a7,93
 ecall
# a0: four corner coordinates; a1: face. Leaf, caller-saved only.
turn4:
 la t0,turn_map
 slli t1,a1,5
 add t0,t0,t1
 li t2,0
'''
for k in range(4):
 a+=f' srli t3,a0,{8*k}\n andi t3,t3,31\n add t3,t0,t3\n lbu t3,0(t3)\n slli t3,t3,{8*k}\n or t2,t2,t3\n'
a+=' mv a0,t2\n ret\n# Two nibble lookups, maximum; no multiply/divide.\nheuristic:\n mv a2,a0\n mv a3,a1\n'
for grp in range(2):
 reg='a2' if grp==0 else 'a3'
 a+=f' # group {grp}\n andi t0,{reg},7\n'
 for shift,mask in [(5,56),(10,448),(15,3584)]:
  a+=f' srli t1,{reg},{shift}\n li t2,{mask}\n and t1,t1,t2\n or t0,t0,t1\n'
 a+=' slli t0,t0,1\n la t1,pos_rank\n add t0,t0,t1\n lhu t0,0(t0)\n slli t1,t0,6\n slli t2,t0,4\n add t0,t0,t1\n add t0,t0,t2\n'
 a+=f' srli t1,{reg},3\n andi t1,t1,3\n'
 for shift,mask in [(9,12),(15,48),(21,192)]:a+=f' srli t2,{reg},{shift}\n andi t2,t2,{mask}\n or t1,t1,t2\n'
 a+=' la t2,ori_rank\n add t1,t1,t2\n lbu t1,0(t1)\n add t0,t0,t1\n andi t1,t0,1\n slli t1,t1,2\n srli t0,t0,1\n'
 a+=f' la t2,pdb_{"a" if grp==0 else "b"}\n add t0,t0,t2\n lbu t0,0(t0)\n srl t0,t0,t1\n andi t0,t0,15\n mv a{4+grp},t0\n'
a+=' mv a0,a4\n bgeu a4,a5,h_done\n mv a0,a5\nh_done:\n ret\n'
Path('search.s').write_text(a)
Path('solver-cli.s').write_text(a)
