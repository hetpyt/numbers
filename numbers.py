#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import math

class Numbers:
    """Транслирует цифровое представление чисел в текстовое"""
    _PyMajorVersion = 3
    # максимальное число девятьсот девяность девять миллиардов ...
    _max_number = 999999999999.99999
    # род (мужской, женский, средний)
    _gender = "masculine", "feminine", "neuter"
    # представление нуля
    _zero = "ноль"
    # словарь представлений цифр, разделенных на классы в зависимости от позиции цифры в числе
    _number_class = {
        1 : {
            0 : ("", "", ""),
            1 : ("один", "одна", "одно"),
            2 : ("два", "две", "два"),
            3 : ("три", "три", "три"),
            4 : ("четыре", "четыре", "четыре"),
            5 : ("пять", "пять", "пять"),
            6 : ("шесть", "шесть", "шесть"),
            7 : ("семь", "семь", "семь"),
            8 : ("восемь", "восемь", "восемь"),
            9 : ("девять", "девять", "девять")
        },
        2 : {
            0 : "",
            1 : {
                0 : "десять",
                1 : "одиннадцать",
                2 : "двенадцать",
                3 : "тринадцать",
                4 : "четырнадцать",
                5 : "пятнадцать",
                6 : "шестнадцать",
                7 : "семнадцать",
                8 : "восемнадцать",
                9 : "девятнадцать"
            },
            2 : "двадцать",
            3 : "тридцать",
            4 : "сорок",
            5 : "пятьдесят",
            6 : "шестьдесят",
            7 : "семьдесят",
            8 : "восемьдесят",
            9 : "девяносто"
        },
        0 : {
            0 : "",
            1 : "сто",
            2 : "двести",
            3 : "триста",
            4 : "четыреста",
            5 : "пятьсот",
            6 : "шестьсот",
            7 : "семьсот",
            8 : "восемьсот",
            9 : "девятьсот"
        }
    }
    _integer_suffix = {
        4 : ("тысяча", "тысячи","тысяч"),
        7 : ("миллион", "миллиона", "миллионов"),
        10 : ("миллиард", "миллиарда", "миллиардов")
    }
    _fractional_suffix = {
        1 : ("десятая", "десятых"),
        2 : ("сотая", "сотых"),
        3 : ("тысячная", "тысячных"),
        4 : ("десятитысячная", "десятитысячных"),
        5 : ("стотысячная", "стотысячных")
    }
    
    
    def __init__(self):
        _PyMajorVersion = sys.version_info[0]
    
    def _is_string(self, value):
        if self._PyMajorVersion == 3:
            return isinstance(value, str)
        else:
            return isinstance(value, basestring)
            
    def convert(self, number, gender = "masculine"):
        number = round(float(number), 5)
        # проверка на размерность числа
        if number > self._max_number:
            return None
        # проверим вдруг в качестве рода передали число от 0 до 2
        if self._is_string(gender):
            gender = self._genders.index(gender)
        # разобьем число на целую и дробную части
        int_part, fract_part = tuple(format(number).split("."))
        # список результата
        result = []
        pos = len(int_part)
        if pos == 1 and int(int_part) == 0:
            # частный случай нуля
            return [self._zero]
        # признак начала последовательности из 1 и [0,9] начиная в позиции десяток
        # те для обработки чисел 11, 12 и тд до 19, тк тут два цифры идут одним словом
        is_11 = False
        while pos > 0:
            # число - цифра текущего разряда
            digit = int(int_part[len(int_part) - pos])
            # проверка нуля
#            if digit == 0 and len(int_part) > 1:
#                # пропускаем нули, если число не 0
#                pos -= 1
#                continue
                
            # класс разряда - сотни, десятки, единицы (в тч тысяч, миллионов и тд)
            num_class = pos % 3
            # текстовое представление текущего разряда
            str_digit = ""
            int_suffix = ""
            # определим суффикс
            if pos in self._integer_suffix:
                if digit == 1 and not is_11:
                    int_suffix = self._integer_suffix[pos][0]
                elif digit > 1 and digit < 5 and not is_11:
                    int_suffix = self._integer_suffix[pos][1]
                else:
                    int_suffix = self._integer_suffix[pos][2]
            # определим представление        
            if is_11:
                # была единица на классе 2 в предыдущей итерации
                str_digit = self._number_class[2][1][digit]
                if pos in self._integer_suffix:
                    int_suffix = self._integer_suffix[pos][2]
                is_11 = False
            else:
                if digit == 1 and num_class == 2:
                    # частный случай для десяток (10, 11, 12 и тд)
                    # выставляем признак и будем обрабатывать в следующей итерации
                    is_11 = True
                else:
                    if num_class == 1:
                        # здесь требуется уточнение рода (мужской, женский, средний)
                        gen = 0 # по умолчанию мужской
                        if pos == 4:
                            # для тысяч женский
                            gen = 1
                        elif pos == 1:
                            # род первого разряда задается в параметре функции
                            gen = gender
                        str_digit = self._number_class[num_class][digit][gen]
                    else:
                        str_digit = self._number_class[num_class][digit]
            # добавляем текстовое представление разряда в список результата 
            if str_digit:
                result.append(str_digit) 
            
            # добавим суффикс для 10, 7, 4 разрядов
            if int_suffix:
                result.append(int_suffix) 
            # инкремент счетчика разрядов
            pos -= 1
        # возврат результата
        return result