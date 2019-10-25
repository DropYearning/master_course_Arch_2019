# -*- coding: utf-8 -*-
# @Time    : 2019/10/24 9:42 下午
# @Author  : Zhou Liang
# @File    : MIPSim.py
# @Software: PyCharm

START_ADDRESS = 256  # 起始地址
instruction_sequence = {}  # 指令序列
memory_space = {}  # 模拟存储器（存放data）


def disassembler(input_file_name, start_address):  # 反汇编器，将机器码还原为指令序列，并写入存储器内容
    current_address = start_address
    input_file = open(input_file_name)
    input_line = input_file.readline()
    while input_line:  # 指令段到BREAK结束
        print(input_line[0:32], end='\t')
        if input_line[0:2] == '01':  # Category-1
            if input_line[2:6] == '0000':
                print(current_address, end='\t')
                instruction = 'J '
                print(instruction, end='\t')
            elif input_line[2:6] == '0001':
                print(current_address, end='\t')
                instruction = 'JR '
                print(instruction, end='\t')
            elif input_line[2:6] == '0010':
                print(current_address, end='\t')
                instruction = 'BEQ '
                print(instruction, end='\t')
            elif input_line[2:6] == '0011':
                print(current_address, end='\t')
                instruction = 'BLTZ '
                print(instruction, end='\t')
            elif input_line[2:6] == '0100':
                print(current_address, end='\t')
                instruction = 'BGTZ '
                print(instruction, end='\t')
            elif input_line[2:6] == '0101':
                print(current_address, end='\t')
                instruction = 'BREAK'
                print(instruction, end='\t')
            elif input_line[2:6] == '0110':
                print(current_address, end='\t')
                instruction = 'SW '
                print(instruction, end='\t')
            elif input_line[2:6] == '0111':
                print(current_address, end='\t')
                instruction = 'LW '
                print(instruction, end='\t')
            elif input_line[2:6] == '1000':
                print(current_address, end='\t')
                instruction = 'SLL '
                print(instruction, end='\t')
            elif input_line[2:6] == '1001':
                print(current_address, end='\t')
                instruction = 'SRL '
                print(instruction, end='\t')
            elif input_line[2:6] == '1010':
                print(current_address, end='\t')
                instruction = 'SRA '
                print(instruction, end='\t')
            elif input_line[2:6] == '1011':
                print(current_address, end='\t')
                instruction = 'NOP '
                print(instruction, end='\t')
            print("Category-1")
        elif input_line[0:2] == '11':  # Category-2
            if input_line[2:6] == '0000':
                print(current_address, end='\t')
                instruction = 'ADD '
                print(instruction, end='\t')
            elif input_line[2:6] == '0001':
                print(current_address, end='\t')
                instruction = 'SUB '
                print(instruction, end='\t')
            elif input_line[2:6] == '0010':
                print(current_address, end='\t')
                instruction = 'MUL '
                print(instruction, end='\t')
            elif input_line[2:6] == '0011':
                print(current_address, end='\t')
                instruction = 'AND '
                print(instruction, end='\t')
            elif input_line[2:6] == '0100':
                print(current_address, end='\t')
                instruction = 'OR '
                print(instruction, end='\t')
            elif input_line[2:6] == '0101':
                print(current_address, end='\t')
                instruction = 'XOR '
                print(instruction, end='\t')
            elif input_line[2:6] == '0110':
                print(current_address, end='\t')
                instruction = 'NOR '
                print(instruction, end='\t')
            elif input_line[2:6] == '0111':
                print(current_address, end='\t')
                instruction = 'SLT '
                print(instruction, end='\t')
            elif input_line[2:6] == '1000':
                print(current_address, end='\t')
                instruction = 'ADDI '
                print(instruction, end='\t')
            elif input_line[2:6] == '1001':
                print(current_address, end='\t')
                instruction = 'ANDI '
                print(instruction, end='\t')
            elif input_line[2:6] == '1010':
                print(current_address, end='\t')
                instruction = 'ORI '
                print(instruction, end='\t')
            elif input_line[2:6] == '1011':
                print(current_address, end='\t')
                instruction = 'XORI '
                print(instruction, end='\t')
            print("Category-2")
        if input_line[0:32] == '01010100000000000000000000001101':
            break
        current_address = current_address + 4
        input_line = input_file.readline()


disassembler('sample.txt', START_ADDRESS)