from parser import Instr, Operand
from parser import IMPL, IMM, ABS, ZP_ABS, ABS_X, INDIR, ZP_INDIR, INDEXED_INDIR_X, INDIR_INDEXED_X
import parser

"""
Tiny test for verifying basic functionality.
"""
def test_parser():
    tests = [("NOP", Instr("NOP", Operand(IMPL, None))),
             ("ADC #16", Instr("ADC", Operand(IMM, 16))),
             ("ADC $FF", Instr("ADC", Operand(ZP_ABS, 255))),
             ("ADC 16, X", Instr("ADC", Operand(ABS_X, 16))),
             ("ADC ($100)", Instr("ADC", Operand(INDIR, 256))),
             ("ADC (120)", Instr("ADC", Operand(ZP_INDIR, 120))),
             ("ADC (120, X)", Instr("ADC", Operand(INDEXED_INDIR_X, 120))),
             ("ADC (120), X", Instr("ADC", Operand(INDIR_INDEXED_X, 120))),]

    succeeded = 0
    failed = 0
    
    for i in range(len(tests)):
        test = tests[i]
        result = parser.parse_line(test[0], i)[0]
        if result == test[1]:
            succeeded += 1
        else:
            print("Failed: " + test[0] + " => " + str(result) + "( expected " + str(test[1]) + " )")
            failed += 1

    print(str(succeeded) + " succeeded, " + str(failed) + " failed")
