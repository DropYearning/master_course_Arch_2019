# -*- coding: utf-8 -*-
# @Time    : 2019/11/16 5:42 下午
# @Author  : Zhou Liang
# @File    : MIPSsim2.py.py
# @Software: PyCharm

# On my honor, I have neither given nor received unauthorized aid on this assignment.

import sys

START_ADDRESS = 256  # 起始地址
INSTRUCTION_SEQUENCE = {}  # 指令序列
INSTRUCTION_COUNT = 0  # 指令条数
MACHINE_WORD_LENGTH = 32  # 机器字长
MIPS_STATUS = {
    'CycleNumber': 0,  # 当前执行指令的周期数
    'PC': START_ADDRESS,  # 程序计数器
    'Registers': [0] * 32,  # 32个MIPS寄存器
    'Data': {},  # 模拟的存储器空间
    'END': False,  # 标志程序是否运行结束
    # 下面两个变量用于在simulation中输出IF Unit的状态
    "IF_Waiting": "",  #
    "IF_Executed": "",  #
    # 下面是一些流水线buffer, 为保证冒号后不多空格，存储的指令格式为" [instruction]"
    'Pre_Issue': [''] * 4,  # 4 entry
    'Pre_ALU1': [''] * 2,  # 2 entry
    'Pre_ALU2': [''] * 2,  # 2 entry
    'Pre_MEM': "",  # 1 entry
    'Post_ALU2': "",  # 1 entry
    'Post_MEM': "",  # 1 entry
}



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
        if len(binary_value_str) < MACHINE_WORD_LENGTH - 1:
            for i in range(MACHINE_WORD_LENGTH - 1 - len(binary_value_str)):
                binary_value_str = '0' + binary_value_str
        elif len(binary_value_str) == MACHINE_WORD_LENGTH:  # 解决2147483648转为二进制的问题
            binary_value_str = binary_value_str[1:]
        for i in range(MACHINE_WORD_LENGTH - 1):  # 按位取反
            if binary_value_str[i] == '0':
                binary_value_str = binary_value_str[:i] + '1' + binary_value_str[i + 1:]
            else:
                binary_value_str = binary_value_str[:i] + '0' + binary_value_str[i + 1:]
        last_zero_index = binary_value_str.rfind('0')  # 加一
        if last_zero_index != -1:
            binary_value_str = binary_value_str[:last_zero_index] + '1' + binary_value_str[last_zero_index + 1:]
        else:  # 解决2147483648转为二进制的问题
            for i in range(MACHINE_WORD_LENGTH - 1):  # 按位取反
                if binary_value_str[i] == '0':
                    binary_value_str = binary_value_str[:i] + '1' + binary_value_str[i + 1:]
                else:
                    binary_value_str = binary_value_str[:i] + '0' + binary_value_str[i + 1:]
        for i in range(last_zero_index + 1, MACHINE_WORD_LENGTH - 1):
            binary_value_str = binary_value_str[:i] + '0' + binary_value_str[i + 1:]
        binary_value_str = '1' + binary_value_str
    else:  # 正数
        binary_value_str = str(bin(value))[2:]
        if len(binary_value_str) < MACHINE_WORD_LENGTH - 1:
            for i in range(MACHINE_WORD_LENGTH - 1 - len(binary_value_str)):
                binary_value_str = '0' + binary_value_str
        binary_value_str = '0' + binary_value_str
    return binary_value_str


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


def disassembler_instruction(input_file_name, output_file_name,
                             start_address):  # 反汇编器（第一部分），将机器码还原为指令序列， 并写入文件disassembly.txt
    instruction_count = 0
    instruction_sequence = {}
    current_address = start_address
    input_file_pointer = open(input_file_name)
    output_file_pointer = open(output_file_name, 'w')
    input_line = input_file_pointer.readline()
    while input_line:  # 指令段到BREAK结束
        # print(input_line[0:32], end='\t')
        if input_line[0:2] == '01':  # Category-1
            if input_line[2:6] == '0000':  # J target
                instruction = 'J #' + str(int(input_line[6:32] + '00', 2))

            elif input_line[2:6] == '0001':  # JR rs
                instruction = 'JR ' + 'R' + str(int(input_line[6:11], 2))

            elif input_line[2:6] == '0010':  # BEQ rs, rt, offset
                sign_extend_offset = input_line[16:32] + '00'  # 18bits sign_extend_offset
                if sign_extend_offset[0] == '0':  # 符号位为0，offset为正
                    target_offset = int(sign_extend_offset, 2)
                elif sign_extend_offset[0] == '1':  # 符号位为1，offset为负
                    target_offset = twos_complement_to_value(sign_extend_offset)
                instruction = 'BEQ ' + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(target_offset)

            elif input_line[2:6] == '0011':  # BLTZ rs, offset
                sign_extend_offset = input_line[16:32] + '00'  # 18bits sign_extend_offset
                if sign_extend_offset[0] == '0':  # 符号位为0，offset为正
                    target_offset = int(sign_extend_offset, 2)
                elif sign_extend_offset[0] == '1':  # 符号位为1，offset为负
                    target_offset = twos_complement_to_value(sign_extend_offset)
                instruction = 'BLTZ ' + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(target_offset)

            elif input_line[2:6] == '0100':  # BGTZ rs, offset
                sign_extend_offset = input_line[16:32] + '00'  # 18bits sign_extend_offset
                if sign_extend_offset[0] == '0':  # 符号位为0，offset为正
                    target_offset = int(sign_extend_offset, 2)
                elif sign_extend_offset[0] == '1':  # 符号位为1，offset为负
                    target_offset = twos_complement_to_value(sign_extend_offset)
                instruction = 'BGTZ ' + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(target_offset)

            elif input_line[2:6] == '0101':  # BREAK
                instruction = 'BREAK'

            elif input_line[2:6] == '0110':  # SW rt, offset(base)
                if input_line[16] == '0':  # 符号位为0，offset为正
                    decimal_offset = int(input_line[16:32], 2)
                elif input_line[16] == '1':  # 符号位为1，offset为负
                    decimal_offset = twos_complement_to_value(input_line[16:32])
                instruction = 'SW ' + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + str(decimal_offset) + "(R" + str(int(input_line[6:11], 2)) + ')'

            elif input_line[2:6] == '0111':  # LW rt, offset(base)
                if input_line[16] == '0':  # 符号位为0，offset为正
                    decimal_offset = int(input_line[16:32], 2)
                elif input_line[16] == '1':  # 符号位为1，offset为负
                    decimal_offset = twos_complement_to_value(input_line[16:32])
                instruction = 'LW ' + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + str(decimal_offset) + "(R" + str(int(input_line[6:11], 2)) + ')'

            elif input_line[2:6] == '1000':  # SLL rd, rt, sa [Shift Word Left Logical]
                instruction = 'SLL ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(int(input_line[21:26], 2))

            elif input_line[2:6] == '1001':  # SRL rd, rt, sa [Shift Word Right Logical]
                instruction = 'SRL ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(int(input_line[21:26], 2))

            elif input_line[2:6] == '1010':  # SRA rd, rt, sa [Shift Word Right Arithmetic]
                instruction = 'SRA ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2)) + ", " \
                              + '#' + str(int(input_line[21:26], 2))

            elif input_line[2:6] == '1011':  # NOP（No Operation）
                instruction = 'NOP'

        elif input_line[0:2] == '11':  # Category-2
            if input_line[2:6] == '0000':  # ADD rd, rs, rt
                instruction = 'ADD ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))

            elif input_line[2:6] == '0001':  # SUB
                instruction = 'SUB ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))

            elif input_line[2:6] == '0010':  # MUL rd, rs, rt [rd ← rs × rt]
                instruction = 'MUL ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))

            elif input_line[2:6] == '0011':  # AND rd, rs, rt
                instruction = 'AND ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))

            elif input_line[2:6] == '0100':  # OR rd, rs, rt
                instruction = 'OR ' + 'R' + str(int(input_line[16:21], 2)) + ", " \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + 'R' + str(int(input_line[11:16], 2))

            elif input_line[2:6] == '0101':  # XOR rd, rs, rt
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

            elif input_line[2:6] == '1000':  # ADDI rt, rs, immediate
                decimal_imm = int(input_line[16:32], 2) if input_line[16] == '0' else twos_complement_to_value(
                    input_line[16:32])
                instruction = 'ADDI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(decimal_imm)

            elif input_line[2:6] == '1001':  # ANDI rt, rs, immediate
                decimal_imm = int(input_line[16:32], 2) if input_line[16] == '0' else twos_complement_to_value(
                    input_line[16:32])
                instruction = 'ANDI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(decimal_imm)

            elif input_line[2:6] == '1010':  # ORI rt, rs, immediate
                decimal_imm = int(input_line[16:32], 2) if input_line[16] == '0' else twos_complement_to_value(
                    input_line[16:32])
                instruction = 'ORI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(decimal_imm)

            elif input_line[2:6] == '1011':  # XORI rt, rs, immediate
                decimal_imm = int(input_line[16:32], 2) if input_line[16] == '0' else twos_complement_to_value(
                    input_line[16:32])
                instruction = 'XORI ' + 'R' + str(int(input_line[11:16], 2)) + ', ' \
                              + 'R' + str(int(input_line[6:11], 2)) + ", " \
                              + '#' + str(decimal_imm)

        # print(input_line[0:32] + '\t' + str(current_address) + '\t' + instruction)
        output_file_pointer.write(input_line[0:32] + '\t' + str(current_address) + '\t' + instruction + '\n')
        instruction_count = instruction_count + 1
        instruction_sequence[current_address] = instruction
        current_address = current_address + 4
        if instruction == 'BREAK':
            break
        input_line = input_file_pointer.readline()
    output_file_pointer.close()
    input_file_pointer.close()
    return instruction_count, instruction_sequence


def disassembler_memory(input_file_name, output_file_name,
                        instruction_count):  # 反汇编器(第二部分)，将指令序列后的补码序列写入到存储空间（data），并写入文件disassembly.txt
    memory_space = {}
    input_file_pointer = open(input_file_name)
    output_file_pointer = open(output_file_name, 'a')
    current_address = START_ADDRESS + instruction_count * 4
    input_lines = input_file_pointer.readlines()[instruction_count:]
    for line in input_lines:
        line_value = twos_complement_to_value(line)
        # print(line[0:32] + '\t' + str(current_address) + '\t' + str(line_value))
        output_file_pointer.write(line[0:32] + '\t' + str(current_address) + '\t' + str(line_value) + '\n')
        memory_space[current_address] = line_value
        current_address = current_address + 4
    output_file_pointer.close()
    input_file_pointer.close()
    return memory_space


def print_reg(mips_status, output_file_pointer):  # 输出所有寄存器的值
    # print("Registers")
    output_file_pointer.write("Registers" + '\n')
    for i in range(32):  # 打印32个寄存器状态
        if i % 8 == 0:
            if i < 9:
                # print('R0' + str(i) + ':\t' + str(mips_status['Registers'][i]), end='\t')
                output_file_pointer.write('R0' + str(i) + ':\t' + str(mips_status['Registers'][i]) + '\t')
            else:
                # print('R' + str(i) + ':\t' + str(mips_status['Registers'][i]), end='\t')
                output_file_pointer.write('R' + str(i) + ':\t' + str(mips_status['Registers'][i]) + '\t')
        elif i % 8 == 7:
            # print(str(mips_status['Registers'][i]))
            output_file_pointer.write(str(mips_status['Registers'][i]) + '\n')
        else:
            # print(str(mips_status['Registers'][i]), end='\t')
            output_file_pointer.write(str(mips_status['Registers'][i]) + '\t')
    # print("")
    output_file_pointer.write('\n')


def print_memory(mips_status, output_file_pointer):  # 输出存储器内容
    # print("Data")
    output_file_pointer.write("Data" + '\n')
    word_number = len(mips_status['Data'])  # 存储器中的字数
    data_start_address = sorted(mips_status['Data'])[0]
    for i in range(word_number):  # 打印存储器状态
        current_address = data_start_address + i * 4
        if i % 8 == 0:
            # print(str(current_address) + ":" + '\t' + str(mips_status['Data'][current_address]), end='\t')
            output_file_pointer.write(str(current_address) + ":" + '\t' + str(mips_status['Data'][current_address]) + '\t')
        elif i % 8 == 7:
            # print(str(mips_status['Data'][current_address]))
            output_file_pointer.write(str(mips_status['Data'][current_address]) + '\n')
        else:
            # print(str(mips_status['Data'][current_address]), end='\t')
            output_file_pointer.write(str(mips_status['Data'][current_address]) + '\t')


def print_cycle_status(mips_status, output_file_name):  # 输出每个周期的模拟结果
    output_file_pointer = open(output_file_name, 'a')
    # print('--------------------')
    output_file_pointer.write("--------------------" + '\n')
    # print("Cycle:" + str(mips_status['CycleNumber']))
    output_file_pointer.write("Cycle:" + str(mips_status['CycleNumber']) + '\n')
    # print("")
    output_file_pointer.write('\n')
    # print("IF Unit:")
    output_file_pointer.write("IF Unit:" + '\n')
    # print("\t" + "Waiting Instruction: " + mips_status['IF_Waiting'])
    output_file_pointer.write("\t" + "Waiting Instruction: " + mips_status['IF_Waiting'] + '\n')
    # print("\t" + "Executed Instruction: " + mips_status['IF_Executed'])
    output_file_pointer.write("\t" + "Executed Instruction: " + mips_status['IF_Executed'] + '\n')
    # print("Pre-Issue Queue:")
    output_file_pointer.write("Pre-Issue Queue:"+ '\n')
    # print("\t" + "Entry 0:" + mips_status['Pre_Issue'][0])
    output_file_pointer.write("\t" + "Entry 0:" + mips_status['Pre_Issue'][0] + '\n')
    # print("\t" + "Entry 1:" + mips_status['Pre_Issue'][1])
    output_file_pointer.write("\t" + "Entry 1:" + mips_status['Pre_Issue'][1] + '\n')
    # print("\t" + "Entry 2:" + mips_status['Pre_Issue'][2])
    output_file_pointer.write("\t" + "Entry 2:" + mips_status['Pre_Issue'][2] + '\n')
    # print("\t" + "Entry 3:" + mips_status['Pre_Issue'][3])
    output_file_pointer.write("\t" + "Entry 3:" + mips_status['Pre_Issue'][3] + '\n')
    # print("Pre-ALU1 Queue:")
    output_file_pointer.write("Pre-ALU1 Queue:" + '\n')
    # print("\t" + "Entry 0:" + mips_status['Pre_ALU1'][0])
    output_file_pointer.write("\t" + "Entry 0:" + mips_status['Pre_ALU1'][0] + '\n')
    # print("\t" + "Entry 1:" + mips_status['Pre_ALU1'][1])
    output_file_pointer.write("\t" + "Entry 1:" + mips_status['Pre_ALU1'][1] + '\n')
    # print("Pre-MEM Queue:" + mips_status['Pre_MEM'])
    output_file_pointer.write("Pre-MEM Queue:" + mips_status['Pre_MEM'] + '\n')
    # print("Post-MEM Queue:" + mips_status['Post_MEM'])
    output_file_pointer.write("Post-MEM Queue:" + mips_status['Post_MEM'] + '\n')
    # print("Pre-ALU2 Queue:")
    output_file_pointer.write("Pre-ALU2 Queue:" + '\n')
    # print("\t" + "Entry 0:" + mips_status['Pre_ALU2'][0])
    output_file_pointer.write("\t" + "Entry 0:" + mips_status['Pre_ALU2'][0] + '\n')
    # print("\t" + "Entry 1:" + mips_status['Pre_ALU2'][1])
    output_file_pointer.write("\t" + "Entry 1:" + mips_status['Pre_ALU2'][1] + '\n')
    # print("Post-ALU2 Queue:" + mips_status['Post_ALU2'])
    output_file_pointer.write("Post-ALU2 Queue:" + mips_status['Post_ALU2'] + '\n')
    # print('')
    output_file_pointer.write('\n')
    print_reg(mips_status, output_file_pointer)
    print_memory(mips_status, output_file_pointer)


if __name__ == '__main__':
    # 默认sys.argv[1]为输入的文件名
    # INSTRUCTION_COUNT, INSTRUCTION_SEQUENCE = disassembler_instruction(sys.argv[1], 'disassembly.txt', START_ADDRESS)
    # MIPS_STATUS['Data'] = disassembler_memory(sys.argv[1], 'disassembly.txt', INSTRUCTION_COUNT)

    # 文件名写死
    INSTRUCTION_COUNT, INSTRUCTION_SEQUENCE = disassembler_instruction('sample.txt', 'disassembly.txt', START_ADDRESS)
    print("指令条数：", INSTRUCTION_COUNT)
    print(START_ADDRESS + INSTRUCTION_COUNT * 4)
    MIPS_STATUS['Data'] = disassembler_memory('sample.txt', 'disassembly.txt', INSTRUCTION_COUNT)
    print("指令序列：", INSTRUCTION_SEQUENCE)
    print("存储器：", MIPS_STATUS['Data'])
    # 清空文件simulation.txt
    p = open('simulation.txt', 'w')
    p.truncate()
    p.close()
    print_cycle_status(MIPS_STATUS, 'simulation.txt')