from __future__ import print_function

import sys

"""
Print error message and exit.
"""
def error(message, ln_no=-1, path=None):
    if path:
        message = path + ": " + message
    
    if ln_no >= 0:
        message = "[" + str(ln_no) + "] " + message

    print(message, file=sys.stderr)
        
    sys.exit(1)
