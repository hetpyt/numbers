#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import queue

class FilteredQueue(queue.Queue):
    
    def put(self, item, block=True, timeout=None):
        # фильтрация строк
        str = item.strip()
        if str:
            # игнорируем пустые строки и строки содержащие только пробельные символы
            super(FilteredQueue, self).put(str, block, timeout)
    