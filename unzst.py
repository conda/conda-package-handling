#!/usr/bin/env python
# Unpack zstd usin new thingy

from conda_package_handling import archive_utils_cy

a = archive_utils_cy.read_zstd(open("setup.py.zst", "rb").read)

print(f"read_zstd says {a}")
