#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import __main__ as Main

class ConfigReader(dict):
    """read configuration from file"""
    
    def __init__(self, def_conf_name):
        super().__init__()
        if not def_conf_name:
            raise Exception("default config file name is not defined")
        self._def_config_name = def_conf_name
        self._config_readed = False
        self._readed_file_name = ""
        self._search_paths = []
        self._search_paths.append(os.path.dirname(os.path.abspath(Main.__file__)))
        if os.sys.platform.lower().find("linux"):
            self._search_paths += ["/usr/local/etc", "/etc"]
    
        for path_name in self._search_paths:
            file_name = os.path.join(path_name, self._def_config_name)
            if os.path.exists(file_name):
                self._readed_file_name = file_name
                self._read(file_name)
        
    def __str__(self):
        res = ''
        for key in self:
            res += key + '=' + str(self.get(key)) + os.linesep
            
        return res
    
    def is_readed(self):
        return self._config_readed
        
    def get_file_name(self):
        return self._readed_file_name
        
    # проверяет существуют (есть в словаре и не пустые) ли параметры переданные в кортеже
    def is_params_exists(self, keys):
        for key in keys:
            if not self.get(key):
                return False
        return True    
    
    def _read(self, file_name):
        # открываем файл на чтение
        try: 
            file = open(file_name, "r", encoding='utf-8', newline = os.linesep)
            #print(file_name)
        except os.OSError as e:
            raise Exception("Can't open config file '{}'".format(_file_name)) from e
            
        else:
            with file:
                line_counter = 0
                for line in file:
                    line_counter += 1
                    line = line.strip()
                    if (not line) or line[0] in '#;/':
                        continue
                    key, value = tuple([s.strip() for s in line.split('=', 1)])
                    self.__setitem__(key, value)
                    
        self._config_readed = True