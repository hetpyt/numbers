#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import math
from numbers import Numbers
# создание экземляра класса - объекта
Num = Numbers()

# цикл из десяти случайных чисел размером от 0 до _max_number
for i in range(10):
    # генерация случайного числа
    n = random.randint(0, math.floor(Num._max_number))
    # печать числа цифрами
    print(n)
    # печать числа прописью
    # первый параметр функции convert - число для получения представления
    # второй параметр - род, в котором представление нужно вывести (0 - мужской, 1 - женский, 2 - средний)
    print(" ".join(Num.convert(n, 0)))
    
# ручные тесты
# ноль
print(0, " ".join(Num.convert(0, 0)))
# проверка 11
print(11, " ".join(Num.convert(11, 0)))
print(11011, " ".join(Num.convert(11011, 0)))
# с нулями
print(100340001, " ".join(Num.convert(100340001, 1)))



