import struct, re, error

""" OPs """
ops = ["NOP", "LDA", "TAX", "TXA", "TAY", "TYA", "ADC","SBC", "AND", "ORA", "EOR", "ASL", "LSR", "INX", "DEX", "JMP", "STA", "PHA", "PLA", "JSR", "RTS", "CMP", "BCS", "BEQ", "BMI", "BNE", "BPL", "BIT", "LDX", "LDY", "STX", "STY"]
jmp_ops = [ "JMP", "JSR", "BCS", "BEQ", "BMI", "BNE", "BPL"]

""" Addressing Modes """
IMM, ABS, ZP_ABS, ABS_X, INDIR, JMP_ABS, INDEXED_INDIR_X, INDIR_INDEXED_X = range(8)
IMPL = -1

"""
Instruction.
"""
class Instr:

    """
    Constructor.
    """
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
        
        # Remove ZP addressing from jump operands
        if self.op in jmp_ops:
            if self.operand.mode == ZP_ABS:
                self.operand.mode = ABS

        
    """
    Op-code.
    """
    def op_code(self):
        return ops.index(self.op.upper())


    """
    Addressing mode bits
    """
    def addr_mode(self, ln_no, path):
        if self.op in jmp_ops:
            if self.operand.mode == ABS:
                return JMP_ABS
            elif self.operand.mode == INDIR:
                return ABS
            else:
                error.error(self.op.upper() + " only allows ABSOLUTE and INDIRECT addressing")
        elif self.operand.mode == IMPL:
            return IMM
        else:
            return self.operand.mode
        

    def __str__(self):
        return self.op + " " + str(self.operand)

    
    def __eq__(self, other):
        if not isinstance(other, Instr):
            return False
        return self.op == other.op and self.operand == other.operand

    
    def __len__(self):
        return len(self.operand) + 1


"""
Operand.
"""
class Operand:

    """
    Constructor.
    """
    def __init__(self, mode=IMPL, value=0):
        self.mode = mode
        self.value = value


    def __str__(self):
        if self.mode == IMPL:
            return ""
        
        if self.mode == IMM:
            return "#" + str(self.value)
        
        if self.mode == ABS or self.mode == ZP_ABS or self.mode == JMP_ABS:
            return str(self.value)
        
        if self.mode == ABS_X:
            return str(self.value) + ", X"
        
        if self.mode == INDIR:
            return "(" + str(self.value) + ")"
        
        if self.mode == INDEXED_INDIR_X:
            return "(" + str(self.value) + ", X)"
        
        if self.mode == INDIR_INDEXED_X:
            return "(" + str(self.value) + "), X"

        error.error("Cannot convert operand to string")
            
    def __eq__(self, other):
        if not isinstance(other, Operand):
            return False
        return self.mode == other.mode and self.value == other.value

    def __len__(self):   
        if self.mode in [IMPL, IMM, ZP_ABS]: # 1 byte operands
            return 1
        
        return 2
        

    
"""
Label
"""
class Label:
    def __init__(self, identifier):
        self.identifier = identifier;

    def __str__(self):
        return self.identifier + ":"


class Literal:
    def __init__(self, data):
        if isinstance(data, str):
            self.data = data.encode("ascii")
            print(self.data)
    
"""
Read chars from specified line while fn(c) is true.
"""
def read(line, fn):
    length = 0
    while length < len(line) and fn(line[length]):
        length += 1

    result = line[:length]

    return (line[length:].strip(), result)


"""
Read index from line.
"""
def read_index(line):
    nline, index = read(line, (lambda c : c.upper() in ', X'))
    if re.match(",\s*X", index) == None:
        return (line, None)

    return (nline, index)
    

"""
Parse label.
"""
def parse_label(line, ln_no, path):
    if len(line) == 0:
        return (line, None)

    line, label = read(line, (lambda c : c.isalpha() or c == '_'))
    
    if label.upper() not in ops:
        if not line.startswith(":"):
            error.error("Expected ':'", ln_no, path)
        
        return (line[1:], Label(label))
    else:
        return (line, None)

    
"""
Parse number.
"""
def parse_num(line, ln_no, path):
    line, label = read(line, (lambda c : c.isalpha() or c == '_'))
    if len(label) != 0:
        if label.upper() not in ops:
            return (line, Label(label))
        else:
            error.error("'" + label + "' not a valid label", ln_no, path)
    
    base = 10;
    numbers = "0123456789"
    
    if line.startswith("$"):
        base = 16
        line = line[1:]
        numbers = "0123456789ABCDEF"
        
    line, result = read(line, (lambda c: c.upper() in numbers) )

    if len(result) == 0:
        return (line, None)
    
    try:
        return (line, int(result, base))
    except ValueError:
        error.error("Invalid number literal", ln_no, path)

        
""" 
Return zero page variant of specified mode if available.
 """
def zero_page(mode):
    if mode == ABS:
        return ZP_ABS
    return mode


"""
Return indexed variant of specified mode. If not available raise an error.
"""
def indexed(mode, ln_no, path):
    if mode == ABS:
        return ABS_X
    if mode == INDIR:
        return INDEXED_INDIR_X
    error.error("Bad index", ln_no, path)


"""
Parse immediate operand.
"""
def parse_imm(line, ln_no, path):
    if not line.startswith("#"):
        return (line, None)

    line, value = parse_num(line[1:], ln_no, path)

    if value == None:
        error.error("Expected immediate value")

    if value > 255:
        error.error("Operand must be in range 0-255", ln_no, path)

    return (line, Operand(IMM, value))


"""
Parse absolute operand.
"""
def parse_abs(line, ln_no, path):
    mode = ABS
    
    line, value = parse_num(line, ln_no, path)

    if value == None:
        return (line, None)

    line, index = read_index(line)
    if index != None:
        mode = ABS_X
   
    return (line, Operand(mode, value))


"""
Parse indirect operand.
"""
def parse_indir(line, ln_no, path):
    mode = INDIR
    
    if not line.startswith("("):
        return (line, None)
    
    line, value = parse_num(line[1:], ln_no, path)
    
    if value == None:
        error.error("Expected indirect address")

    line, index = read_index(line)
    if index != None:
        mode = INDEXED_INDIR_X
        
    if not line.startswith(")"):
        error.error("Expected ')'", ln_no)

    line = line[1:]

    line, index = read_index(line)
    if index != None:
        if mode == INDEXED_INDIR_X:
            error.error("Only one index level supported")
        else:
            mode = INDIR_INDEXED_X

    return (line, Operand(mode, value))


"""
Parse operand.
"""        
def parse_operand(line, ln_no, path):
    operand = None
    
    operand_parse_functions = [ parse_imm, parse_abs, parse_indir ]
    for fn in operand_parse_functions:
        line, operand = fn(line, ln_no, path)

        if operand != None:
            break

    if operand == None:
        return (line, Operand())
    
    if not isinstance(operand.value, Label) and operand.value < 256:
        operand.mode = zero_page(operand.mode)
    
    if not isinstance(operand.value, Label) and operand.value > 65535:
        error.error("Operand must be in range 0-65535", ln_no, path)
    
    return (line, operand)
    

"""
Parse instruction.
"""
def parse_instr(line, ln_no, path):
    line, op = read(line, str.isalpha)

    if len(op) == 0:
        return (line, None)
    
    if op.upper() not in ops:
        error.error("Unknown instruction: '" + op + "'", ln_no, path)

    line, operand = parse_operand(line, ln_no, path)
        
    return (line, Instr(op, operand))


"""
Parse line.
"""
def parse_line(line, ln_no, path):
    line = line.strip()
    
    if line.startswith(";"):
        return [ ]

    nline, label = parse_label(line, ln_no, path)
    if label != None:
        return [ label ] + parse_line(nline, ln_no, path)

    line, op = parse_instr(line, ln_no, path)
    
    if len(line) > 0 and not line.trim().startswith(";"):
        error.error("Unexpected trailing characters '" + line + "'", ln_no, path)

    if op == None:
        return [ ]
    
    return [ op ]


"""
Parse file with specified path.
"""
def parse(paths):
    nodes = []
    
    for path in paths:
        ln_no = 0
        try:
            with open(path, "r") as f:
                for line in f:
                    parsed_line = parse_line(line, ln_no, path)
                    nodes.extend(parsed_line)
                    ln_no += 1
                    
                    
        except:
            error.error("Error opening file", path=path)

    return nodes
