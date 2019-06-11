#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import math
from numbers import Numbers

Num = Numbers()
for i in range(10):
    n = random.randint(0, math.floor(Num._max_number))
    print(n)
    print(" ".join(Num.convert(n, 0)))
