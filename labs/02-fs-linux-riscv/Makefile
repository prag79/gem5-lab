# Lab 02 FS-mode artifacts. Fetched from dist.gem5.org once; cached
# afterwards in the writable workdir. Switched to v22-1 paths because the
# v23-0 directory at dist.gem5.org returns 404 (the artifacts themselves
# are gem5-version-agnostic: just an RV64 kernel and a busybox rootfs).

DIST_BASE := http://dist.gem5.org/dist/v22-1
KERNEL_URL := $(DIST_BASE)/kernels/riscv/static/bootloader-vmlinux-5.10
DISK_URL   := $(DIST_BASE)/images/riscv/busybox/riscv-disk.img.gz

KERNEL_MD5 := ac29fe5f71c096e6b2044b4e4d623edc
DISK_GZ_MD5 := d6126db9f6bed7774518ae25aa35f153

artifacts: bootloader-vmlinux-5.10 riscv-disk.img

bootloader-vmlinux-5.10:
	@echo "Fetching kernel ($(KERNEL_URL))..."
	curl -fSL -o $@ $(KERNEL_URL)
	@echo "$(KERNEL_MD5)  $@" | md5sum -c -

riscv-disk.img.gz:
	@echo "Fetching disk image ($(DISK_URL))..."
	curl -fSL -o $@ $(DISK_URL)
	@echo "$(DISK_GZ_MD5)  $@" | md5sum -c -

riscv-disk.img: riscv-disk.img.gz
	gunzip -kf $<

clean:
	rm -f bootloader-vmlinux-5.10 riscv-disk.img riscv-disk.img.gz

.PHONY: artifacts clean
