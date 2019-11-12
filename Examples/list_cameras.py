# TODO: Add License

# (C) 2019 Allied Vision Technologies GmbH - All Rights Reserved

from vimba import *


def main():
    with Vimba.get_instance() as vimba:
        print('Print id of all detected cameras:')

        for cam in vimba.get_all_cameras():
            msg = 'Camera Name: {}, Model: {}, Camera ID:{}, Serial Number: {}, Interface ID: {}'
            print(msg.format(cam.get_name(), cam.get_model(), cam.get_id(), cam.get_serial(),
                  cam.get_interface_id()))


if __name__ == '__main__':
    main()
