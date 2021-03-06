import sys, struct, parser, error

from parser import Instr, Operand, Label, Literal
from parser import IMPL, IMM, ABS, ZP_ABS, ABS_X, INDIR, JMP_ABS, INDEXED_INDIR_X, INDIR_INDEXED_X


"""
Generate operand.
"""
def generate_operand(operand, symbol_table, ln_no, path):
    value = operand.value

    if isinstance(operand.value, Label):
        if operand.value.identifier.lower() not in symbol_table:
            error.error("Label not defined: " + operand.value.identifier.lower(), ln_no, path)
        value = operand.value.transform_fn(symbol_table[operand.value.identifier.lower()]) + operand.value.offset
    
    if len(operand) == 1: # 8-bit operand
        return (struct.pack("B", value), 1)
    elif len(operand) == 2:                                       # 16-bit operand
        return (struct.pack("<H", value), 2)

    
"""
Generate instruction.
"""
def generate_instr(instr, symbol_table, ln_no, path):
    operation = instr.op_code() << 3
    
    operation = operation | instr.addr_mode(ln_no, path)
    
    operand, operand_size = generate_operand(instr.operand, symbol_table, ln_no, path)
    return ([struct.pack("B", operation), operand], 1 + operand_size)


def generate_literal(literal, symbol_table, ln_no, path):
    if isinstance(literal.data, Label):
        if operand.value.identifier.lower() not in symbol_table:
            error.error("Label not defined: " + operand.value.identifier.lower(), ln_no, path)

        return (struct.pack("<H", symbol_table[operand.value.identifier.lower()]), 2)
    else:
        return (literal.data, len(literal))
    
"""
Generate symbol table and calculate label offsets.
"""
def generate_symbol_table(nodes, offset):
    position = offset
    symbol_table = {}
    
    for node in nodes:
        if isinstance(node, Label):
            if node.identifier.lower() in symbol_table:
                error.error("Multiple declarations of '" + node.identifier + "'")
            symbol_table[node.identifier.lower()] = position
        else:
             position += len(node)   
                
    return symbol_table


"""
Generate array containing assembled code.
"""
def generate(nodes, offset, entry_label):
    symbol_table = generate_symbol_table(nodes, offset)

    buf = []
    
    code_size = 0
    for i in range(len(nodes)):
        node = nodes[i]
        if isinstance(node, Literal):
            b, sz = generate_literal(node, symbol_table, i, None)
            buf.extend(b)
            code_size += sz
        elif isinstance(node, Instr):
            b, sz = generate_instr(node, symbol_table, i, None)
            buf.extend(b)
            code_size += sz
    
    entry_point = offset
    if entry_label:
        if entry_label.lower() not in symbol_table:
            error.error("Entry label not defined: " + entry_label.lower(), 0)
        entry_point = symbol_table[entry_label.lower()]

    return (buf, entry_point, code_size)
