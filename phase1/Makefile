CC ?= cc
CFLAGS ?= -O3 -std=c99 -Wall -Wextra
RISCV_CC ?= riscv64-unknown-elf-gcc
.PHONY: all check full hard asm reference clean
all: compact verify

generate: generate.c original/solver.c
	$(CC) $(CFLAGS) generate.c -o $@
tables.c tables.inc pdb_reference.bin: generate
	./generate
compact: compact.c engine.h tables.c
	$(CC) $(CFLAGS) compact.c tables.c -o $@
verify: verify.c engine.h tables.c
	$(CC) $(CFLAGS) verify.c tables.c -o $@
check_tables: check_tables.c engine.h tables.c pdb_reference.bin
	$(CC) $(CFLAGS) check_tables.c tables.c -o $@
asm: tables.inc
	python3 build_asm.py
	python3 renderer.py
check: all check_tables asm
	./check_tables
	python3 check_vectors.py
	python3 check_renderer.py
hard: verify
	./verify
full: verify
	./verify --full
reference: reference.c reference-start.s reference.ld engine.h tables.c
	$(RISCV_CC) -O2 -march=rv32i -mabi=ilp32 -ffreestanding -fno-builtin -msmall-data-limit=0 -nostdlib -nostartfiles -Wl,-T,reference.ld reference-start.s reference.c tables.c -o reference.elf
	riscv64-unknown-elf-size -A reference.elf
	riscv64-unknown-elf-objdump -d reference.elf > reference-disassembly.txt
clean:
	rm -f compact verify generate check_tables rvcheck rvcheck-gui reference.elf
