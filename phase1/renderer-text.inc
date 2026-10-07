
# Solver's current state is in s0/s1. Preserve every s-register used here.
render:
 addi sp,sp,-32
 sw s2,0(sp)
 sw s3,4(sp)
 sw s4,8(sp)
 sw s5,12(sp)
 sw s6,16(sp)
 sw s7,20(sp)
 sw s8,24(sp)
 sw s9,28(sp)
 la t0,render_coords
 sw s0,0(t0)
 srli t1,s1,8
 sb t1,4(t0)
 srli t1,s1,16
 sb t1,5(t0)
 srli t1,s1,24
 sb t1,6(t0)
 li s4,LED_MATRIX_0_BASE
 li t0,LED_MATRIX_0_HEIGHT
 mv t1,s4
clear_y:
 li t2,LED_MATRIX_0_WIDTH
clear_x:
 sw zero,0(t1)
 addi t1,t1,4
 addi t2,t2,-1
 bnez t2,clear_x
 addi t0,t0,-1
 bnez t0,clear_y
 la s3,facelets
 li s2,24
facelet_loop:
 lbu s5,0(s3)
 lbu s6,1(s3)
 lbu t0,2(s3)
 lbu t1,3(s3)
 beqz t0,fixed_corner
 addi t0,t0,-1
 la t2,render_coords
 li t3,0
find_corner:
 lbu t4,0(t2)
 andi t5,t4,7
 beq t5,t0,corner_found
 addi t2,t2,1
 addi t3,t3,1
 j find_corner
corner_found:
 srli t4,t4,3
 sub t1,t1,t4
 bge t1,zero,slot_ready
 addi t1,t1,3
slot_ready:
 addi t3,t3,1
 j color_index
fixed_corner:
 li t3,0
color_index:
 slli t0,t3,1
 add t0,t0,t3
 add t0,t0,t1
 la t1,corner_colors
 add t0,t0,t1
 lbu t0,0(t0)
 slli t0,t0,2
 la t1,palette
 add t0,t0,t1
 lw s7,0(t0)
 # Address = BASE + 4*(y*WIDTH+x); repeated addition avoids M extension.
 mv t0,s6
 mv t1,s5
 li t2,LED_MATRIX_0_WIDTH
 beqz t0,address_ready
row_offset:
 add t1,t1,t2
 addi t0,t0,-1
 bnez t0,row_offset
address_ready:
 slli t1,t1,2
 add s8,s4,t1
 slli t2,t2,2
 li s9,3
paint_row:
 sw s7,0(s8)
 sw s7,4(s8)
 sw s7,8(s8)
 sw s7,12(s8)
 add s8,s8,t2
 addi s9,s9,-1
 bnez s9,paint_row
 addi s3,s3,4
 addi s2,s2,-1
 bnez s2,facelet_loop
 # Visible dwell; excluded entirely from the CLI build.
 li t0,250000
dwell:
 addi t0,t0,-1
 bnez t0,dwell
 lw s2,0(sp)
 lw s3,4(sp)
 lw s4,8(sp)
 lw s5,12(sp)
 lw s6,16(sp)
 lw s7,20(sp)
 lw s8,24(sp)
 lw s9,28(sp)
 addi sp,sp,32
 ret
