#!/usr/bin/env python
# -*- coding: utf-8 -*-

from soundspeaker import SoundSpeaker

sp = SoundSpeaker()

print(17036)
sp.speak(sp.convert_by_numeral(17036))

print(340001)
sp.speak(sp.convert_by_groups(340001, 3))

print(249411.56)
sp.speak(sp.convert(249411.56))

print("Здравствуйте, уважаемый Андрей Сергеевич")
sp.speak(["zero_special"])