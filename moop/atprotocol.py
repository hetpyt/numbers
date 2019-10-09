#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class AtProtocol:
    ARGIMENTS_SEPARATOR = ","
    COMMAND_SEPARATOR = ":"
    SUPPORTED_COMMANDS = {
        "ATA" : {
            "SUCCESS" : ("OK"),
            "FAIL" : ("ERROR")
        },
        "ATH" : {
            "SUCCESS" : ("OK"),
            "FAIL" : None
        },
        "AT+DDET=1,0,0,0" : {
            "SUCCES" : ("OK"),
            "FAIL" : ("ERROR")
        },
        "AT+DDET=0" : {
            "SUCCES" : ("OK"),
            "FAIL" : ("ERROR")
        },
    }
    # Unsolicited results
    UNSOLICITED_RESULTS = {
        "RING" : {
        
        },
        "+CCWA" : {
            "PARAMS" : ("NUMBER", "TYPE", "CLASS")
        }
    }
    
    def __init__(self):
        pass
    
    