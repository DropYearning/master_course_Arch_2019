# -*- coding: utf-8 -*-
# @Time    : 2019/10/25 10:39 上午
# @Author  : Zhou Liang
# @File    : test.py
# @Software: PyCharm


START_ADDRESS = 256  # 起始地址
instruction_sequence = {}  # 指令序列
memory_space = {}  # 模拟存储器（存放data）


def disassembler(input_file_name):  # 反汇编器，将机器码还原为指令序列，并写入存储器内容
    input_file = open(input_file_name)
    input_line = input_file.readline()
    while input_line != '':  # 指令段到BREAK结束
        print(input_line[0:32])

        input_line = input_file.readline()


disassembler('sample.txt')