#!/bin/bash

# BSD 2-Clause License
#
# Copyright (c) 2019, Allied Vision Technologies GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# THE SOFTWARE IS PRELIMINARY AND STILL IN TESTING AND VERIFICATION PHASE AND
# IS PROVIDED ON AN “AS IS” AND “AS AVAILABLE” BASIS AND IS BELIEVED TO CONTAIN DEFECTS.
# A PRIMARY PURPOSE OF THIS EARLY ACCESS IS TO OBTAIN FEEDBACK ON PERFORMANCE AND
# THE IDENTIFICATION OF DEFECT SOFTWARE, HARDWARE AND DOCUMENTATION.


function get_input()
{
    QUESTION=$1
    ANSWER=""

    while [[ $ANSWER != "yes" ]] && [[ $ANSWER != "no" ]]
    do
        echo -n $QUESTION
        read ANSWER
    done

    [[ $ANSWER == "yes" ]]
}


PYTHONS=$(ls /usr/bin /usr/local/bin | grep "^python[[:digit:]]\?\.\?[[:digit:]]\?\.\?[[:digit:]]\?$" | tr '\n' ' ')
PYTHON="unknown"
TARGET=""


# Sanity checks
echo "VimbaPython installation."

if [ $UID -ne 0 ]
then
    echo "Error: Installation requires root priviliges. Abort."
    exit 1
fi

if [ ! -e "./setup.py" ]
then
    echo "Error: ./setup.py not found. Please execute Install.sh within VimbaPython directory."
    exit 1
fi

if [ -z "$PYTHONS" ]
then
    echo "Error: No Python installations were found. Abort."
    exit 1
fi


# 1) Select Python interpreter
echo "The following Python versions were detected: $PYTHONS"
while [[ !($PYTHONS =~ (^|[[:space:]])$PYTHON($|[[:space:]])) ]]
do
    TMP=""

    echo -n "1) Please select the Python interpreter to use: "
    read TMP

    if [ -n "$TMP" ]
    then
        PYTHON=$TMP
    fi
done
echo "    Installing VimbaPython for $PYTHON"


# 2) Ask for OpenCV support
get_input "2) Install VimbaPython with OpenCV support (yes/no):"
if [ $? -eq 0 ]
then
    TARGET="opencv-export"
fi

# 2) Ask for numpy support
get_input "3) Install VimbaPython with numpy support (yes/no):"
if [ $? -eq 0 ]
then
    if [ -z $TARGET ]
    then
        TARGET="numpy-export"
    else
        TARGET=$TARGET,numpy-export
    fi
fi

# 3) Ask for unittest support
get_input "4) Install VimbaPython with unittest support (yes/no):"
if [ $? -eq 0 ]
then
    if [ -z $TARGET ]
    then
        TARGET="test"
    else
        TARGET=$TARGET,test
    fi
fi

# Execute installation via pip
if [ -z $TARGET ]
then
    TARGET="."
else
    TARGET=".[$TARGET]"
fi

$PYTHON -m pip install $TARGET

if [ $? -eq 0 ]
then
    echo "VimbaPython installation successful."
else
    echo "Error: VimbaPython installation failed. Please check pip output for details."
fi
