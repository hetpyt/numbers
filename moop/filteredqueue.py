#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import queue

class FilteredQueue(queue.Queue):
    
    def put(self, item, block=True, timeout=None):
        # do some filtering stuff
        super(FilteredQueue, self).put(item, block, timeout)
    