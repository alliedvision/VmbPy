import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vimba

#from vimba import *


def main():
    sys = vimba.System.get_instance()

    help(vimba.c_binding)

if __name__ == '__main__':
    main()
