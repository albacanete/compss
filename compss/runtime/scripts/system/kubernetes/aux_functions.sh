#!/bin/bash

function ERROR {
    echo -e "\\e[91m [  RUNCOMPSS-K8S  ]: [  ERROR  ]: $1 \\e[0m" 
}

function ECHO {
    echo -e "\\e[32m [  RUNCOMPSS-K8S  ]: $1 \\e[0m"
}

function ASSERT {
    if [ $? -ne 0 ]; then
    	echo
	    ERROR "$1"	
	    echo
	    exit 1
    fi
}
