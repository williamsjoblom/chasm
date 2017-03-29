#!/usr/bin/env python

import sys, error, parser, codegen

def assemble_file(path):      
        nodes = parser.parse(path)
        buf = codegen.generate(nodes)
        
        with open("a.out", 'wb') as f:
            for b in buf:
                f.write(b)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        error.error("syntax: chasm INPUT_FILE")
    assemble_file(sys.argv[1])
