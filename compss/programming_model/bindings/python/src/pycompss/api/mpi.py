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
PyCOMPSs API - MPI
==================
    This file contains the class mpi, needed for the mpi
    definition through the decorator.
"""

from functools import wraps
import pycompss.util.context as context
from pycompss.api.commons.error_msgs import not_in_pycompss
from pycompss.api.commons.decorator import PyCOMPSsDecorator
from pycompss.api.commons.decorator import keep_arguments
from pycompss.api.commons.decorator import CORE_ELEMENT_KEY
from pycompss.runtime.task.core_element import CE
from pycompss.util.arguments import check_arguments

if __debug__:
    import logging

    logger = logging.getLogger(__name__)

MANDATORY_ARGUMENTS = {'runner'}
SUPPORTED_ARGUMENTS = {'binary',
                       'processes',
                       'working_dir',
                       'binary',
                       'runner',
                       'flags',
                       'scale_by_cu',
                       'fail_by_exit_value'}
DEPRECATED_ARGUMENTS = {'computing_nodes',
                        'computingNodes',
                        'workingDir'}


class MPI(PyCOMPSsDecorator):
    """
    This decorator also preserves the argspec, but includes the __init__ and
    __call__ methods, useful on mpi task creation.
    """

    __slots__ = ['task_type']

    def __init__(self, *args, **kwargs):
        """ Store arguments passed to the decorator.

        self = itself.
        args = not used.
        kwargs = dictionary with the given mpi parameters.

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        self.task_type = "mpi"
        decorator_name = '@' + self.__class__.__name__.lower()
        super(self.__class__, self).__init__(decorator_name, *args, **kwargs)
        if self.scope:
            if __debug__:
                logger.debug("Init @mpi decorator...")

            layout_nums = 0
            # TODO: Maybe add here the collection layout to avoid iterate twice per elements
            # Add <param_name>_layout params to SUPPORTED_ARGUMENTS
            for key in self.kwargs.keys():
                if "_layout" in key:
                   layout_nums += 1
                   SUPPORTED_ARGUMENTS.add(key)
            
            if layout_nums > 1:
               raise Exception("More than one layout definition is not yet supported!")
           
            # Check the arguments
            check_arguments(MANDATORY_ARGUMENTS,
                            DEPRECATED_ARGUMENTS,
                            SUPPORTED_ARGUMENTS | DEPRECATED_ARGUMENTS,
                            list(kwargs.keys()),
                            decorator_name)

            # Get the computing nodes
            self.__process_computing_nodes__(decorator_name)

            # Set default value if it has not been defined
            if 'processes' not in self.kwargs:
                self.kwargs['processes'] = 1

            # The processes parameter will have to go down until the execution is invoked.
            # WARNING: processes can be an int, a env string, a str with dynamic variable name.
            if __debug__:
                logger.debug("This MPI task will have " +
                             str(self.kwargs['processes']) + " processes.")
        else:
            pass

    def __call__(self, func):
        """ Parse and set the mpi parameters within the task core element.

        :param func: Function to decorate.
        :return: Decorated function.
        """

        @wraps(func)
        def mpi_f(*args, **kwargs):
            if not self.scope:
                raise Exception(not_in_pycompss("mpi"))

            if __debug__:
                logger.debug("Executing mpi_f wrapper.")

            if context.in_master():
                # master code
                if not self.core_element_configured:
                    self.__configure_core_element__(kwargs)
            else:
                # worker code
                pass

            # Set the computing_nodes variable in kwargs for its usage
            # in @task decorator
            kwargs['computing_nodes'] = self.kwargs['processes']

            if self.task_type == "PYTHON_MPI":
                prepend_strings = True
            else:
                prepend_strings = False

            with keep_arguments(args, kwargs, prepend_strings=prepend_strings):
                # Call the method
                ret = func(*args, **kwargs)

            return ret

        mpi_f.__doc__ = func.__doc__
        return mpi_f
    def __resolve_collection_layout_params__(self, kwargs):
        param_name = ""
        block_count = -1
        block_length = -1
        stride = -1

        for key, value in self.kwargs.items():
            if "_layout" in key:
               param_name = key.split("_layout")[0]
               collection_layout = value
               if "block_count" in collection_layout:
                   block_count = collection_layout["block_count"]
               else:
                   block_count = -1

               if "block_length" in collection_layout:
                   block_length = collection_layout["block_length"]
               else:
                   block_length = -1

               if "stride" in collection_layout:
                  stride = collection_layout["stride"]
               else:
                  stride = -1

               if (block_length != -1 and block_count == -1) or (stride != -1 and block_count == -1):
                       raise Exception("Error: collection_layout must contain block_count!")

        return [param_name, str(block_count), str(block_length), str(stride)]


    def __configure_core_element__(self, kwargs):
        # type: (dict) -> None
        """ Include the registering info related to @mpi.

        IMPORTANT! Updates self.kwargs[CORE_ELEMENT_KEY].

        :param kwargs: Keyword arguments received from call.
        :return: None
        """
        if __debug__:
            logger.debug("Configuring @mpi core element.")

        # Resolve @mpi specific parameters
        if "binary" in self.kwargs:
            binary = self.kwargs['binary']
            impl_type = "MPI"
        else:
            binary = "[unassigned]"
            impl_type = "PYTHON_MPI"
            self.task_type = impl_type

        runner = self.kwargs['runner']

        if 'flags' in self.kwargs:
            flags = self.kwargs['flags']
        else:
            flags = '[unassigned]'  # Empty or '[unassigned]'

        if 'scale_by_cu' in self.kwargs:
            scale_by_cu = self.kwargs['scale_by_cu']
            if isinstance(scale_by_cu, bool):
                if scale_by_cu:
                    scale_by_cu_str = 'true'
                else:
                    scale_by_cu_str = 'false'
            elif isinstance(scale_by_cu, str):
                scale_by_cu_str = scale_by_cu
            else:
                raise Exception("Incorrect format for scale_by_cu property. " +  # noqa: E501
                                "It should be boolean or an environment variable")  # noqa: E501
        else:
            scale_by_cu_str = 'false'

        # Resolve the working directory
        self.__resolve_working_dir__()
        # Resolve the fail by exit value
        self.__resolve_fail_by_exit_value__()
        # Resolve parameter collection layout
        collection_layout_params = self.__resolve_collection_layout_params__()

        if binary == "[unassigned]":
            impl_signature = impl_type + '.'
        else:
            impl_signature = '.'.join((impl_type,
                                       str(self.kwargs['processes']),
                                       binary))
        impl_args = [binary,
                     self.kwargs['working_dir'],
                     runner,
                     flags,
                     scale_by_cu_str,
                     self.kwargs['fail_by_exit_value']] + collection_layout_params

        if CORE_ELEMENT_KEY in kwargs:
            # Core element has already been created in a higher level decorator
            # (e.g. @constraint)
            kwargs[CORE_ELEMENT_KEY].set_impl_type(impl_type)
            kwargs[CORE_ELEMENT_KEY].set_impl_signature(impl_signature)
            kwargs[CORE_ELEMENT_KEY].set_impl_type_args(impl_args)
        else:
            # @binary is in the top of the decorators stack.
            # Instantiate a new core element object, update it and include
            # it into kwarg
            core_element = CE()
            core_element.set_impl_type(impl_type)
            core_element.set_impl_signature(impl_signature)
            core_element.set_impl_type_args(impl_args)
            kwargs[CORE_ELEMENT_KEY] = core_element

        # Set as configured
        self.core_element_configured = True


# ########################################################################### #
# ##################### MPI DECORATOR ALTERNATIVE NAME ###################### #
# ########################################################################### #

mpi = MPI
