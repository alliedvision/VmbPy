"""BSD 2-Clause License

Copyright (c) 2022, Allied Vision Technologies GmbH
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import logging  # Only needed for manual logging configuration

from vmbpy import *


def main():
    print('//////////////////////////////////////')
    print('/// vmbpy Create Trace Log Example ///')
    print('//////////////////////////////////////\n')

    # Enable logging mechanism, creating a trace log. The log file is
    # stored at the location this script was executed from.
    vmb = VmbSystem.get_instance()
    vmb.enable_log(LOG_CONFIG_TRACE_FILE_ONLY)

    # While entering this scope, feature, camera and interface discovery occurs.
    # All function calls to VmbC are captured in the log file.
    with vmb:
        pass

    vmb.disable_log()


def manual_configuration():
    print('//////////////////////////////////////////////')
    print('/// vmbpy Manual Log Configuration Example ///')
    print('//////////////////////////////////////////////\n')

    # By default the vmbpy logger instance will not forward its log messages to any handlers. To
    # integrate log messages a handler needs to be added to the logger instance. In this example we
    # log just the message to the console
    logger = Log.get_instance()
    # Alternatively the logger instance can also be retrieved by its name: `vmbpyLog`
    # logger = logging.getLogger('vmbpyLog')
    handler = logging.StreamHandler()
    logger.addHandler(handler)

    # By default the level of `logger` is set to the custom level `LogLevel.Trace` defined by VmbPy.
    # This will create a lot of output. Adjust as needed for your desired log level
    logger.setLevel(logging.INFO)

    # While entering this scope, feature, camera and interface discovery occurs. Only INFO messages
    # and higher will be logged since we set the `logger` level to that
    vmb = VmbSystem.get_instance()
    with vmb:
        pass


if __name__ == '__main__':
    main()
    # manual_configuration()
