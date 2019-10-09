#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading.queue

class FilteredQueue(threading.queue.Queue):
    
    def put(self, item, block=True, timeout=None):
        # do some filtering things
        super(FilteredQueue, self).put(item, block, tumeout)
    