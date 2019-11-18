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

# instruction = "SW R15, 340(R6)"
# rt_index = int(instruction[3:].replace(" ", "").split(',')[0][1:])
# comma_index = int(instruction[3:].replace(" ", "").index(','))
# left_parenthesis_index = int(instruction[3:].replace(" ", "").index('('))
# offset = int(instruction[3:].replace(" ", "")[comma_index + 1:left_parenthesis_index])
# base_index = int(instruction[3:].replace(" ", "")[left_parenthesis_index + 2:-1])
#
# print(rt_index, base_index)


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

MIPS_STATUS = issue_one_instruction('ADD R1, R0, R0', 0, MIPS_STATUS)
print(SCOREBOARD_STATUS)
print(MIPS_STATUS)

# 在判断是否可以issue之前必须前清空SCOREBOARD中已经取完操作数的指令在Operand表中的表项
if len(MIPS_STATUS['Pre_ALU1']) >= 1:
    excuted_alu1_instruction = MIPS_STATUS['Pre_ALU1'][0][2:-1]
    excuted_read_regs_set, excuted_write_regs_set = extract_regs(excuted_alu1_instruction)
    for reg in excuted_read_regs_set:
        SCOREBOARD_STATUS['Regs_Operand_Status'][reg] = ''
if len(MIPS_STATUS['Pre_ALU2']) >= 1:

    excuted_alu2_instruction = MIPS_STATUS['Pre_ALU2'][0][2:-1]
    print(excuted_alu2_instruction)
    excuted_read_regs_set, excuted_write_regs_set = extract_regs(excuted_alu2_instruction)
    print(excuted_read_regs_set)
    print(excuted_write_regs_set)
    for reg in excuted_read_regs_set:
        print(reg)
        print(SCOREBOARD_STATUS['Regs_Operand_Status'][0])
        SCOREBOARD_STATUS['Regs_Operand_Status'][reg] = ''
        print(SCOREBOARD_STATUS['Regs_Operand_Status'][0])
print(SCOREBOARD_STATUS)