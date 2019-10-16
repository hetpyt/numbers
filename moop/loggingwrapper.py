#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import inspect

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
    file_h.setFormatter(logging.Formatter('%(asctime)s (%(thread)d)%(name)s [%(levelname)s] : %(message)s'))
    logger.addHandler(file_h)
    return logger

def debug(msg):
    try:
        frm = inspect.stack()[1]
        mod_name = inspect.getmodule(frm[0]).__name__
    except Exception as e:
        mod_name = "none"
    logger = logging.getLogger(".".join([APP_NAME, mod_name])).debug(msg)
    
def info(msg):
    try:
        frm = inspect.stack()[1]
        mod_name = inspect.getmodule(frm[0]).__name__
    except Exception as e:
        mod_name = "none"
    logger = logging.getLogger(".".join([APP_NAME, mod_name])).info(msg)
    
def warning(msg):
    try:
        frm = inspect.stack()[1]
        mod_name = inspect.getmodule(frm[0]).__name__
    except Exception as e:
        mod_name = "none"
    logger = logging.getLogger(".".join([APP_NAME, mod_name])).warning(msg)
    
def error(msg):
    try:
        frm = inspect.stack()[1]
        mod_name = inspect.getmodule(frm[0]).__name__
    except Exception as e:
        mod_name = "none"
    logger = logging.getLogger(".".join([APP_NAME, mod_name])).error(msg)
    
def exception(msg):
    try:
        frm = inspect.stack()[1]
        mod_name = inspect.getmodule(frm[0]).__name__
    except Exception as e:
        mod_name = "none"
    logger = logging.getLogger(".".join([APP_NAME, mod_name])).exception(msg)
    
def critical(msg):
    try:
        frm = inspect.stack()[1]
        mod_name = inspect.getmodule(frm[0]).__name__
    except Exception as e:
        mod_name = "none"
    logger = logging.getLogger(".".join([APP_NAME, mod_name])).critical(msg)

           