NAME       := dtcmp
SRC_EXT    := gz

TEST_PACKAGES := $(NAME)-openmpi3-devel $(NAME)-mpich-devel

include packaging/Makefile_packaging.mk

