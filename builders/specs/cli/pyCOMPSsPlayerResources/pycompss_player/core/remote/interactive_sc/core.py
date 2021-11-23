import os
import sys
import argparse
import subprocess
import re
import time
import signal
import getpass

from pycompss_player.core.remote.interactive_sc.defaults import INTERPRETER
from pycompss_player.core.remote.interactive_sc.defaults import SUBMIT_SCRIPT
from pycompss_player.core.remote.interactive_sc.defaults import STATUS_SCRIPT
from pycompss_player.core.remote.interactive_sc.defaults import INFO_SCRIPT
from pycompss_player.core.remote.interactive_sc.defaults import FIND_SCRIPT
from pycompss_player.core.remote.interactive_sc.defaults import CANCEL_SCRIPT

from pycompss_player.core.remote.interactive_sc.defaults import VERSION
from pycompss_player.core.remote.interactive_sc.defaults import DECODING_FORMAT
from pycompss_player.core.remote.interactive_sc.defaults import SUCCESS_KEYWORD
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_KEYWORD
from pycompss_player.core.remote.interactive_sc.defaults import NOT_RUNNING_KEYWORD
from pycompss_player.core.remote.interactive_sc.defaults import DISABLED_VALUE

from pycompss_player.core.remote.interactive_sc.defaults import LOG_LEVEL_DEBUG
from pycompss_player.core.remote.interactive_sc.defaults import LOG_LEVEL_INFO
from pycompss_player.core.remote.interactive_sc.defaults import LOG_LEVEL_OFF
from pycompss_player.core.remote.interactive_sc.defaults import DEFAULT_VERBOSE
from pycompss_player.core.remote.interactive_sc.defaults import DEFAULT_CONNECTIVITY_CHECK

from pycompss_player.core.remote.interactive_sc.defaults import DEFAULT_PROJECT
from pycompss_player.core.remote.interactive_sc.defaults import DEFAULT_CREDENTIALS

from pycompss_player.core.remote.interactive_sc.defaults import DEFAULT_SSH
from pycompss_player.core.remote.interactive_sc.defaults import DEFAULT_SSHPASS
from pycompss_player.core.remote.interactive_sc.defaults import DEFAULT_SSH_WINDOWS

from pycompss_player.core.remote.interactive_sc.defaults import CONNECTION_URL

from pycompss_player.core.remote.interactive_sc.defaults import INFO_CONNECTION_ESTABLISHED

from pycompss_player.core.remote.interactive_sc.defaults import WARNING_USER_NAME_NOT_PROVIDED
from pycompss_player.core.remote.interactive_sc.defaults import WARNING_NOTEBOOK_NOT_RUNNING
from pycompss_player.core.remote.interactive_sc.defaults import WARNING_NO_BROWSER

from pycompss_player.core.remote.interactive_sc.defaults import ERROR_UNEXPECTED_PARAMETER
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_UNRECOGNIZED_ACTION
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_SESSION_NOT_PROVIDED
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_CONNECTING
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_COMPSS_NOT_DEFINED
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_SUBMITTING_JOB
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_STATUS_JOB
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_INFO_JOB
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_STORAGE_PROPS
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_UNSUPPORTED_STORAGE_SHORTCUT
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_JUPYTER_SERVER
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_BROWSER
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_NO_BROWSER
from pycompss_player.core.remote.interactive_sc.defaults import ERROR_CANCELLING_JOB

from pycompss_player.core.remote.interactive_sc.defaults import is_windows

ALIVE_PROCESSES = []  # Needed for proper cleanup

def __signal_handler(sig, frame):
    """
    Signal handler. Acts when CTRL + C is pressed.
    Checks the global variables to see what needs to be cleaned:
        - Alive processes
        - Cancel running job
    """
    global ALIVE_PROCESSES
    
    if ALIVE_PROCESSES:
        for p in ALIVE_PROCESSES:
            p.kill()
    # # Cancel # Not cancelling here... wait for the user to cancel it explicitly.
    # # If needed, the following information needs to be global
    # global user_name
    # global supercomputer
    # global scripts_path
    # global job_id
    # global verbose
    # if job_id:
    #     if VERBOSE:
    #         print("\t - Cancelling job...")
    #     _cancel_job(user_name, supercomputer, scripts_path, job_id, verbose)
    # else:
    #     __display_warning(WARNING_JOB_CANCELLED)
    print("Finished!")
    # sys.exit(0)


def __display_error(message, return_code=None, stdout=None, stderr=None):
    """
    Display error in a common format.
    :return: None
    """
    # # Hide the client stack trace and show only the prints from remote when fails.
    # if return_code:
    #     print("Return code: " + str(return_code))
    # if stdout:
    #     print("Standard OUTPUT:")
    #     print(stdout)
    if stderr:
        print("Standard ERROR:")
        print(stderr)
    print("ERROR: " + message)
    exit(1)


def __display_warning(message):
    """
    Display warning in a common format.
    :return: None
    """
    print("WARNING: " + message)


def _check_remote_compss(login_info, modules_path):
    """
    Check if COMPSs is available in the remote supercomputer and retrieve the
    its installation path.
    This path is used to infer the submit_jupyter_job.sh path.
    :return: Remote COMPSs installation path.
    """
    cmd = ['which', 'enqueue_compss']
    return_code, stdout, stderr = _command_runner(cmd, login_info, modules_path=modules_path)
    if return_code != 0:
        __display_error(ERROR_CONNECTING, return_code, stdout, stderr)
    if stdout == '':
        __display_error(ERROR_COMPSS_NOT_DEFINED)
    user_scripts_path = os.path.dirname(stdout.strip().split('\n')[-1])
    # Remove the last 3 folders: Runtime/scripts/user to get the real path
    compss_path = '/'.join(user_scripts_path.split('/')[:-3])
    return compss_path


def _infer_scripts_path(compss_path):
    """
    Infer the remote helper scripts path.
    Uses the COMPSs installation path as base and includes the necessary
    folders: Runtime/scripts/system/cli
    :param compss_path: Remote COMPSs installation path.
    :return: Remote helper scripts path.
    """
    # Append the folders to reach teh helper scripts
    scripts_path = compss_path + '/Runtime/scripts/system/cli'
    return scripts_path

def job_status(scripts_path, job_id, login_info, modules_path):
    """
    Checks the status of a job in the supercomputer.
    :param scripts_path: Remote helper scripts path
    :param job_id: Job identifier
    :return: None
    """
    cmd = [INTERPRETER,
           str(scripts_path + '/' + STATUS_SCRIPT),
           job_id]
    return_code, stdout, stderr = _command_runner(cmd, login_info, modules_path=modules_path)
    # if return_code != 0:
    #     __display_error(ERROR_STATUS_JOB, return_code, stdout, stderr)

    # Parse the output for fancy printing
    out = stdout.splitlines()
    if out[-2] == SUCCESS_KEYWORD:
        status = out[-1].split(':')[1]
        return status
    return ERROR_STATUS_JOB

def job_list(scripts_path, login_info, modules_path):
    """
    Checks the list of available jobs in the supercomputer.
    :param scripts_path: Remote helper scripts path
    :return: None
    """
    cmd = [INTERPRETER,
           str(scripts_path + '/' + FIND_SCRIPT)]
    return_code, stdout, stderr = _command_runner(cmd, login_info, modules_path=modules_path)
    if return_code != 0:
        __display_error(ERROR_STATUS_JOB, return_code, stdout, stderr)

    # Parse the output for fancy printing
    out = stdout.splitlines()
    if out[0] == SUCCESS_KEYWORD:
        print("Available notebooks: ")
        for job_id in out[1:]:
            print(job_id)
    else:
        __display_error(ERROR_STATUS_JOB, return_code, stdout, stderr)

def connect_job(scripts_path, job_id, login_info, modules_path, port_forward='8888', web_browser='firefox'):
    """
    Establish the connection with an existing notebook.
    :param scripts_path: Remote helper scripts path
    :param arguments: Arguments received from command line.
    :return: None
    """
    # First register the signal (the connection will be ready until CTRL+C)
    signal.signal(signal.SIGINT, __signal_handler)

    # Second, get information about the job (node and token)
    node = None
    token = None
    
    cmd = [INTERPRETER,
           str(scripts_path + '/' + INFO_SCRIPT),
           job_id]
    return_code, stdout, stderr = _command_runner(cmd, login_info, modules_path=modules_path)
    # if return_code != 0:
    #     __display_error(ERROR_INFO_JOB, return_code, stdout, stderr)

    # Parse the output
    out = stdout.splitlines()
    if NOT_RUNNING_KEYWORD in stdout:
        __display_warning(WARNING_NOTEBOOK_NOT_RUNNING)
        exit(0)
    elif SUCCESS_KEYWORD in stdout:
        for i in out[1:]:
            line = i.split(':')
            if line[0] == 'MASTER':
                node = line[1]
            elif line[0] == 'SERVER':
                try:
                    server_out = ' '.join(line[1:])
                    raw_token = re.search("token=\w*", server_out).group(0)
                    token = raw_token.split('=')[1]
                except AttributeError:
                    __display_error(ERROR_JUPYTER_SERVER)
    else:
        __display_error(ERROR_INFO_JOB, return_code, stdout, stderr)

    cmd = ['-L', '8888:localhost:' + port_forward,
           'ssh', node,
           '-L', port_forward + ':localhost:8888']
    _command_runner(cmd, login_info, blocking=False)

    time.sleep(5)  # Wait 5 seconds

    if web_browser is None:
        print(INFO_CONNECTION_ESTABLISHED)
        print(CONNECTION_URL + token)
    else:
        print("Opening the " + web_browser + " browser with the connection URL.")
        if is_windows():
            cmd = ['cmd', '/c', 'start', web_browser]
        else:
            cmd = [web_browser]
        cmd = cmd + [CONNECTION_URL + token]
        return_code, stdout, stderr = _command_runner(cmd, login_info, remote=False)
        if return_code != 0:
            message = ERROR_BROWSER + '\n\n' \
                      + "Alternatively, please use the following URL to connect to the job.\n" \
                      + CONNECTION_URL + token
            __display_error(message, return_code, stdout, stderr)
        else:
            print(INFO_CONNECTION_ESTABLISHED)
            print(CONNECTION_URL + token)

    # Finally, wait for the CTRL+C signal
    print("Ready to work!")
    print("To force quit: CTRL + C")
    if is_windows():
        while True:
            # Waiting for signal
            try:
                time.sleep(5)
            except IOError:
                pass
    else:
        signal.pause()
    # The signal is captured and everything cleaned and canceled (if needed)


def cancel_job(scripts_path, job_ids, login_info, modules_path):
    """
    Cancel a list of notebook jobs running in the supercomputer.
    :param scripts_path: Path where the remote helper scripts are
    :param job_ids: List of job identifiers
    :return: None
    """
    cmd = [INTERPRETER,
           str(scripts_path + '/' + CANCEL_SCRIPT)] + job_ids
    return_code, stdout, stderr = _command_runner(cmd, login_info, modules_path=modules_path)
    if return_code != 0:
        __display_error(ERROR_CANCELLING_JOB, return_code, stdout, stderr)

    # Parse the output
    out = stdout.splitlines()
    if out[0] == SUCCESS_KEYWORD:
        print("Jobs successfully cancelled.")
    else:
        __display_error(ERROR_CANCELLING_JOB, return_code, stdout, stderr)


def _command_runner(cmd, login_info, modules_path=None, blocking=True, remote=True):
    """
    Run the command defined in the cmd list.
    Decodes the stdout and stderr following the DECODING_FORMAT.
    :param cmd: Command to execute as list.
    :param blocking: blocks until the subprocess finishes. Otherwise,
                     does not wait and appends the process to the global
                     alive processes list
    :param remote: Enable/Disable the execution in the remote supercomputer.
                   By default, prepend the needed SSH command.
                   (Uses the globals SSH, SESSION, USER_NAME and SUPERCOMPUTER).
    :return: return code, stdout, stderr | None if non blocking
    """
    global ALIVE_PROCESSES

    if remote:
        # Prepend the needed ssh command
        if is_windows():
            raise NotImplementedError()
        else:
            cmd = ' '.join(cmd)
            if modules_path:
                cmd = f"'{modules_path};{cmd}'"
            cmd = f"ssh {login_info} {cmd}"

            print(cmd)
    else:
        # Execute the command as requested
        pass

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if blocking:
        stdout, stderr = p.communicate()   # blocks until cmd is done
        stdout = stdout.decode(DECODING_FORMAT)
        stderr = stderr.decode(DECODING_FORMAT)
        return p.returncode, stdout, stderr
    else:
        ALIVE_PROCESSES.append(p)
