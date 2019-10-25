# -*- coding: utf-8 -*-
# @Time    : 2019/10/24 9:42 下午
# @Author  : Zhou Liang
# @File    : MIPSim.py
# @Software: PyCharm

START_ADDRESS = 256  # 起始地址
INSTRUCTION_SEQUENCE = {}  # 指令序列
INSTRUCTION_COUNT = 0  # 指令条数
memory_space = {}  # 模拟存储器（存放data）


def disassembler_instruction(input_file_name, output_file_name, start_address):  # 反汇编器（第一部分），将机器码还原为指令序列， 并写入文件disassembly.txt
    instruction_count = 0
    instruction_sequence = {}
    current_address = start_address
    input_file = open(input_file_name)
    output_file = open(output_file_name, 'w')
    input_line = input_file.readline()
    while input_line:  # 指令段到BREAK结束
        # print(input_line[0:32], end='\t')
        if input_line[0:2] == '01':  # Category-1
            if input_line[2:6] == '0000':  # J target
                instruction = 'J #' + str(int(input_line[6:32]+'00', 2))
            elif input_line[2:6] == '0001':  # JR rs
                instruction = 'JR ' + 'R' + str(int(input_line[6:11], 2))
            elif input_line[2:6] == '0010':  # BEQ rs, rt, offset
                sign_extend_offset = input_line[16:32] + '00'  # 18bits
                if sign_extend_offset[0] == '0':  # 符号位为0，offset为正
                    target_offset = int(sign_extend_offset, 2)
                elif sign_extend_offset[0] == '1':  # 符号位为1，offset为负
                    pass  # TODO
                instruction = 'BEQ ' + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(target_offset)
            elif input_line[2:6] == '0011':  # BLTZ rs, offset
                sign_extend_offset = input_line[16:32] + '00'  # 18bits
                if sign_extend_offset[0] == '0':  # 符号位为0，offset为正
                    target_offset = int(sign_extend_offset, 2)
                elif sign_extend_offset[0] == '1':  # 符号位为1，offset为负
                    pass
                instruction = 'BLTZ ' + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(target_offset)
            elif input_line[2:6] == '0100':  # BGTZ rs, offset
                sign_extend_offset = input_line[16:32] + '00'  # 18bits
                if sign_extend_offset[0] == '0':  # 符号位为0，offset为正
                    target_offset = int(sign_extend_offset, 2)
                elif sign_extend_offset[0] == '1':  # 符号位为1，offset为负
                    pass
                instruction = 'BGTZ ' + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(target_offset)
            elif input_line[2:6] == '0101':  # BREAK
                instruction = 'BREAK'
            elif input_line[2:6] == '0110':  # SW rt, offset(base)
                if input_line[16] == '0': # 符号位为0，offset为正
                    decimal_offset = int(input_line[16:32], 2)
                elif input_line[16] == '1': # 符号位为1，offset为负
                    pass
                instruction = 'SW ' + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + str(decimal_offset) + "(R" + str(int(input_line[6:11], 2)) + ')'
            elif input_line[2:6] == '0111':  # LW rt, offset(base)
                if input_line[16] == '0': # 符号位为0，offset为正
                    decimal_offset = int(input_line[16:32], 2)
                elif input_line[16] == '1': # 符号位为1，offset为负
                    pass
                instruction = 'LW ' + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + str(decimal_offset) + "(R" + str(int(input_line[6:11], 2)) + ')'
            elif input_line[2:6] == '1000':  # SLL rd, rt, sa
                instruction = 'SLL ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(int(input_line[21:26], 2))
            elif input_line[2:6] == '1001':  # SRL rd, rt, sa
                instruction = 'SRL ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(int(input_line[21:26], 2))
            elif input_line[2:6] == '1010':  # SRA rd, rt, sa (Shift Word Right Arithmetic)
                instruction = 'SRA ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(int(input_line[21:26], 2))
            elif input_line[2:6] == '1011':   # NOP（No Operation）
                instruction = 'NOP'
        elif input_line[0:2] == '11':  # Category-2
            if input_line[2:6] == '0000':  # ADD
                instruction = 'ADD ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '0001':  # SUB
                instruction = 'SUB ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '0010':  # MUL
                instruction = 'MUL ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '0011':  # AND
                instruction = 'AND ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '0100':  # OR
                instruction = 'OR ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '0101':  # XOR
                instruction = 'XOR ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '0110':  # NOR
                instruction = 'NOR ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '0111':  # SLT
                instruction = 'SLT ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))
            elif input_line[2:6] == '1000':  # ADDI
                instruction = 'ADDI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
            elif input_line[2:6] == '1001':  # ANDI
                instruction = 'ANDI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
            elif input_line[2:6] == '1010':  # ORI
                instruction = 'ORI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
            elif input_line[2:6] == '1011':  # XORI
                instruction = 'XORI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(int(input_line[16:32], 2))
        print(input_line[0:32] + '\t' + str(current_address) + '\t' + instruction)
        output_file.write(input_line[0:32] + '\t' + str(current_address) + '\t' + instruction + '\n')
        instruction_count = instruction_count + 1
        instruction_sequence[current_address] = instruction
        current_address = current_address + 4
        if instruction == 'BREAK':
            break
        input_line = input_file.readline()
    output_file.close()
    return instruction_count, instruction_sequence


def disassembler_memory(input_file_name, start_address):  # 反汇编器(第二部分)，将指令序列后的补码序列写入到存储空间（data），并写入文件disassembly.txt
    pass


INSTRUCTION_COUNT, INSTRUCTION_SEQUENCE = disassembler_instruction('sample.txt', 'disassembly.txt',START_ADDRESS)

