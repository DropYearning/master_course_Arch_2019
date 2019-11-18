# -*- coding: utf-8 -*-
# @Time    : 2019/11/17 5:42 下午
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
    'Pre_Issue': [],  # 4 entry at most
    'Pre_ALU1': [],  # 2 entry at most
    'Pre_ALU2': [],  # 2 entry at most
    'Pre_MEM': "",  # 1 entry
    'Post_ALU2': "",  # 1 entry
    'Post_MEM': "",  # 1 entry
    # 下面是一些用在MEM和WB单元的buffer
    'Pre_MEM_target_address': None,  # LS类指令的目标地址
    'Pre_MEM_target_reg': None,  # LS类指令的目标寄存器
    'Post_MEM_value': None,  # Load指令需要写入的值
    'Post_MEM_target_reg': None,  # Load指令需要写入的寄存器
    'Post_ALU2_value': None,  # 非LS类指令的结果值
    'Post_ALU2_target_reg': None  # 非LS类指令的目标寄存器
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


def fetch_one_instruction(instruction, previous_mips_status, previous_modified_mips_status):  # 每种指令在IF单元需要进行的操作
    temp_modified_mips_status = previous_modified_mips_status
    global SCOREBOARD_STATUS
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
        if SCOREBOARD_STATUS['Regs_Result_Status'][rs_index] == '':  # rs准备好
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
        if SCOREBOARD_STATUS['Regs_Result_Status'][rs_index] == '' and \
                SCOREBOARD_STATUS['Regs_Result_Status'][rt_index] == '':  # rs和rt准备好
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
        if SCOREBOARD_STATUS['Regs_Result_Status'][rs_index] == '':  # rs准备好
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


def fetch_operation(previous_mips_status):  # IF功能单元在每个周期的操作
    # IF单元承担改变PC的任务
    # stall_sign = previous_mips_status['IF_Stall']  # 在IF单元最后（本周期末）更新IF_Stall
    temp_modified_mips_status = previous_mips_status
    global SCOREBOARD_STATUS
    # 若IF单元Stall，本周期不提取任何指令
    if previous_mips_status['IF_Stall']:
        # 检查[Waiting Instruction]中原来不可用的寄存器是否已经可用
        instruction_waiting = previous_mips_status['IF_Waiting'][2:-1]
        op = instruction_waiting.split()[0]
        if op == 'JR':
            rs_index = int(instruction_waiting.split()[1][1:])
            if SCOREBOARD_STATUS['Regs_Result_Status'][rs_index] == '':  # rs准备好
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
            if SCOREBOARD_STATUS['Regs_Result_Status'][rs_index] == '' and \
                    SCOREBOARD_STATUS['Regs_Result_Status'][rt_index] == '':  # rs和rt准备好
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
            if SCOREBOARD_STATUS['Regs_Result_Status'][rs_index] == '':  # rs准备好
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
        temp_modified_mips_status = fetch_one_instruction(instruction_fetched, previous_mips_status,
                                                          temp_modified_mips_status)

    # 若本周期可以提取2条指令
    elif len(previous_mips_status['Pre_Issue']) <= 2:
        instruction_fetched_1 = INSTRUCTION_SEQUENCE[previous_mips_status['PC']]
        op1 = instruction_fetched_1.split()[0]
        if op1 in ['J', 'JR', 'BEQ', 'BLTZ', 'BGTZ', 'BREAK']:  # 不再取instruction_fetched_2
            temp_modified_mips_status = fetch_one_instruction(instruction_fetched_1, previous_mips_status,
                                                              temp_modified_mips_status)
        else:  # 再取第二条指令
            instruction_fetched_2 = INSTRUCTION_SEQUENCE[previous_mips_status['PC'] + 4]  # 没有分支，所以PC=PC+4
            temp_modified_mips_status = fetch_one_instruction(instruction_fetched_1, previous_mips_status,
                                                              temp_modified_mips_status)
            temp_modified_mips_status = fetch_one_instruction(instruction_fetched_2, previous_mips_status,
                                                              temp_modified_mips_status)
    return temp_modified_mips_status


def extract_regs(instruction):  # 从指令中抽取要读的寄存器和要写的寄存器序号集合
    read_regs_set = set()
    write_regs_set = set()
    op = instruction.split()[0]
    if op in ['SLL', 'SRL', 'SRA']:  # rd ← rt >> sa
        rd_index = int(instruction[4:].replace(" ", "").split(',')[0][1:])
        rt_index = int(instruction[4:].replace(" ", "").split(',')[1][1:])
        sa = int(instruction[4:].replace(" ", "").split(',')[2][1:])
        read_regs_set.add(rt_index)
        write_regs_set.add(rd_index)
    elif op in ['ADD', 'SUB', 'MUL', 'AND', 'OR', 'XOR', 'NOR', 'SLT']:  # rd ← rs × rt
        rd_index = int(instruction[4:].replace(" ", "").split(',')[0][1:])
        rs_index = int(instruction[4:].replace(" ", "").split(',')[1][1:])
        rt_index = int(instruction[4:].replace(" ", "").split(',')[2][1:])
        read_regs_set.add(rt_index)
        read_regs_set.add(rs_index)
        write_regs_set.add(rd_index)
    elif op in ['ADDI', 'ANDI', 'ORI', 'XORI']:  # rt ← rs + immediate
        rt_index = int(instruction[4:].replace(" ", "").split(',')[0][1:])
        rs_index = int(instruction[4:].replace(" ", "").split(',')[1][1:])
        read_regs_set.add(rs_index)
        write_regs_set.add(rt_index)
    elif op == 'SW':   # SW rt, offset(base) [memory[base+offset] ← rt]
        rt_index = int(instruction[3:].replace(" ", "").split(',')[0][1:])
        left_parenthesis_index = int(instruction[3:].replace(" ", "").index('('))
        base_index = int(instruction[3:].replace(" ", "")[left_parenthesis_index + 2:-1])
        read_regs_set.add(rt_index)
        read_regs_set.add(base_index)
    elif op == 'LW':  # LW rt, offset(base) [rt ← memory[base+offset]]
        rt_index = int(instruction[3:].replace(" ", "").split(',')[0][1:])
        left_parenthesis_index = int(instruction[3:].replace(" ", "").index('('))
        base_index = int(instruction[3:].replace(" ", "")[left_parenthesis_index + 2:-1])
        write_regs_set.add(rt_index)
        read_regs_set.add(base_index)
    return read_regs_set, write_regs_set


# 判断pre-issue中的某一条指令是否可以发射，只判断WAR，RAW，WAW相关，不判断其他条件（输入的指令格式为：" [instruction]"）
def judge_issue(current_instruction, current_index_in_list, previous_mips_status):
    # instruction_index_in_list是当前指令在pre-issue单元中的序号
    global SCOREBOARD_STATUS
    all_early_read_regs_set = set()  # 所有pre-issue中在该指令前的指令要读的寄存器
    all_early_write_regs_set = set()  # 所有pre-issue中在该指令前的指令要写的寄存器
    current_read_regs_set, current_write_regs_set = extract_regs(current_instruction)
    for i in range(current_index_in_list):
        early_instruction = previous_mips_status['Pre_Issue'][i][2:-1]
        early_read_regs_set, early_write_regs_set = extract_regs(early_instruction)
        all_early_read_regs_set.union(early_read_regs_set)
        all_early_write_regs_set.union(early_write_regs_set)
    # 检查该指令与Pre-issue单元中在它前面的指令之间的相关性
    # Pre-issue队列中在它前面的指令不和它写同一个寄存器
    for reg_index in current_write_regs_set:
        if reg_index in all_early_write_regs_set:
            return False
    # Pre-issue队列中在它前面的指令不写它要读的寄存器
    for reg_index in current_read_regs_set:
        if reg_index in all_early_write_regs_set:
            return False
    # Pre-issue队列中没有指令要读它要写的寄存器
    for reg_index in current_write_regs_set:
        if reg_index in early_read_regs_set:
            return False
    # 检查该指令与已经发射（但未结束）的指令之间的相关性
    # 没有已经发射（但未结束）的指令与它写同一个寄存器
    for reg_index in current_write_regs_set:
        if SCOREBOARD_STATUS['Regs_Result_Status'][reg_index] != '':
            return False
    # 没有已经发射（但未结束）的指令写它要读的寄存器
    for reg_index in current_read_regs_set:
        if SCOREBOARD_STATUS['Regs_Result_Status'][reg_index] != '':
            return False
    # 没有已经发射（但未结束）的指令要读它要写的寄存器
    for reg_index in current_write_regs_set:
        if SCOREBOARD_STATUS['Regs_Operand_Status'][reg_index] != '':
            return False
    return True


def issue_one_instruction(instruction, instruction_index, previous_modified_mips_status):  # 发射某一条指令
    global SCOREBOARD_STATUS
    temp_modified_mips_status = previous_modified_mips_status
    op = instruction.split()[0]
    # 修改SCOREBOARD_STATUS中的Operand表和Result表
    current_read_regs_set, current_write_regs_set = extract_regs(instruction)
    for reg_index in current_read_regs_set:
        SCOREBOARD_STATUS['Regs_Operand_Status'][reg_index] = instruction
    for reg_index in current_write_regs_set:
        SCOREBOARD_STATUS['Regs_Result_Status'][reg_index] = instruction
    if op in ['SW', 'LW']:  # 走ALU1
        del temp_modified_mips_status['Pre_Issue'][instruction_index]
        temp_modified_mips_status['Pre_ALU1'].append(' [' + instruction + ']')
    else:    # 走ALU2 立即数
        del temp_modified_mips_status['Pre_Issue'][instruction_index]
        temp_modified_mips_status['Pre_ALU2'].append(' [' + instruction + ']')
    return temp_modified_mips_status


def issue_operation(previous_mips_status, previous_modified_mips_status):  # Issue功能单元在每个周期的操作
    global SCOREBOARD_STATUS
    ls_issued = False  # 是否已经发射过一条LS类指令
    non_ls_issued = False  # 是否已经发射过一条非LS类指令
    temp_modified_mips_status = previous_modified_mips_status
    # 在判断是否可以issue之前必须前清空SCOREBOARD中已经取完操作数的指令在Operand表中的表项
    if len(previous_mips_status['Pre_ALU1']) >= 1:
        excuted_alu1_instruction = previous_mips_status['Pre_ALU1'][0][2:-1]
        excuted_read_regs_set, excuted_write_regs_set = extract_regs(excuted_alu1_instruction)
        for reg in excuted_read_regs_set:
            SCOREBOARD_STATUS['Regs_Operand_Status'][reg] = ''
    if len(previous_mips_status['Pre_ALU2']) >= 1:
        excuted_alu2_instruction = previous_mips_status['Pre_ALU2'][0][2:-1]
        excuted_read_regs_set, excuted_write_regs_set = extract_regs(excuted_alu2_instruction)
        for reg in excuted_read_regs_set:
            SCOREBOARD_STATUS['Regs_Operand_Status'][reg] = ''
    # 按序判断Pre-issue单元中的指令是否可以发射
    pre_issue_count = len(previous_mips_status['Pre_Issue'])
    if pre_issue_count == 0:  # 没有要发射的指令，直接返回
        pass
    else:
        for index, instruction_in_list in enumerate(previous_mips_status['Pre_Issue']):
            current_instruction = instruction_in_list[2:-1]  # 当前要判断的指令
            current_op = current_instruction.split()[0]
            if judge_issue(current_instruction, index, previous_mips_status):  # 若该条指令与活动指令没有WAR，WAW，RAW相关
                if current_op == 'LW':  # 若想要发射的是LW指令
                    # 在这里有检查Pre-ALU1是否有空位的必要吗？ —— 有必要！
                    if len(previous_mips_status['Pre_ALU1']) == 2:  # 若Pre-ALU1没有空位
                        continue  # 不发射这一条
                    elif ls_issued:  # 若本周期之前已经发射过一条LS类指令
                        continue  # 不发射这一条
                    else:
                        # 检查LW指令前是否有未发射的Store指令
                        have_store_previous = False
                        for pre_index in range(index):
                            pre_instruction = previous_mips_status['Pre_Issue'][pre_index]
                            pre_op = pre_instruction[2:-1].split()[0]
                            if pre_op == 'SW':
                                have_store_previous = True
                        if have_store_previous:
                            continue
                        else:  # 检查到这里才可以发射这条LW指令
                            temp_modified_mips_status = issue_one_instruction(current_instruction, index,
                                                                              temp_modified_mips_status)
                            ls_issued = True
                elif current_op == 'SW':  # 若想要发射的是SW指令
                    if len(previous_mips_status['Pre_ALU1']) == 2:  # 若Pre-ALU1没有空位
                        continue  # 不发射这一条
                    elif ls_issued:  # 若本周期之前已经发射过一条LS类指令
                        continue  # 不发射这一条
                    else:
                        # Store指令必须按序发射，检查SW指令前面是否有未发射的Store指令
                        have_store_previous = False
                        for pre_index in range(index):
                            pre_instruction = previous_mips_status['Pre_Issue'][pre_index]
                            pre_op = pre_instruction[2:-1].split()[0]
                            if pre_op == 'SW':
                                have_store_previous = True
                        if have_store_previous:
                            continue
                        else:  # 检查到这里才可以发射这条SW指令
                            temp_modified_mips_status = issue_one_instruction(current_instruction, index,
                                                                              temp_modified_mips_status)
                            ls_issued = True
                else:  # 若想要发射的是其他计算指令
                    if len(previous_mips_status['Pre_ALU2']) == 2:  # 若Pre-ALU2没有空位
                        continue  # 不发射这一条
                    elif non_ls_issued:  # 若之前一条发射过一条非LS类指令
                        continue  # 不发射这一条
                    else:  # 发射
                        temp_modified_mips_status = issue_one_instruction(current_instruction, index,
                                                                          temp_modified_mips_status)
                        non_ls_issued = True
    return temp_modified_mips_status


def alu1_operation(previous_mips_status, previous_modified_mips_status):  # ALU1功能单元在每个周期的操作
    # ALU1 handles the calculation of address for memory (LW and SW) instructions.
    # The instruction and its result will be written into the Pre-MEM buffer at the end of the current cycle.
    temp_modified_mips_status = previous_modified_mips_status
    if len(previous_mips_status['Pre_ALU1']) == 0:  # 若pre-alu1中没有等待执行的指令
        pass
    else:  # 从pre-alu1队列中取一条执行
        instruction_executed = previous_mips_status['Pre_ALU1'][0][2:-1]
        # 从Pre-ALU1队列中删除它
        del temp_modified_mips_status['Pre_ALU1'][0]
        op = instruction_executed.split()[0]
        if op == 'LW':  # LW: IF, Issue, ALU1, MEM, WB;
            target_regs = int(instruction_executed[3:].replace(" ", "").split(',')[0][1:])  # 写目标寄存器
            comma_index = int(instruction_executed[3:].replace(" ", "").index(','))
            left_parenthesis_index = int(instruction_executed[3:].replace(" ", "").index('('))
            offset = int(instruction_executed[3:].replace(" ", "")[comma_index + 1:left_parenthesis_index])
            base = int(instruction_executed[3:].replace(" ", "")[left_parenthesis_index + 2:-1])
            # LW rt, offset(base) [rt ← memory[base+offset]]
            target_adress = previous_mips_status['Data'][offset + previous_mips_status['Registers'][base]]   # 读目标地址
            # 将状态信息写入下一级流水线单元
            temp_modified_mips_status['Pre_MEM_target_address'] = target_adress
            temp_modified_mips_status['Pre_MEM_target_reg'] = target_regs
        else:  # SW: IF, Issue, ALU1, MEM;
            target_regs = int(instruction_executed[3:].replace(" ", "").split(',')[0][1:])  # 写目标寄存器
            comma_index = int(instruction_executed[3:].replace(" ", "").index(','))
            left_parenthesis_index = int(instruction_executed[3:].replace(" ", "").index('('))
            offset = int(instruction_executed[3:].replace(" ", "")[comma_index + 1:left_parenthesis_index])
            base = int(instruction_executed[3:].replace(" ", "")[left_parenthesis_index + 2:-1])
            # SW rt, offset(base) [memory[base+offset] ← rt]
            target_adress = previous_mips_status['Data'][offset + previous_mips_status['Registers'][base]]  # 写目标地址
            # 将状态信息写入下一级流水线单元
            temp_modified_mips_status['Pre_MEM_target_address'] = target_adress
            temp_modified_mips_status['Pre_MEM_target_reg'] = target_regs
    return temp_modified_mips_status


def alu2_operation(previous_mips_status, previous_modified_mips_status):  # ALU2功能单元在每个周期的操作
    # ALU2 handles the calculation of all non-memory instructions.
    # The instruction and its result will be written into the Post-ALU2 buffer at the end of the current cycle.
    temp_modified_mips_status = previous_modified_mips_status
    if len(previous_mips_status['Pre_ALU2']) == 0:  # 若pre-alu2中没有等待执行的指令
        pass
    else:
        instruction_executed = previous_mips_status['Pre_ALU2'][0][2:-1]
        # 从Pre-ALU2队列中删除它
        del temp_modified_mips_status['Pre_ALU2'][0]
        op = instruction_executed.split()[0]
        # 分类执行这条指令


    return temp_modified_mips_status


def mem_operation(previous_mips_status, previous_modified_mips_status):  # MEM功能单元在每个周期的操作
    pass


def wb_operation(previous_mips_status, previous_modified_mips_status):  # WB功能单元在每个周期的操作
    # 若有指令要WB，需要在SCOREBOARD的Result表中删除对应项

    pass


def run_simulation(start_mips_status):  # 开始模拟
    previous_mips_status = start_mips_status  # previous_mips_status是上一个周期结束的状态
    temp_mips_status = start_mips_status  # temp_mips_status是这个周期中被各个功能单元改变的状态
    while not temp_mips_status['END']:
        # 一个Cycle开始
        temp_mips_status['CycleNumber'] = temp_mips_status['CycleNumber'] + 1
        temp_mips_status = fetch_operation(previous_mips_status)  # IF单元操作
        temp_mips_status = issue_operation(previous_mips_status, temp_mips_status)  # ISSUE单元操作
        temp_mips_status = alu1_operation(previous_mips_status, temp_mips_status)  # ALU1单元操作
        temp_mips_status = alu2_operation(previous_mips_status, temp_mips_status)  # ALU1单元操作
        temp_mips_status = mem_operation(previous_mips_status, temp_mips_status)  # MEM单元操作
        temp_mips_status = wb_operation(previous_mips_status, temp_mips_status)  # WB单元操作
        # 一个Cycle结束，打印这个Cycle结束时的状态
        print_cycle_status(temp_mips_status, 'simulation.txt')
        previous_mips_status = temp_mips_status  # 更新上一个周期的状态


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
    run_simulation(MIPS_STATUS)