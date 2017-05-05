#!/usr/bin/env python

import sys, math, argparse, struct
import error, parser, codegen

def power_of_two(target):
    if target > 1:
        for i in range(1, int(target)):
            if (2 ** i >= target):
                return 2 ** i
    else:
        return 1

def create_rom_buffer(buf, code_size, size, reset_vector):
    code_size += 2; # Reset vector consumes 2 bytes
    if size == -1:
        size = power_of_two(code_size)
        
    if code_size > size:
        error.error("Code unable to fit in ROM (code size: " + str(code_size) + ", ROM size: " + str(size) + ")")
    
    padding = [b"\x00" for x in range(size - code_size)]

    rom_buffer = []
    rom_buffer.extend(buf) # Machine code
    rom_buffer.extend(padding) # NOP padding
    rom_buffer.extend(struct.pack("<H", reset_vector)) # Reset vector
    return rom_buffer

def assemble_file(path, offset, size, entry_label):      
    nodes = parser.parse(path)
    buf, entry_point, code_size = codegen.generate(nodes, offset, entry_label)

    rom = create_rom_buffer(buf, code_size, size, entry_point)
    
    with open("a.out", 'wb') as f:
        for b in rom:
            f.write(b)

def assemble_vhdl(path, vhdl_path, offset, size, entry_label):
    assemble_file(path, offset, size, entry_label)
     
    vhdl_template = None
    with open(vhdl_path, 'r') as vhdl_file:
        vhdl_template = vhdl_file.read()

    required_bits = int(math.ceil(math.log(size, 2)))

    vhdl_template = vhdl_template.replace("<MAX_INDEX>", str(size - 1))
    vhdl_template = vhdl_template.replace("<MAX_BIT>", str(required_bits - 1))
    
    sp = vhdl_template.split("<BUFFER>")

    print(sp[0])

    print("(")
    with open("a.out", "rb") as f:
        byte = f.read(1)
        first = True
        while byte != "":
            if first:
                print(' x"' + "%0.2x" % ord(byte) + '"')
            else:
                print(',x"' + "%0.2x" % ord(byte) + '"')

            byte = f.read(1)
            first = False
    print(");")

    print(sp[1])

    

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--offset", help="memory offset of first instruction (default: E000)")
    p.add_argument("--vhdl", help="VHDL template")
    p.add_argument("--entry", help="entry point label (default is offset address)")
    p.add_argument("--size", help="rom size")
    p.add_argument("input")
    args = p.parse_args()
    
    offset = args.offset if args.offset else "E000"
    entry_label = args.entry if args.entry else None
    size = args.size if args.size else -1
    
    if args.vhdl:
        assemble_vhdl(args.input, args.vhdl, int(offset, 16), int(size), entry_label)
    else:
        assemble_file(args.input, int(offset, 16), int(size), entry_label)
