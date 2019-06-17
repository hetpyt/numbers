#!/usr/bin/env python
# -*- coding: utf-8 -*-

class NumberSpeaker:
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
    # суффиксы частей кратных 1000
    _10multiple_suffix = {
        4 : ("тысяча", "тысячи","тысяч"),
        7 : ("миллион", "миллиона", "миллионов"),
        10 : ("миллиард", "миллиарда", "миллиардов")
    }
    # суффикс целой части
    _integer_suffix = ("целая", "целые", "целых")
    # суффиксы дробной части (до 5 цифр после запятой)
    _fractional_suffix = {
        1 : ("десятая", "десятые", "десятых"),
        2 : ("сотая", "сотые", "сотых"),
        3 : ("тысячная", "тысячные", "тысячных"),
        4 : ("десятитысячная", "десятитысячные", "десятитысячных"),
        5 : ("стотысячная", "стотысячные", "стотысячных")
    }
    
    def __init__(self):
        pass
    
    def _choose_suffix(self, suffixes, digit):
        if digit == 1:
            return suffixes[0]
        elif digit > 1 and digit < 5:
            return suffixes[1]
        else:
            return suffixes[2]
    
    def _convert(self, result, num_part, gender = 0):
        # счетчик позиции (разряда) цифры в числе начиная с 1 от десятичной точки справа налево
        pos = len(num_part)
        if pos == 1 and int(num_part) == 0:
            # частный случай нуля
            result.append(self._zero)
            return 0
        # признак начала последовательности из 1 и [0,9] начиная в позиции десяток
        # те для обработки чисел 11, 12 и тд до 19, тк тут два цифры идут одним словом
        is_11 = False
        while pos > 0:
            # число - цифра текущего разряда
            digit = int(num_part[len(num_part) - pos])
            # класс разряда - сотни, десятки, единицы (в тч тысяч, миллионов и тд)
            num_class = pos % 3
            # текстовое представление текущего разряда
            str_digit = ""
            suffix = ""
            # определим суффикс
            if pos in self._10multiple_suffix:
                if is_11:
                    suffix = self._10multiple_suffix[pos][2]
                else:
                    suffix = self._choose_suffix(self._10multiple_suffix[pos], digit)
            # определим представление        
            if is_11:
                # была единица на классе 2 в предыдущей итерации
                str_digit = self._number_class[2][1][digit]
                is_11 = False
                # установим digit в двухциферное число чтобы вернуть его из функции если оно последнее
                digit += 10
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
            if suffix:
                result.append(suffix) 
            # декремент счетчика разрядов
            pos -= 1
        # возврат результата
        return digit 
        
    def convert(self, number, int_gender = 0, fract_gender = 0, unit = None, int_unit = None, fract_unit = None):
        # преобразуем к числу с плавающей точкой и округляем до 5 знаков после запятой
        number = round(float(number), 5)
        # проверка на размерность числа
        if number > self._max_number:
            return None
        # разобьем число на целую и дробную части
        int_part, fract_part = tuple(format(number).split("."))
        non_zero_fract_part = 0 != int(fract_part)
        # список результата
        result = []
        if None == int_unit:
            # не задана единица для целой части
            if non_zero_fract_part:
                # и есть ненулевая дробная часть
                # подставляем стандартный суффикс "целая" и меняем род на женский
                int_unit = self._integer_suffix
                int_gender = 1
            else:
                # нет дробной части - нет единицы
                int_unit = ("", "", "")
        # последняя цифра целой части
        last_int_digit = self._convert(result, int_part, int_gender)
        result.append(self._choose_suffix(int_unit, last_int_digit))
        if non_zero_fract_part:
            # конвертируем только ненулевые дробные части
            if None == fract_unit:
                # не задана единица для дробной части
                # подставляем стандартные
                fract_unit = self._fractional_suffix[len(fract_part)]
                fract_gender = 1
            result.append(self._choose_suffix(fract_unit, self._convert(result, fract_part, fract_gender)))
        # общая единица измерения
        if None != unit:
            # передана общая единица измерения - она ставится в конец
            if non_zero_fract_part:
                # для ненулевой дробной части берется вторая форма, пр "одна целая одна сотая литра"
                result.append(unit[1])
            else:
                # для нулевой дробной части форма определяется по последней цифре целой
                result.append(self._choose_suffix(unit, last_int_digit))
        # возврат результата
        return result
        