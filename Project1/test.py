# -*- coding: utf-8 -*-
# @Time    : 2019/10/25 10:39 上午
# @Author  : Zhou Liang
# @File    : test.py
# @Software: PyCharm

def twos_complement_to_value(input_str):
    unsigned_str = input_str[1:]
    for i in range(31):  # 无符号部分按位取反
        if unsigned_str[i] == '0':
            unsigned_str = unsigned_str[:i] + '1' + unsigned_str[i + 1:]
        else:
            unsigned_str = unsigned_str[:i] + '0' + unsigned_str[i + 1:]
    abs_value = int(unsigned_str, 2) + 1
    value = abs_value if input_str[0] == '0' else abs_value * (-1)

    print(value)



twos_complement_to_value('11111111111111111111111111111111')
