hello-se.elf: hello-se.c
	riscv64-linux-gnu-gcc -O2 -static $< -o $@

clean:
	rm -f hello-se.elf
	rm -rf m5out-atomic m5out-o3

.PHONY: clean
