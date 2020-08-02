#!/usr/bin/python
#
#  Copyright 2002-2019 Barcelona Supercomputing Center (www.bsc.es)
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
PyCOMPSs Core Element
=====================
    This file contains the Core Element class, needed for the task
    registration.
"""


class CE(object):

    __slots__ = ['__ceSignature', '__implSignature', '__implConstraints',
                 '__implType', '__implIO', '__implTypeArgs']

    def __init__(self,
                 ce_signature=None,
                 impl_signature=None,
                 impl_constraints=None,
                 impl_type=None,
                 impl_io=None,
                 impl_type_args=None):
        self.__ceSignature = ce_signature
        self.__implSignature = impl_signature
        self.__implConstraints = impl_constraints
        self.__implType = impl_type
        self.__implIO = impl_io
        self.__implTypeArgs = impl_type_args

    ###########
    # METHODS #
    ###########

    def reset(self):
        self.__ceSignature = None
        self.__implSignature = None
        self.__implConstraints = None
        self.__implType = None
        self.__implIO = None
        self.__implTypeArgs = None

    ###########
    # GETTERS #
    ###########

    def get_ce_signature(self):
        # type: () -> str
        return self.__ceSignature

    def get_impl_signature(self):
        # type: () -> str
        return self.__implSignature

    def get_impl_constraints(self):
        # type: () -> dict
        return self.__implConstraints

    def get_impl_type(self):
        # type: () -> str
        return self.__implType

    def get_impl_io(self):
        # type: () -> bool
        return self.__implIO

    def get_impl_type_args(self):
        # type: () -> list
        return self.__implTypeArgs

    ###########
    # SETTERS #
    ###########

    def set_ce_signature(self, ce_signature):
        # type: (str) -> None
        self.__ceSignature = ce_signature

    def set_impl_signature(self, impl_signature):
        # type: (str) -> None
        self.__implSignature = impl_signature

    def set_impl_constraints(self, impl_constraints):
        # type: (dict) -> None
        self.__implConstraints = impl_constraints

    def set_impl_type(self, impl_type):
        # type: (str) -> None
        self.__implType = impl_type

    def set_impl_io(self, impl_io):
        # type: (bool) -> None
        self.__implIO = impl_io

    def set_impl_type_args(self, impl_type_args):
        # type: (list) -> None
        self.__implTypeArgs = impl_type_args

    ##################
    # REPRESENTATION #
    ##################

    def __repr__(self):
        # type: () -> str
        """ Builds the element representation as string.

        :return: The core element representation.
        """
        _repr = 'CORE ELEMENT: \n'
        _repr += '\t - CE signature     : ' + str(self.__ceSignature) + '\n'
        _repr += '\t - Impl. signature  : ' + str(self.__implSignature) + '\n'
        if self.__implConstraints:
            impl_constraints = ''
            for key, value in self.__implConstraints.items():
                impl_constraints += key + ':' + str(value) + ';'
        else:
            impl_constraints = str(self.__implConstraints)
        _repr += '\t - Impl. constraints: ' + impl_constraints + '\n'
        _repr += '\t - Impl. type       : ' + str(self.__implType) + '\n'
        _repr += '\t - Impl. io         : ' + str(self.__implIO) + '\n'
        _repr += '\t - Impl. type args  : ' + str(self.__implTypeArgs)
        return _repr