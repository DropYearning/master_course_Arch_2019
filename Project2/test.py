# -*- coding: utf-8 -*-
# @Time    : 2019/11/16 7:13 下午
# @Author  : Zhou Liang
# @File    : test.py
# @Software: PyCharm

MIPS_STATUS = {
    'CycleNumber': 0,  # 当前执行指令的周期数
    'PC': START_ADDRESS,  # 程序计数器
    'Registers': [0] * 32,  # 32个MIPS寄存器
    'Data': {},  # 模拟的存储器空间
    'END': False,  # 标志程序是否运行结束
    # 下面两个变量用于在simulation中输出IF Unit的状态
    "IF_Waiting": "",  #
    "IF_Executed": "",  #
    # 下面是一些流水线buffer
    'Pre_Issue': [''] * 4,  # 4 entry
    'Pre_ALU1': [''] * 2,  # 2 entry
    'Pre_ALU2': [''] * 2,  # 2 entry
    'Pre_MEM': "",  # 1 entry
    'Post_ALU2': "",  # 1 entry
    'Post_MEM': "",  # 1 entry
}


l = ['']
l.append('123')
print(l[1])