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
    # 下面两个变量用于在simulation中输出IF Unit的状态(只有分支指令会进入下面两个buffer)
    "IF_Stall": False,  # IF功能单元是否stall
    "IF_Waiting": "",  # 使IF单元stall的分支指令
    "IF_Executed": "",
    # 下面是一些流水线buffer, 为保证冒号后不多空格，存储的指令格式为" [instruction]"
    'Pre_Issue': [],  # 4 entry
    'Pre_ALU1': [],  # 2 entry
    'Pre_ALU2': [],  # 2 entry
    'Pre_MEM': "",  # 1 entry
    'Post_ALU2': "",  # 1 entry
    'Post_MEM': "",  # 1 entry
}

# 计分卡数据结构
SCOREBOARD_STATUS = {
    'Regs_Result_Status': [''] * 32,  # 寄存器结果表(哪一条指令将写这个寄存器)
    'Regs_Operand_Status': [''] * 32,  # 寄存器操作数表(哪一条指令将读这个寄存器)
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
    output_file_pointer.write("--------------------" + '\n')
    output_file_pointer.write("Cycle:" + str(mips_status['CycleNumber']) + '\n')
    output_file_pointer.write('\n')
    output_file_pointer.write("IF Unit:" + '\n')
    output_file_pointer.write("\t" + "Waiting Instruction: " + mips_status['IF_Waiting'] + '\n')
    output_file_pointer.write("\t" + "Executed Instruction: " + mips_status['IF_Executed'] + '\n')
    output_file_pointer.write("Pre-Issue Queue:"+ '\n')
    for i in range(4):
        count = len(mips_status['Pre_Issue'])
        if i < count:
            output_file_pointer.write("\t" + "Entry " + str(i) + ":" + mips_status['Pre_Issue'][i] + '\n')
        else:
            output_file_pointer.write("\t" + "Entry " + str(i) + ":" + '\n')
    output_file_pointer.write("Pre-ALU1 Queue:" + '\n')
    for j in range(2):
        count = len(mips_status['Pre_ALU1'])
        if j < count:
            output_file_pointer.write("\t" + "Entry " + str(j) + ":" + mips_status['Pre_ALU1'][j] + '\n')
        else:
            output_file_pointer.write("\t" + "Entry " + str(j) + ":" + '\n')
    output_file_pointer.write("Pre-MEM Queue:" + mips_status['Pre_MEM'] + '\n')
    output_file_pointer.write("Post-MEM Queue:" + mips_status['Post_MEM'] + '\n')
    output_file_pointer.write("Pre-ALU2 Queue:" + '\n')
    for k in range(2):
        count = len(mips_status['Pre_ALU2'])
        if k < count:
            output_file_pointer.write("\t" + "Entry " + str(k) + ":" + mips_status['Pre_ALU2'][k] + '\n')
        else:
            output_file_pointer.write("\t" + "Entry " + str(k) + ":" + '\n')
    output_file_pointer.write("Post-ALU2 Queue:" + mips_status['Post_ALU2'] + '\n')
    output_file_pointer.write('\n')
    print_reg(mips_status, output_file_pointer)
    print_memory(mips_status, output_file_pointer)


def if_instruction_operation(instruction, previous_scoreboard, previous_mips_status):  # 每种指令在IF单元需要进行的操作
    temp_modified_mips_status = previous_mips_status
    op = instruction.split()[0]
    if op == 'BREAK':  # 若提取到的是BREAK指令
        temp_modified_mips_status['IF_Executed'] = ' [BREAK]'  # 立即执行BREAK
        temp_modified_mips_status['IF_Stall'] = True  # 不再提取其他指令
        temp_modified_mips_status['END'] = True
        # BREAK指令不改变PC（改了也没有意义）
    elif op == "NOP":  # 若提取到的是NOP指令
        temp_modified_mips_status['IF_Executed'] = ' [NOP]'  # 立即执行NOP
        # no operation
        temp_modified_mips_status['PC'] = previous_mips_status['PC'] + 4  # PC = PC +4
    elif op == 'J':  # 若提取到的是J指令(一定立即发生跳转)
        target_address = int(instruction.split()[1][1:])
        temp_modified_mips_status['IF_Executed'] = ' [' + instruction + ']'  # 立即执行J
        temp_modified_mips_status['PC'] = target_address  # 修改 PC = target
    elif op == 'JR':  # 若提取到的是JR指令
        rs_index = int(instruction.split()[1][1:])
        if previous_scoreboard['Regs_Result_Status'][rs_index] == '':  # rs准备好
            target_address = previous_mips_status['Registers'][rs_index]
            temp_modified_mips_status['IF_Executed'] = ' [' + instruction + ']'  # JR立即执行
            temp_modified_mips_status['PC'] = target_address  # 修改 PC = target
        else:  # rs没有准备好
            temp_modified_mips_status['IF_Waiting'] = ' [' + instruction + ']'  # JR进入等待状态
            temp_modified_mips_status['IF_Stall'] = True  # 不再提取其他指令
            # 已经暂停取指，PC改变也没有意义
    elif op == 'BEQ':  # 若提取到的是BEQ指令
        rs_index = int(instruction[4:].replace(" ", "").split(',')[0][1:])
        rt_index = int(instruction[4:].replace(" ", "").split(',')[1][1:])
        offset = int(instruction[4:].replace(" ", "").split(',')[2][1:])
        target_address = previous_mips_status['PC'] + offset
        if previous_scoreboard['Regs_Result_Status'][rs_index] == '' and \
                previous_scoreboard['Regs_Result_Status'][rt_index] == '':  # rs和rt准备好
            temp_modified_mips_status['IF_Executed'] = ' [' + instruction + ']'  # BEQ立即执行
            if previous_mips_status['Registers'][rs_index] == previous_mips_status['Registers'][rt_index]:
                # rs == rt 才跳转
                temp_modified_mips_status['PC'] = target_address  # 修改 PC = target
            else:  # 否则PC正常+4
                temp_modified_mips_status['PC'] = previous_mips_status['PC'] + 4  # PC = PC +4
        else:  # rs和rt没准备好
            temp_modified_mips_status['IF_Waiting'] = ' [' + instruction + ']'  # BEQ进入等待状态
            temp_modified_mips_status['IF_Stall'] = True  # 不再提取其他指令
            # 已经暂停取指，PC改变也没有意义
    elif op in ['BLTZ', 'BGTZ']:  # 若提取到的是BGTZ或者BLTZ指令 , BLTZ rs, offset [if rs < 0 then branch]
        rs_index = int(instruction[4:].replace(" ", "").split(',')[0][1:])
        offset = int(instruction[4:].replace(" ", "").split(',')[1][1:])
        target_address = previous_mips_status['PC'] + offset
        if previous_scoreboard['Regs_Result_Status'][rs_index] == '':  # rs准备好
            temp_modified_mips_status['IF_Executed'] = ' [' + instruction + ']'  # BGTZ/BLTZ立即执行
            if op == "BLTZ" and previous_mips_status['Registers'][rs_index] < 0:  # BLTZ操作
                temp_modified_mips_status['PC'] = target_address  # 修改PC
            elif op == "BGTZ" and previous_mips_status['Registers'][rs_index] > 0:  # BGTZ操作
                temp_modified_mips_status['PC'] = target_address  # 修改PC
            else:  # 否则PC正常+4
                temp_modified_mips_status['PC'] = previous_mips_status['PC'] + 4  # PC = PC +4
        else:  # rs没准备好
            temp_modified_mips_status['IF_Waiting'] = ' [' + instruction + ']'  # 指令进入等待状态
            temp_modified_mips_status['IF_Stall'] = True  # 不再提取其他指令
            # 已经暂停取指，PC改变也没有意义
    else:  # 若提取到的是其他指令(SW,LW,运算指令等) 【这些指令会进入Pre-issue中，需要更改pre-issue的空位数】
        # IF单元不检查这些指令的操作数是否准备完毕，只要有空位就进入Pre-issue，最后要更改PC+4
        # pre_issue_count = len(previous_mips_status['Pre_Issue'])
        # 检查空位的操作在前面已经做过，这里直接append
        temp_modified_mips_status['Pre_Issue'].append(' [' + instruction + ']')  # 写入pre-issue
        temp_modified_mips_status['PC'] = previous_mips_status['PC'] + 4  # PC = PC +4
    return temp_modified_mips_status


def if_operation(previous_scoreboard, previous_mips_status):  # IF功能单元在每个周期的操作
    # IF单元承担改变PC的任务
    # stall_sign = previous_mips_status['IF_Stall']  # 在IF单元最后（本周期末）更新IF_Stall
    temp_modified_mips_status = previous_mips_status

    # 若IF单元Stall，本周期不提取任何指令
    if previous_mips_status['IF_Stall']:
        # 检查[Waiting Instruction]中原来不可用的寄存器是否已经可用
        instruction_waiting = previous_mips_status['IF_Waiting'][2:-1]
        op = instruction_waiting.split()[0]
        if op == 'JR':
            rs_index = int(instruction_waiting.split()[1][1:])
            if previous_scoreboard['Regs_Result_Status'][rs_index] == '':  # rs准备好
                target_address = previous_mips_status['Registers'][rs_index]
                temp_modified_mips_status['IF_Waiting'] = ""
                temp_modified_mips_status['IF_Executed'] = ' [' + instruction_waiting + ']'  # JR执行
                temp_modified_mips_status['PC'] = target_address  # 修改 PC = target
                temp_modified_mips_status['IF_Stall'] = False  # 不再提取其他指令
        elif op == 'BEQ':
            rs_index = int(instruction_waiting[4:].replace(" ", "").split(',')[0][1:])
            rt_index = int(instruction_waiting[4:].replace(" ", "").split(',')[1][1:])
            offset = int(instruction_waiting[4:].replace(" ", "").split(',')[2][1:])
            target_address = previous_mips_status['PC'] + offset
            if previous_scoreboard['Regs_Result_Status'][rs_index] == '' and \
                    previous_scoreboard['Regs_Result_Status'][rt_index] == '':  # rs和rt准备好
                temp_modified_mips_status['IF_Waiting'] = ""
                temp_modified_mips_status['IF_Executed'] = ' [' + instruction_waiting + ']'  # BEQ执行
                temp_modified_mips_status['IF_Stall'] = False  # 不再提取其他指令
                if previous_mips_status['Registers'][rs_index] == previous_mips_status['Registers'][rt_index]:
                    # rs == rt 才跳转
                    temp_modified_mips_status['PC'] = target_address  # 修改 PC = target
                else:  # 否则PC正常+4
                    temp_modified_mips_status['PC'] = previous_mips_status['PC'] + 4  # PC = PC +4
        elif op in ['BLTZ', 'BGTZ']:
            rs_index = int(instruction_waiting[4:].replace(" ", "").split(',')[0][1:])
            offset = int(instruction_waiting[4:].replace(" ", "").split(',')[1][1:])
            target_address = previous_mips_status['PC'] + offset
            if previous_scoreboard['Regs_Result_Status'][rs_index] == '':  # rs准备好
                temp_modified_mips_status['IF_Waiting'] = ""
                temp_modified_mips_status['IF_Executed'] = ' [' + instruction_waiting + ']'  # BGTZ/BLTZ执行
                temp_modified_mips_status['IF_Stall'] = False  # 不再提取其他指令
                if op == "BLTZ" and previous_mips_status['Registers'][rs_index] < 0:  # BLTZ操作
                    temp_modified_mips_status['PC'] = target_address  # 修改PC
                elif op == "BGTZ" and previous_mips_status['Registers'][rs_index] > 0:  # BGTZ操作
                    temp_modified_mips_status['PC'] = target_address  # 修改PC
                else:  # 否则PC正常+4
                    temp_modified_mips_status['PC'] = previous_mips_status['PC'] + 4  # PC = PC +4

    # 若Pre-issue没有空位，本周期不提取任何指令
    elif len(previous_mips_status['Pre_Issue']) == 4:
        # If there is no empty slot in the Pre-issue buffer at the end of the last cycle,
        # no instruction can be fetched at the current cycle.
        # 此时PC不变
        pass

    # 若本周期可以提取1条指令
    elif len(previous_mips_status['Pre_Issue']) == 3:
        instruction_fetched = INSTRUCTION_SEQUENCE[previous_mips_status['PC']]
        temp_modified_mips_status = if_instruction_operation(instruction_fetched, previous_scoreboard,
                                                             previous_mips_status, temp_modified_mips_status)

    # 若本周期可以提取2条指令
    elif len(previous_mips_status['Pre_Issue']) <= 2:
        instruction_fetched_1 = INSTRUCTION_SEQUENCE[previous_mips_status['PC']]
        op1 = instruction_fetched_1.split()[0]
        if op1 in ['J', 'JR', 'BEQ', 'BLTZ', 'BGTZ', 'BREAK']:  # 不再取instruction_fetched_2
            temp_modified_mips_status = if_instruction_operation(instruction_fetched_1, previous_scoreboard,
                                                                 previous_mips_status, temp_modified_mips_status)
            return temp_modified_mips_status
        else:
            instruction_fetched_2 = INSTRUCTION_SEQUENCE[previous_mips_status['PC'] + 4]  # 没有分支，所以PC=PC+4
            temp_modified_mips_status = if_instruction_operation(instruction_fetched_1, previous_scoreboard,
                                                                 previous_mips_status, temp_modified_mips_status)
            temp_modified_mips_status = if_instruction_operation(instruction_fetched_2, previous_scoreboard,
                                                                 previous_mips_status, temp_modified_mips_status)
    return temp_modified_mips_status


def issue_operation(previous_scoreboard, modified_scoreboard, previous_mips_status, modified_mips_status):  # Issue功能单元在每个周期的操作
    pass


def alu1_operation(previous_scoreboard, modified_scoreboard, previous_mips_status, modified_mips_status):  # ALU1功能单元在每个周期的操作
    pass


def alu2_operation(previous_scoreboard, modified_scoreboard, previous_mips_status, modified_mips_status):  # ALU2功能单元在每个周期的操作
    pass


def mem_operation(previous_scoreboard, modified_scoreboard, previous_mips_status, modified_mips_status):  # MEM功能单元在每个周期的操作
    pass


def wb_operation(previous_scoreboard, modified_scoreboard, previous_mips_status, modified_mips_status):  # WB功能单元在每个周期的操作
    pass



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