#!/usr/bin/python
#
#  Copyright 2002-2021 Barcelona Supercomputing Center (www.bsc.es)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# -*- coding: utf-8 -*-

"""
PyCOMPSs Binding - Utils - typing_helper
========================================
    This file contains the typing helpers.
"""

try:
    import typing
except ImportError:
    # No typing if not available - will not compile with mypyc
    typing = None  # type: ignore
    # message = "WARNING: Typing is not available!!!"
    # print(message)
    # raise Exception(message)


class dummy_mypyc_attr(object):
    """
    Dummy on mypy_attr class (decorator style)
    """

    def __init__(self, *args, **kwargs):
        # type: (*typing.Any, **typing.Any) -> None
        self.args = args
        self.kwargs = kwargs

    def __call__(self, f):
        # type: (typing.Any) -> typing.Any
        def wrapped_mypyc_attr(*args, **kwargs):
            # type: (*typing.Any, **typing.Any) -> typing.Any
            return f(*args, **kwargs)

        return wrapped_mypyc_attr


import_ok = True
try:
    from mypy_extensions import mypyc_attr as real_mypyc_attr
    # https://mypyc.readthedocs.io/en/latest/native_classes.html#inheritance
except ImportError:
    # Dummy mypyc_attr just in case mypy_extensions is not installed
    import_ok = False

if import_ok:
    mypyc_attr = real_mypyc_attr
else:
    mypyc_attr = dummy_mypyc_attr  # type: ignore


######################################
# Boilerplate to mimic user fuctions #
######################################

def dummy_function():
    # type: () -> None
    pass