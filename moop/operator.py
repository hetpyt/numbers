#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector as sql

# создается при получении входящего звонка, отвечает за логику приема данных от абонента
class Operator:
    def __init__(self, config, caller_number):
        self._caller_number = caller_number
        
    def getCallerInfo(self):
        conn = sql.connect(
            host = server_host,
            port = server_port, 
            database = db_name,
            user = db_user,
            password = db_pass)
            
        pass
        
    