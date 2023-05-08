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
import os
import sys

from vmbpy.util import *
from vmbpy.util.tracer import _Tracer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers import VmbPyTestCase


class TracerTest(VmbPyTestCase):
    def setUp(self):
        self.log = Log.get_instance()

        self.log.enable(LOG_CONFIG_CRITICAL_CONSOLE_ONLY)

    def tearDown(self):
        self.log.disable()

    def test_trace_normal_exit(self):
        # Expectation: Must not throw on call normal func.
        # Each traced call must add two Log entries:

        @TraceEnable()
        def test_func(arg):
            return str(arg)

        with self.assertLogs(self.log, level=LogLevel.Trace) as logs:
            self.assertEqual(test_func(1), '1')
            self.assertEqual(len(logs.records), 2)

            self.assertEqual(test_func('test'), 'test')
            self.assertEqual(len(logs.records), 4)

            self.assertEqual(test_func(2.0), '2.0')
            self.assertEqual(len(logs.records), 6)

    def test_trace_raised_exit(self):
        # Expectation: Throws internally thrown exception and adds two log entries
        # Each traced call must add two Log entries:

        @TraceEnable()
        def test_func(arg):
            raise TypeError('my error')

        with self.assertLogs(self.log, level=LogLevel.Trace) as logs:
            self.assertRaises(TypeError, test_func, 1)
            self.assertEqual(len(logs.records), 2)

            self.assertRaises(TypeError, test_func, 'test')
            self.assertEqual(len(logs.records), 4)

            self.assertRaises(TypeError, test_func, 2.0)
            self.assertEqual(len(logs.records), 6)

    def test_trace_function(self):
        # Expectation: Normal functions must be traceable
        @TraceEnable()
        def test_func():
            pass

        with self.assertLogs(self.log, level=LogLevel.Trace) as logs:
            test_func()
            self.assertEqual(len(logs.records), 2)

            test_func()
            self.assertEqual(len(logs.records), 4)

            test_func()
            self.assertEqual(len(logs.records), 6)

    def test_trace_lambda(self):
        # Expectation: Lambdas must be traceable

        test_lambda = TraceEnable()(lambda: 0)

        with self.assertLogs(self.log, level=LogLevel.Trace) as logs:
            test_lambda()
            self.assertEqual(len(logs.records), 2)

            test_lambda()
            self.assertEqual(len(logs.records), 4)

            test_lambda()
            self.assertEqual(len(logs.records), 6)

    def test_trace_object(self):
        # Expectation: Objects must be traceable including constructors.
        class TestObj:
            @TraceEnable()
            def __init__(self, arg):
                self.arg = arg

            @TraceEnable()
            def __str__(self):
                return 'TestObj({})'.format(str(self.arg))

            @TraceEnable()
            def __repr__(self):
                return 'TestObj({})'.format(repr(self.arg))

            @TraceEnable()
            def __call__(self):
                pass

        with self.assertLogs(self.log, level=LogLevel.Trace) as logs:
            test_obj = TestObj('test')
            self.assertEqual(len(logs.records), 2)

            str(test_obj)
            self.assertEqual(len(logs.records), 4)

            repr(test_obj)
            self.assertEqual(len(logs.records), 6)

            test_obj()
            self.assertEqual(len(logs.records), 8)

    def test_tracer_is_log_enabled(self):
        # Expectation: The `_Tracer` class correctly determines if logging is enabled or disabled.
        # This reduces overhead by not attempting to create trace entries if logging has been
        # completely disabled
        self.assertTrue(_Tracer.is_log_enabled())  # Logging is enabled in `setUp` of the test class
        self.log.disable()
        self.assertFalse(_Tracer.is_log_enabled())
