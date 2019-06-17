#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import math
from numberspeaker import NumberSpeaker
# создание экземляра класса - объекта
Num = NumberSpeaker()

int_unit = ("рубль", "рубля", "рублей")
fract_unit = ("копейка", "копейки", "копеек")
# цикл из десяти случайных чисел размером от 0 до _max_number
for i in range(10):
    # генерация случайного числа
    n = round(random.randint(0, math.floor(99999)) / random.randint(1, 9), 5)
    # печать числа цифрами
    print(n)
    # печать числа прописью
    # первый параметр функции convert - число для получения представления
    # второй параметр - род, в котором представление нужно вывести (0 - мужской, 1 - женский, 2 - средний)
    print(" ".join(Num.convert(n, 0, 1, None, int_unit, fract_unit)))
    
# ручные тесты
# ноль
print(0, " ".join(Num.convert(0, 0, 1, None, int_unit, fract_unit)))
# проверка 11
print(11.01, " ".join(Num.convert(11.01, 0, 1, None, int_unit, fract_unit)))
print(11011.31, " ".join(Num.convert(11011.31, 0, 1, None, int_unit, fract_unit)))
# с нулями
print(100340001.11, " ".join(Num.convert(100340001.11, 0, 1, None, int_unit, fract_unit)))

unit = ("литр", "литра", "литров")
print(0, " ".join(Num.convert(0, 0, 1, unit)))
# проверка 11
print(11.02, " ".join(Num.convert(11.01, 0, 1, unit)))
print(11011.31, " ".join(Num.convert(11011.31, 0, 1, unit)))
print(11011.35, " ".join(Num.convert(11011.35, 0, 1, unit)))
# с нулями
print(100340001.11, " ".join(Num.convert(100340001.11, 0, 1, unit)))


