#!/usr/bin/env python
"""
Replace usage section of README.md with current help text.
"""

import pathlib
import subprocess
import sys

process = subprocess.run(["cph", "-h"], capture_output=True, encoding="utf-8")
usage = process.stdout

readme = pathlib.Path("README.md")
text = readme.read_text()

output = []

lines = iter(text.splitlines())
for line in lines:
    output.append(line)
    if line.startswith("```"):
        break

output.append(usage)
output.append("```")
for line in lines:
    if line.startswith("```"):
        break

output.extend(lines)

new_text = "\n".join(output) + "\n"
if new_text != text:
    readme.write_text(new_text)
    sys.exit(0)

sys.exit(1)
