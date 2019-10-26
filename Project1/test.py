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

v = 'SLL R16, R11, #31'
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

a = 8
print(a << 32)


