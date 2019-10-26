# -*- coding: utf-8 -*-
# @Time    : 2019/10/25 10:39 上午
# @Author  : Zhou Liang
# @File    : test.py
# @Software: PyCharm

import re
MIPS_STATUS={}
INSTRUCTION_SEQUENCE={256: 'ADD R1, R0, R0', 260: 'ADDI R2, R0, #3', 264: 'BEQ R1, R2, #68', 268: 'SLL R16, R1, #2', 272: 'LW R3, 340(R16)', 276: 'LW R4, 360(R16)', 280: 'LW R5, 380(R16)', 284: 'MUL R5, R3, R4', 288: 'BEQ R5, R0, #28', 292: 'BGTZ R5, #16', 296: 'ADD R6, R3, R4', 300: 'SUB R5, R6, R5', 304: 'J #324', 308: 'BLTZ R5, #4', 312: 'SLL R5, R5, #2', 316: 'J #324', 320: 'ADDI R5, R5, #12', 324: 'SW R5, 380(R16)', 328: 'ADDI R1, R1, #1', 332: 'J #264', 336: 'BREAK'}
MIPS_STATUS['Registers']=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MIPS_STATUS['Data']={340: -1, 344: -2, 348: -3, 352: 1, 356: 2, 360: 4, 364: -4, 368: 10, 372: 7, 376: 9, 380: 1, 384: 0, 388: -1, 392: 1, 396: -1, 400: 0, 404: 0, 408: 0, 412: 0, 416: 0, 420: 0, 424: 0, 428: 0, 432: 0}

d = {256: 'ADD R1, R0, R0', 260: 'ADDI R2, R0, #3', 264: 'BEQ R1, R2, #68', 268: 'SLL R16, R1, #2', 272: 'LW R3, 340(R16)', 276: 'LW R4, 360(R16)', 280: 'LW R5, 380(R16)', 284: 'MUL R5, R3, R4', 288: 'BEQ R5, R0, #28', 292: 'BGTZ R5, #16', 296: 'ADD R6, R3, R4', 300: 'SUB R5, R6, R5', 304: 'J #324', 308: 'BLTZ R5, #4', 312: 'SLL R5, R5, #2', 316: 'J #324', 320: 'ADDI R5, R5, #12', 324: 'SW R5, 380(R16)', 328: 'ADDI R1, R1, #1', 332: 'J #264', 336: 'BREAK'}

v = 'ADD R6, R3, R4'
# rs_index = int(v[4:].replace(" ", "").split(',')[0][1:])
# rt_index = int(v[4:].replace(" ", "").split(',')[1][1:])
# offset = int(v[4:].replace(" ", "").split(',')[2][1:])
# # rt = v[3:].replace(" ", "").split(',')[0][1:]
# comma_index = v[3:].replace(" ", "").index(',')
# left_parenthesis_index = v[3:].replace(" ", "").index('(')
# offset = v[3:].replace(" ", "")[comma_index+1:left_parenthesis_index]
# base = v[3:].replace(" ", "")[left_parenthesis_index+2:-1]

# print(rs_index, rt_index, offset)
#
# for inst in INSTRUCTION_SEQUENCE.values():
#     print(inst)

MACHINE_WORD_LENGTH = 32

def twos_complement_to_value(input_str):  # 二进制补码转整数真值
    unsigned_str = input_str[1:]
    if input_str[0] == '1':
        for i in range(31):  # 将负数补码的无符号部分按位取反
            if unsigned_str[i] == '0':
                unsigned_str = unsigned_str[:i] + '1' + unsigned_str[i + 1:]
            else:
                unsigned_str = unsigned_str[:i] + '0' + unsigned_str[i + 1:]
        abs_value = int(unsigned_str, 2) + 1
        value = abs_value if input_str[0] == '0' else abs_value * (-1)
    else:
        value = int(unsigned_str, 2)
    return value


def value_to_twos_complement(value):  # 整数真值转换为二进制补码，要求输入的真值在32位补码可表示的范围内
    global MACHINE_WORD_LENGTH
    if str(value)[0] == '-':  # 负数
        abs_value = value * -1
        binary_value_str = str(bin(abs_value))[2:]
        # print(binary_value_str)
        if len(binary_value_str) < MACHINE_WORD_LENGTH - 1:
            for i in range(MACHINE_WORD_LENGTH - 1 - len(binary_value_str)):
                binary_value_str = '0' + binary_value_str
        elif len(binary_value_str) == MACHINE_WORD_LENGTH:  # 解决2147483648转为二进制的问题
            binary_value_str = binary_value_str[1:]
        # print(binary_value_str)
        for i in range(MACHINE_WORD_LENGTH - 1):  # 按位取反
            if binary_value_str[i] == '0':
                binary_value_str = binary_value_str[:i] + '1' + binary_value_str[i + 1:]
            else:
                binary_value_str = binary_value_str[:i] + '0' + binary_value_str[i + 1:]
        # print(binary_value_str)
        last_zero_index = binary_value_str.rfind('0')  # 加一
        if last_zero_index != -1:
            binary_value_str = binary_value_str[:last_zero_index] + '1' + binary_value_str[last_zero_index + 1:]
        else:  # 解决2147483648转为二进制的问题
            for i in range(MACHINE_WORD_LENGTH - 1):  # 按位取反
                if binary_value_str[i] == '0':
                    binary_value_str = binary_value_str[:i] + '1' + binary_value_str[i + 1:]
                else:
                    binary_value_str = binary_value_str[:i] + '0' + binary_value_str[i + 1:]
        for i in range(last_zero_index + 1, MACHINE_WORD_LENGTH-1):
            binary_value_str = binary_value_str[:i] + '0' + binary_value_str[i + 1:]
        binary_value_str = '1' + binary_value_str
    else:  # 正数
        binary_value_str = str(bin(value))[2:]
        if len(binary_value_str) < MACHINE_WORD_LENGTH - 1:
            for i in range(MACHINE_WORD_LENGTH - 1 - len(binary_value_str)):
                binary_value_str = '0' + binary_value_str
        binary_value_str = '0' + binary_value_str
    return binary_value_str


# print('')
# print('最小负数-2147483648补码对应的真值', twos_complement_to_value('10000000000000000000000000000000'))
# print('最大正数2147483647补码对应的真值', twos_complement_to_value('01111111111111111111111111111111'))
# print('0的补码对应的真值', twos_complement_to_value('00000000000000000000000000000000'))
# print('最小负数-2147483648的补码', value_to_twos_complement(-2147483648))
# print('最大正数2147483647的补码', value_to_twos_complement(2147483647))
# print('0的补码', value_to_twos_complement(0))
instruction = "SW R5, 380(R16)"
op = instruction.split(' ')[0]
rt_index = int(instruction[3:].replace(" ", "").split(',')[0][1:])
comma_index = int(instruction[3:].replace(" ", "").index(','))
left_parenthesis_index = int(instruction[3:].replace(" ", "").index('('))
offset = int(instruction[3:].replace(" ", "")[comma_index + 1:left_parenthesis_index])
base = int(instruction[3:].replace(" ", "")[left_parenthesis_index + 2:-1])
print(op,rt_index, offset, base)


def shift(mode, shamt, input_value):  # 移位函数
    binary_str = value_to_twos_complement(input_value)
    if mode == 'SLL':  # 逻辑左移
        binary_str = binary_str[shamt:]
        for i in range(shamt):
            binary_str = binary_str + '0'
        return twos_complement_to_value(binary_str)

    elif mode == 'SRL':  # 逻辑右移
        binary_str = binary_str[:-shamt]
        for i in range(shamt):
            binary_str = '0' + binary_str
        return twos_complement_to_value(binary_str)

    elif mode == 'SRA':  # 算术右移
        sign = binary_str[0]
        binary_str = binary_str[:-shamt]
        for i in range(shamt):
            binary_str = sign + binary_str
        return twos_complement_to_value(binary_str)


print(value_to_twos_complement(0))
print(value_to_twos_complement(1))
print(0 & 1)