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

function check_interpreter
{
    PYTHON=$1

    # Check if pip works on given interpreter
    $PYTHON -m pip > /dev/null 2>&1
    if [ $? -ne 0 ]
    then
        return
    fi

    # If pip works: Check if VimbaPython is installed
    if [ $($PYTHON -m pip list | grep "VimbaPython" | wc -l) -ne 1 ]
    then
        return
    fi

    echo -n "$PYTHON "
}

# Sanity checks
echo "VimbaPython uninstall script."

if [ $UID -ne 0 ]
then
    echo "Error: Installation requires root privileges. Abort."
    exit 1
fi

# Determine all Interpreters that have VimbaPython installed
PYTHONS=$(ls /usr/bin /usr/local/bin | grep "^python[[:digit:]]\?\.\?[[:digit:]]\?\.\?[[:digit:]]\?$")
PYTHONS=$(for P in $PYTHONS; do check_interpreter $P; done)
PYTHON="unknown"

if [ -z "$PYTHONS" ]
then
    echo "Can't remove VimbaPython. Is not installed."
    exit 0
fi

# Select Python interpreter
echo "The following Python versions have VimbaPython installed: $PYTHONS"
while [[ !($PYTHONS =~ (^|[[:space:]])$PYTHON($|[[:space:]])) ]]
do
    TMP=""

    echo -n "Please enter Python version: "
    read TMP

    if [ -n "$TMP" ]
    then
        PYTHON=$TMP
    fi
done
echo "Removing VimbaPython for $PYTHON"

# Remove VimbaPython
$PYTHON -m pip uninstall VimbaPython
