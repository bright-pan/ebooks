import os, sys
import shlex, subprocess
import popen2
from subprocess import call
 

def start_service(service):
    try:
        retcode = subprocess.call(["sudo", "service", service, "start"])
        if retcode < 0:
            print >> sys.stderr, "Unable to start %s" % service
        elif retcode == 0:
            print >> sys.stdout, "%s started" % service
        else:
            print >> sys.stderr, "%s already started" % service
    except OSError, e:
        print >> sys.stderr, "%s start failed:" % service, e


def stop_service(service):
    try:
        retcode = subprocess.call(["sudo", "service", service, "stop"])
        if retcode < 0:
            print >> sys.stderr, "Unable to stop %s" % service
        elif retcode == 0:
            print >> sys.stdout, "%s stopped" % service
        else:
            print >> sys.stderr, "%s already stopped" % service
    except OSError, e:
        print >> sys.stderr, "%s stop failed:" % service, e


def restart_service(service):
    try:
        stop_service(service)
        start_service(service)
    except OSError, e:
        print >> sys.stderr, "%s restart failed:" % service, e


def kill_service(service):
    try:
        retcode = subprocess.call(["sudo", "killall", service])
        if retcode < 0:
            print >> sys.stderr, "Unable to kill %s" % service
        elif retcode == 0:
            print >> sys.stdout, "%s killed" % service
        else:
            print >> sys.stderr, "%s already dead" % service
    except OSError, e:
        print >> sys.stderr, "%s killall failed:" % service, e