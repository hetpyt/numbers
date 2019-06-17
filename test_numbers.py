#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import math
from numberspeaker import NumberSpeaker
# создание экземляра класса - объекта
Num = NumberSpeaker()

# цикл из десяти случайных чисел размером от 0 до _max_number
print("===== convert =====")
for i in range(10):
    # генерация случайного числа
    n = round(random.randint(0, math.floor(Num._max_number)) / random.randint(1, 9), 5)
    # печать числа цифрами
    print(n)
    # печать числа прописью
    # первый параметр функции convert - число для получения представления
    # второй параметр - род, в котором представление нужно вывести (0 - мужской, 1 - женский, 2 - средний)
    print(" ".join(Num.convert(n)))
print("===== convert_by_numeral =====")
for i in range(10):
    # генерация случайного числа
    n = round(random.randint(0, math.floor(Num._max_number)) / random.randint(1, 9), 5)
    # печать числа цифрами
    print(n)
    # печать числа прописью
    # первый параметр функции convert - число для получения представления
    # второй параметр - род, в котором представление нужно вывести (0 - мужской, 1 - женский, 2 - средний)
    print(" ".join(Num.convert_by_numeral(n)))
print("===== convert_by_groups(3) =====")
for i in range(10):
    # генерация случайного числа
    n = round(random.randint(0, math.floor(Num._max_number)) / random.randint(1, 9), 5)
    # печать числа цифрами
    print(n)
    # печать числа прописью
    # первый параметр функции convert - число для получения представления
    # второй параметр - род, в котором представление нужно вывести (0 - мужской, 1 - женский, 2 - средний)
    print(" ".join(Num.convert_by_groups(n, 3)))
print("===== convert_by_groups(2) =====")
for i in range(10):
    # генерация случайного числа
    n = round(random.randint(0, math.floor(Num._max_number)) / random.randint(1, 9), 5)
    # печать числа цифрами
    print(n)
    # печать числа прописью
    # первый параметр функции convert - число для получения представления
    # второй параметр - род, в котором представление нужно вывести (0 - мужской, 1 - женский, 2 - средний)
    print(" ".join(Num.convert_by_groups(n, 2)))


# ручные тесты
# ноль
print(0, " ".join(Num.convert(0, 0, 0)))
# проверка 11
print(11, " ".join(Num.convert(11, 0, 0)))
print(11011, " ".join(Num.convert(11011, 0, 1)))
# с нулями
print(100340001, " ".join(Num.convert(100340001, 1, 1)))

print(110010, " ".join(Num.convert_by_groups(110010, 3)))


