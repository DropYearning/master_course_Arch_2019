# -*- coding: utf-8 -*-
# @Time    : 2019/11/16 7:13 下午
# @Author  : Zhou Liang
# @File    : test.py
# @Software: PyCharm

MIPS_STATUS = {
    'CycleNumber': 0,  # 当前执行指令的周期数
    'PC': 256,  # 程序计数器
    'Registers': [0] * 32,  # 32个MIPS寄存器
    'Data': {},  # 模拟的存储器空间
    'END': False,  # 标志程序是否运行结束
    # 下面两个变量用于在simulation中输出IF Unit的状态(只有分支指令会进入下面两个buffer)
    "IF_Stall": False,  # IF功能单元是否stall
    "IF_Waiting": "",  # 使IF单元stall的分支指令
    "IF_Executed": "",
    # 下面是一些流水线buffer, 为保证冒号后不多空格，存储的指令格式为" [instruction]"
    'Pre_Issue': [],  # 4 entry at most
    'Pre_ALU1': [],  # 2 entry at most
    'Pre_ALU2': [],  # 2 entry at most
    'Pre_MEM': "",  # 1 entry
    'Post_ALU2': "",  # 1 entry
    'Post_MEM': "",  # 1 entry
    # 下面是一些用在MEM和WB单元的buffer
    'Pre_MEM_target_address': None,  # LS类指令的目标地址
    'Pre_MEM_value': None,  # Store指令需要写的值
    'Post_MEM_value': None,  # Load指令需要写入的值
    'Post_ALU2_value': None,  # 非LS类指令的结果值
}

# # 计分卡数据结构
# SCOREBOARD_STATUS = {
#     'Regs_Result_Status': [''] * 32,  # 寄存器结果表(哪一条指令将写这个寄存器)
#     'Regs_Operand_Status': [''] * 32,  # 寄存器操作数表(哪一条指令将读这个寄存器)
# }
#
# instruction = "OR R51, R32, R43"
# rd_index = int(instruction[3:].replace(" ", "").split(',')[0][1:])
# rs_index = int(instruction[3:].replace(" ", "").split(',')[1][1:])
# rt_index = int(instruction[3:].replace(" ", "").split(',')[2][1:])
#
# print(rd_index, rs_index, rt_index)

l = [1,2,3,4]
l[2] = None
print(l)