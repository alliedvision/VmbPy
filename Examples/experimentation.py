import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from vimba import *

def change_handler(feat):
    try:
        feat.set(feat.get())

    except VimbaFeatureError as e:
        print(e)

def main():
    sys = System.get_instance()

    print(help(sys))
    print(sys.set_network_discovery.__doc__)

if __name__ == '__main__':
    main()
