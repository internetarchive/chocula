#!/usr/bin/env python3

import sys
import surt

for line in sys.stdin:
    url = line.strip()
    if not url:
        continue
    as_surt = surt.surt(url)
    print(as_surt)


