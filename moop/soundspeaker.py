#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import simpleaudio as SA
import wave
from moop.numberspeaker import NumberSpeaker
from moop.ierror import IError

class SoundSpeaker(NumberSpeaker, IError):
    """speak the sequence"""
    def __init__(self, resource_path):
        self.reset_error()
        self._res_path = resource_path
        self._zero = "0"
        self._dot = "dot"
        # словарь имен файлов ресурсов с произносимыми цифрами и суффиксами, разделенныч на классы в зависимости от позиции цифры в числе
        self._number_class = {
            1 : {
                0 : ("", "", ""),
                1 : ("1m", "1f", "1n"),
                2 : ("2", "2f", "2"),
                3 : ("3", "3", "3"),
                4 : ("4", "4", "4"),
                5 : ("5", "5", "5"),
                6 : ("6", "6", "6"),
                7 : ("7", "7", "7"),
                8 : ("8", "8", "8"),
                9 : ("9", "9", "9")
            },
            2 : {
                0 : "",
                1 : {
                    0 : "10",
                    1 : "11",
                    2 : "12",
                    3 : "13",
                    4 : "14",
                    5 : "15",
                    6 : "16",
                    7 : "17",
                    8 : "18",
                    9 : "19"
                },
                2 : "20",
                3 : "30",
                4 : "40",
                5 : "50",
                6 : "60",
                7 : "70",
                8 : "80",
                9 : "90"
            },
            0 : {
                0 : "",
                1 : "100",
                2 : "200",
                3 : "300",
                4 : "400",
                5 : "500",
                6 : "600",
                7 : "700",
                8 : "800",
                9 : "900"
            }
        }
        # суффиксы частей кратных 1000
        self._10multiple_suffix = {
            4 : ("1k_1", "1k_24","1k_5"),
            7 : ("1kk_1", "1kk_24", "1kk_5"),
            10 : ("1kkk_1", "1_kkk_24", "1_kkk_5")
        }
        # суффикс целой части
        self._integer_suffix = ("int_1", "int_24", "int_5")
        # суффиксы дробной части (до 5 цифр после запятой)
        self._fractional_suffix = {
            1 : ("10-1_1", "10-1_24", "10-1_5"),
            2 : ("10-2_1", "10-2_24", "10-2_5"),
            3 : ("10-3_1", "10-3_24", "10-3_5"),
            4 : ("10-4_1", "10-4_24", "10-4_5"),
            5 : ("10-5_1", "10-5_24", "10-5_5")
        }
        
    def speak(self, sequence):
        
        #try:
        data = bytes()
        get_params = True
        for word in sequence:
            res_name = os.path.join(self._res_path, word + '.wav')
            try:
                with wave.open(res_name, 'rb') as wr:
                    if get_params:
                        get_params = False
                        nc = wr.getnchannels()
                        bps = wr.getsampwidth()
                        fr = wr.getframerate()
                    data = data + wr.readframes(wr.getnframes())
            except FileNotFoundError as e:
                self._set_error("Can't open resource file: {}".format(e))
                return
            except wave.Error as e:
                self._set_error("Resource file is not valid wave file: {}".format(e))
                return
        play_obj = SA.play_buffer(data, nc, bps, fr)
        play_obj.wait_done()
