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

import os
import sys

from pycompss.worker.external.mpi_executor import main
from pycompss.api.task import task


@task()
def simple():
    pass


@task(returns=1)
def increment(value):
    return value + 1


def test_external_mpi_worker_simple_task():
    # Override sys.argv to mimic runtime call
    sys_argv_backup = list(sys.argv)
    sys_path_backup = list(sys.path)
    job1_out = '/tmp/job1_NEW.out'
    job1_err = '/tmp/job1_NEW.err'
    sys.argv = ["test_external_mpi.py", " ".join(['EXECUTE_TASK', '1',
                                                  job1_out,
                                                  job1_err,
                                                  '0', '1', 'true', 'null', 'METHOD', 'test_external_mpi',
                                                  'simple', '0', '1', 'localhost', '1', 'false',
                                                  'None', '0', '0',
                                                  '-', '0', '0'])]
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_path)
    main()
    sys.argv = sys_argv_backup
    sys.path = sys_path_backup
    check_task(job1_out, job1_err)
    os.remove(job1_out)
    os.remove(job1_err)


def test_external_mpi_worker_increment_task():
    # Override sys.argv to mimic runtime call
    sys_argv_backup = list(sys.argv)
    sys_path_backup = list(sys.path)
    job2_out = '/tmp/job2_NEW.out'
    job2_err = '/tmp/job2_NEW.err'
    job2_result = '/tmp/job2.IT'
    sys.argv = ["test_external_mpi.py", " ".join(['EXECUTE_TASK', '2',
                                                  job2_out,
                                                  job2_err,
                                                  '0', '1', 'true', 'null', 'METHOD', 'test_external_mpi',
                                                  'increment', '0', '1', 'localhost', '1', 'false',
                                                  '9', '1', '2', '4', '3', 'null', 'value', 'null',
                                                  '1', '9', '3', '#', '$return_0', 'null',
                                                  job2_result + ':d1v2_1599560599402.IT:false:true:' + job2_result,
                                                  '-', '0', '0'])]
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_path)
    main()
    sys.argv = sys_argv_backup
    sys.path = sys_path_backup
    check_task(job2_out, job2_err)
    os.remove(job2_out)
    os.remove(job2_err)
    os.remove(job2_result)


def check_task(job_out, job_err):
    if os.path.exists(job_err) and os.path.getsize(job_err) > 0:  # noqa
        # Non empty file exists
        raise Exception("An error happened in the task. Please check " + job_err)  # noqa
    with open(job_out, 'r') as f:
        content = f.read()
        if 'ERROR' in content:
            raise Exception("An error happened in the task. Please check " + job_out)  # noqa
        if 'EXCEPTION' in content or 'Exception' in content:
            raise Exception("An exception happened in the task. Please check " + job_out)  # noqa
        if 'End task execution. Status: Ok' not in content:
            raise Exception("The task was supposed to be OK. Please check " + job_out)  # noqa