#!/usr/bin/env python
# -*- coding: utf-8 -*-
from moop.configreader import ConfigReader

#print(ConfigReader.__mro__)
config = ConfigReader("config.cfg")
if config.is_error():
    print(config.get_error())
#print(config)
#print(config.get('paramgfdgsfgfd0'))
#print(config.get('sdf'))