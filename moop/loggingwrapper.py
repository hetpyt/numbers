#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

APP_NAME = "moop"
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

def create_log(file_name, log_level):
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(log_level)
    file_h = logging.FileHandler(file_name)
    file_h.setFormatter(logging.Formatter('%(asctime)s (%(thread)d)%(name)s.%(module)s [%(levelname)s] : %(message)s'))
    logger.addHandler(file_h)
    return logger

def debug(msg):
    logging.getLogger(APP_NAME).debug(msg)
   
def info(msg):
    logging.getLogger(APP_NAME).info(msg)
    
def warning(msg):
    logging.getLogger(APP_NAME).warning(msg)
    
def error(msg):
    logging.getLogger(APP_NAME).error(msg)
    
def exception(msg):
    logging.getLogger(APP_NAME).exception(msg)
    
def critical(msg):
    logging.getLogger(APP_NAME).critical(msg)

           