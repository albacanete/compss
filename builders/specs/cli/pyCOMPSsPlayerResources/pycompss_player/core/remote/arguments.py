import sys
import argparse
import pathlib

FORMATTER_CLASS = argparse.ArgumentDefaultsHelpFormatter

def cluster_init_parser():
    """ Parses the sys.argv.

    :returns: All arguments as namespace.
    """
    parser = argparse.ArgumentParser(formatter_class=FORMATTER_CLASS)

    # Parent parser - includes all arguments which are common to all actions
    parent_parser = argparse.ArgumentParser(add_help=False,
                                            formatter_class=FORMATTER_CLASS)
    # Action sub-parser
    subparsers = parser.add_subparsers(dest="action")
    # INIT
    parser_init = subparsers.add_parser("init",
                                        aliases=["i"],
                                        help="Initialize COMPSs within a given cluster node.",
                                        parents=[parent_parser],
                                        formatter_class=FORMATTER_CLASS)

    parser_init.add_argument("-l", "--login",
                             type=str,
                             required=True,
                             help="Login info username@cluster_hostname")

    parser_init.add_argument("-m", "--modules",
                             nargs='*',
                             help="Module list or file to load in cluster")

    return parser_init

def cluster_parser_app():
    parser = argparse.ArgumentParser(formatter_class=FORMATTER_CLASS)

    # Parent parser - includes all arguments which are common to all actions
    parent_parser = argparse.ArgumentParser(add_help=False,
                                            formatter_class=FORMATTER_CLASS)
    # Action sub-parser
    subparsers = parser.add_subparsers(dest="action")

    # APP
    parser_app = subparsers.add_parser("app",
                                        aliases=["a"],
                                        parents=[parent_parser],
                                        formatter_class=FORMATTER_CLASS)

    app_subparsers = parser_app.add_subparsers(dest="app")

    app_deploy_parser = app_subparsers.add_parser("deploy",
                                aliases=["d"],
                                help="Deploy an application to a cluster or remote environment",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    app_deploy_parser.add_argument("app_name",
                             type=str,
                             help="Name of the application")

    app_deploy_parser.add_argument("-l", "--local_dir",
                             default='current directory',
                             type=str,
                             help="Directory from which the files will be copied")

    app_deploy_parser.add_argument("-r", "--remote_dir",
                             type=str,
                             help="Remote destination directory for the local app files")

    app_remove_parser = app_subparsers.add_parser("remove",
                                aliases=["r"],
                                help="Delete one or more deployed applications",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    app_remove_parser.add_argument("app_name",
                             type=str,
                             nargs='+',
                             help="Name of the application")

    app_subparsers.add_parser("list",
                                aliases=["l"],
                                help="List all deployed applications",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    return parser_app

def cluster_parser_job():
    """ Parses the sys.argv.

    :returns: All arguments as namespace.
    """
    parser = argparse.ArgumentParser(formatter_class=FORMATTER_CLASS)

    # Parent parser - includes all arguments which are common to all actions
    parent_parser = argparse.ArgumentParser(add_help=False,
                                            formatter_class=FORMATTER_CLASS)
    # Action sub-parser
    subparsers = parser.add_subparsers(dest="action")

    # JOB
    parser_job = subparsers.add_parser("job",
                                        aliases=["j"],
                                        parents=[parent_parser],
                                        formatter_class=FORMATTER_CLASS)

    job_subparsers = parser_job.add_subparsers(dest="job")

    submit_job_parser = job_subparsers.add_parser("submit",
                                aliases=["sub"],
                                help="Submit a job to a cluster or remote environment",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    submit_job_parser.add_argument("app_name",
                             type=str,
                             help="Name of the application on which to submit the job")

    submit_job_parser.add_argument('rest_args', 
                            nargs=argparse.REMAINDER,   
                            help="Remote enqueue_compss arguments")

    job_subparsers.add_parser("status",
                                aliases=["st"],
                                help="Check status of submitted job",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    cancel_parser = job_subparsers.add_parser("cancel",
                                aliases=["c"],
                                help="Cancel a submitted job",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    cancel_parser.add_argument("job_id",
                             type=str,
                             help="Job ID to cancel")

    job_subparsers.add_parser("list",
                                aliases=["l"],
                                help="List all the submitted jobs",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    history_parser = job_subparsers.add_parser("history",
                                aliases=["h"],
                                help="List all past submitted jobs and their app arguments",
                                parents=[parent_parser],
                                formatter_class=FORMATTER_CLASS)

    history_parser.add_argument("--app",
                             type=str,
                             help="")

    return parser_job