#!/usr/bin/env python
# -*- coding: utf-8 -*-
from moop.configreader import ConfigReader
try:
    config = ConfigReader("config.cfg")
except Exception as e:
    print(e, e.__cause__)
    exit()

print(config)
print(config.get('paramgfdgsfgfd0'))
print(config.get('sdf'))