#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class ConfigReader:
    """read configuration from file"""
    def __init__(self):
        self._cur_dir = os.path.dirname(__file__)
        
    def read(self, file_name):
        pass