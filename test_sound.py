#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import sys

from pyglet.gl import *
import pyglet
from pyglet.window import key

script_dir = os.path.dirname(__file__)

#pyglet.options['audio'] = ('openal', 'pulse', 'directsound', 'silent')
pyglet.resource.path = ['res']
pyglet.resource.reindex()

sounds = []

for i in range(10):
    sounds.append(pyglet.resource.media(format(i) + ".wav", streaming=False))

#window = pyglet.window.Window(640, 480)

def update(dt):
    index = random.randint(0, 9)
    print(index)
    sounds[index].play()
        
pyglet.clock.schedule_interval(update, 1)

pyglet.app.run()
