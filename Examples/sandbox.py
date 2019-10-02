# TODO: Add License
# TODO: Add Copywrite Note
# TODA: Add Contact Info (clarify if this is required...)

import ctypes
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vimba import *

#class Context:
#    def __init__(self):
#        setattr(self, 'out_context', getattr(self, '_Context__out_context'))

#    def __enter__(self):
#        delattr(self, 'out_context')
#        setattr(self, 'in_context', getattr(self, '_Context__in_context'))

#    def __exit__(self, _1, _2, _3):
#        delattr(self, 'in_context')
#        setattr(self, 'out_context', getattr(self, '_Context__out_context'))

#    def __in_context(self):
#        print('Existing only inside')

#    def __out_context(self):
#        print('Existing only outside')

def main():
    pass

 #   test = Context()

#    # Usage outside of Context
#    test.out_context()

#    try:
#        test.in_context()

#    except AttributeError:
#        print('Tried test.in_context()')

#    # Usage within Context
#    with test:
#        test.in_context()

#        try:
#            test.out_context()

#        except AttributeError:
#            print('Tried test.out_context()')

#    # Usage outside of Context
#    test.out_context()

#    try:
#        test.in_context()

#    except AttributeError:
#        print('Tried test.in_context()')

if __name__ == '__main__':
    main()

