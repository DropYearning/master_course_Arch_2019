# -*- coding: utf-8 -*-
# @Time    : 2019/10/24 9:42 下午
# @Author  : Zhou Liang
# @File    : MIPSim.py
# @Software: PyCharm

START_ADDRESS = 256  # 起始地址
instruction_sequence = {}  # 指令序列
memory_space = {}  # 模拟存储器（存放data）


def left_shift(input_str, shamt):  # 二进制左移
    output_str = input_str[shamt:]
    for i in range(shamt):
        output_str = output_str + '0'
    return output_str


def disassembler(input_file_name, start_address):  # 反汇编器，将机器码还原为指令序列，并写入存储器内容
    current_address = start_address
    input_file = open(input_file_name)
    input_line = input_file.readline()
    while input_line:  # 指令段到BREAK结束
        print(input_line[0:32], end='\t')
        if input_line[0:2] == '01':  # Category-1
            if input_line[2:6] == '0000':  # J target
                print(current_address, end='\t')
                instruction = 'J #' + str(int(input_line[6:32]+'00', 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0001':  # JR rs
                print(current_address, end='\t')
                instruction = 'JR ' + 'R' + str(int(input_line[6:11], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0010':  # BEQ rs, rt, offset
                print(current_address, end='\t')
                instruction = 'BEQ '
                sign_extend_offset = input_line[16:32] + '00'  # 18bits
                if sign_extend_offset[0] == '0':  # 符号位为0，offset为正
                    decimal_sign_extend_offset = int(sign_extend_offset, 2)
                elif sign_extend_offset[0] == '1':  # 符号位为1，offset为负
                    pass
                instruction = instruction + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(decimal_sign_extend_offset)
                print(instruction, end='\t')
            elif input_line[2:6] == '0011':  # BLTZ
                print(current_address, end='\t')
                instruction = 'BLTZ '
                print(instruction, end='\t')
            elif input_line[2:6] == '0100':  # BGTZ
                print(current_address, end='\t')
                instruction = 'BGTZ '
                print(instruction, end='\t')
            elif input_line[2:6] == '0101':  # BREAK
                print(current_address, end='\t')
                instruction = 'BREAK'
                print(instruction, end='\t')
            elif input_line[2:6] == '0110':  # SW
                print(current_address, end='\t')
                instruction = 'SW '
                print(instruction, end='\t')
            elif input_line[2:6] == '0111':  # LW
                print(current_address, end='\t')
                instruction = 'LW '
                print(instruction, end='\t')
            elif input_line[2:6] == '1000':  # SLL
                print(current_address, end='\t')
                instruction = 'SLL '
                print(instruction, end='\t')
            elif input_line[2:6] == '1001':  # SRL
                print(current_address, end='\t')
                instruction = 'SRL '
                print(instruction, end='\t')
            elif input_line[2:6] == '1010':  # SRA
                print(current_address, end='\t')
                instruction = 'SRA '
                print(instruction, end='\t')
            elif input_line[2:6] == '1011':   # NOP（No Operation）
                print(current_address, end='\t')
                instruction = 'NOP'
                print(instruction, end='\t')
            print("Category-1")
        elif input_line[0:2] == '11':  # Category-2
            if input_line[2:6] == '0000':  # ADD
                print(current_address, end='\t')
                instruction = 'ADD ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0001':  # SUB
                print(current_address, end='\t')
                instruction = 'SUB ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0010':  # MUL
                print(current_address, end='\t')
                instruction = 'MUL ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0011':  # AND
                print(current_address, end='\t')
                instruction = 'AND ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0100':  # OR
                print(current_address, end='\t')
                instruction = 'OR ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0101':  # XOR
                print(current_address, end='\t')
                instruction = 'XOR ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0110':  # NOR
                print(current_address, end='\t')
                instruction = 'NOR ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '0111':  # SLT
                print(current_address, end='\t')
                instruction = 'SLT ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '1000':  # ADDI
                print(current_address, end='\t')
                instruction = 'ADDI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '1001':  # ANDI
                print(current_address, end='\t')
                instruction = 'ANDI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '1010':  # ORI
                print(current_address, end='\t')
                instruction = 'ORI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
                print(instruction, end='\t')
            elif input_line[2:6] == '1011':  # XORI
                print(current_address, end='\t')
                instruction = 'XORI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
                print(instruction, end='\t')
            print("Category-2")
        if input_line[0:32] == '01010100000000000000000000001101':
            break
        current_address = current_address + 4
        input_line = input_file.readline()


disassembler('sample.txt', START_ADDRESS)