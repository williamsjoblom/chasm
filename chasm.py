#!/usr/bin/env python

import sys, error, parser, codegen

def assemble_file(path, offset=0):      
    nodes = parser.parse(path)
    buf = codegen.generate(nodes, offset)
        
    with open("a.out", 'wb') as f:
        for b in buf:
            f.write(b)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        error.error("syntax: chasm INPUT_FILE OFFSET")
    
    assemble_file(sys.argv[1], int(sys.argv[2], 16))
