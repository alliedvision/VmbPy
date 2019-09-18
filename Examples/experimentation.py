import os
import sys
import time
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Cam:
    def __init__(self, id):
        self.__id = id

    def __str__(self):
        return 'Cam(id={})'.format(self.__id)

    def __eq__(self, other):
        return self.__id == other.__id

class Sys:
    def __init__(self):
        self.__cams = []

    def add_cam(self, cam):
        if cam not in self.__cams:
            self.__cams.append(cam)

    def del_cam(self, cam):
        if cam in self.__cams:
            self.__cams.remove(cam)

    def get_cams(self):
        return tuple(self.__cams)

def main():
    sys = Sys()

    cams_1 = sys.get_cams()

    sys.add_cam(Cam(1))
    sys.add_cam(Cam(2))
    sys.add_cam(Cam(3))

    cams_2 = sys.get_cams()

    sys.del_cam(Cam(2))

    cams_3 = sys.get_cams()

    print(cams_1)
    print(cams_2)
    print(cams_3)

if __name__ == '__main__':
    main()
