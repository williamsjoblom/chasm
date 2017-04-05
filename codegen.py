import struct, parser, error

from parser import Instr, Operand, Label
from parser import IMPL, IMM, ABS, ZP_ABS, ABS_X, INDIR, ZP_INDIR, INDEXED_INDIR_X, INDIR_INDEXED_X


"""
Generate operand.
"""
def generate_operand(operand, symbol_table, ln_no):
    value = operand.value

    if isinstance(operand.value, Label):
        if operand.value.identifier.lower() not in symbol_table:
            error.error("Label not defined", ln_no)
        value = symbol_table[operand.value.identifier.lower()]
    
    if len(operand) == 1: # 8-bit operand
        return struct.pack("B", value)
    elif len(operand) == 2:                                       # 16-bit operand
        return struct.pack("<H", value)

    
"""
Generate instruction.
"""
def generate_instr(instr, symbol_table, ln_no):
    operation = instr.op_code() << 3
    
    operation = operation | instr.addr_mode(ln_no)
    return [struct.pack("B", operation), generate_operand(instr.operand, symbol_table, ln_no)]

    
"""
Generate symbol table and calculate label offsets.
"""
def generate_symbol_table(nodes, offset):
    position = offset
    symbol_table = {}
    
    for node in nodes:
        if isinstance(node, Label):
            if node.identifier.lower() in symbol_table:
                error.error("Multiple declarations of '" + node.identifier + "'", i)
            symbol_table[node.identifier.lower()] = position
        else:
             position += len(node)   
                
    return symbol_table


"""
Generate array containing assembled code.
"""
def generate(nodes, offset):
    symbol_table = generate_symbol_table(nodes, offset)
    
    buf = []
    
    for i in range(len(nodes)):
        node = nodes[i]
        if not isinstance(node, Label):
            b = generate_instr(node, symbol_table, i)
            buf.extend(b)

    return buf
