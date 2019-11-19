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
    'Pre_Issue': [' [LW R3, 300(R16)]', ' [LW R4, 320(R16)]', ' [ADD R5, R3, R4]'],  # 4 entry at most
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

# 计分卡数据结构
SCOREBOARD_STATUS = {
    'Regs_Result_Status': [''] * 32,  # 寄存器结果表(哪一条指令将写这个寄存器)
    'Regs_Operand_Status': [''] * 32,  # 寄存器操作数表(哪一条指令将读这个寄存器)
}


def extract_regs(instruction):  # 从指令中抽取要读的寄存器和要写的寄存器序号集合
    read_regs_set = set('')
    write_regs_set = set('')
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
def judge_issue(current_instruction, current_index_in_list, previous_mips_status, mode=''):
    # instruction_index_in_list是当前指令在pre-issue单元中的序号
    global SCOREBOARD_STATUS
    all_early_read_regs_set = set('')  # 所有pre-issue中在该指令前的指令要读的寄存器
    all_early_write_regs_set = set('')  # 所有pre-issue中在该指令前的指令要写的寄存器
    current_read_regs_set, current_write_regs_set = extract_regs(current_instruction)
    for i in range(current_index_in_list):
        print('检查Pre-issue' + str(i) + '中的指令' + previous_mips_status['Pre_Issue'][i][2:-1])
        early_instruction = previous_mips_status['Pre_Issue'][i][2:-1]
        early_read_regs_set, early_write_regs_set = extract_regs(early_instruction)
        print('从指令', early_instruction, "中抽取出要读的寄存器为", early_read_regs_set, '要写的寄存器为', early_write_regs_set)
        all_early_read_regs_set = all_early_read_regs_set.union(early_read_regs_set)
        all_early_write_regs_set = all_early_write_regs_set.union(early_write_regs_set)
        print('合并指令', early_instruction, "后所有要读的寄存器为", all_early_read_regs_set, '要写的寄存器为', all_early_write_regs_set)
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
        if reg_index in all_early_write_regs_set:
            return False
    # 检查该指令与已经发射（但未结束）的指令之间的相关性
    # 没有已经发射（但未结束）的指令与它写同一个寄存器
    for reg_index in current_write_regs_set:
        if SCOREBOARD_STATUS['Regs_Result_Status'][int(reg_index)] != '':
            return False
    # 没有已经发射（但未结束）的指令写它要读的寄存器
    for reg_index in current_read_regs_set:
        if SCOREBOARD_STATUS['Regs_Result_Status'][int(reg_index)] != '':
            return False
    # 没有已经发射（但未结束）的指令要读它要写的寄存器
    for reg_index in current_write_regs_set:
        if SCOREBOARD_STATUS['Regs_Operand_Status'][int(reg_index)] != '':
            return False
    return True


print(judge_issue('ADD R5, R3, R4', 2, MIPS_STATUS, mode='debug'))
