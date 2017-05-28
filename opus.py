# -*- coding: utf-8 -*-

# OPUS Document Generator for Computer Engineering Project
# Department of Computer Engineering
# Faculty of Engineering at Sri Racha
# Kasetsart University, Sri Racha Campus.
#
# Licensing Information:
# The OPUS project was started in 2013
# Developed by
#    Vacharapat Mettanant (v1.0.0 2013)
#    Sirisak Lueangsaksri (v2.0.0 2015)
# Maintainance by
#    Sirisak Lueangsaksri (2014-2017)

import sys
import os
import time
from core import OpusHelp, OpusProject, OpusDocument, InstallValidator, Updater


VERSION = "2.3.3"


supported_ext = {
    "project": ".opus.project",
    "document": ".opus"
}


def is_support(filename):
    for doctype in supported_ext:
        if filename.endswith(supported_ext[doctype]):
            return True
    return False


def is_project(filename):
    return filename.endswith(supported_ext["project"])


def run(args):
    validation = InstallValidator.validate()
    if not validation["valid"] or "--validate" in args:
        components = validation["components"]
        for component in components:
            if component == "python":
                if sys.version_info[0] < 3:
                    print(
                        "  %s\t= required version 3 or later" % (component) +
                        " (current version is %s.%s)" % (sys.version_info[:2])
                    )
                else:
                    print(
                        "  %s\t= installed" % (component) +
                        " (current version is %s.%s)" % (
                            sys.version_info[:2]
                        )
                    )
            else:
                print("  %s\t= %s" % (
                    component,
                    "installed" if components[component] else "not installed"
                ))
        return
    InstallValidator.update_updater()
    if "-v" in args or "--version" in args:
        print("OPUS %s" % VERSION)
        return
    for key in ["--help", "-h", "-?"]:
        if key in args:
            args.remove(key)
            OpusHelp.print_help(args)
            return
    debug = False
    for key in ["--debug", "-d"]:
        if key in args:
            args.remove(key)
            debug = True
            break
    for key in ["--update", "-u", "--force-update", "-fu"]:
        if key in args:
            args.remove(key)
            updater = Updater(VERSION, key in ["--force-update", "-fu"])
            updater.update()
            updater.ready_to_update()
            notice = False
            print("Checking for OPUS updates...")
            while not updater.finish():
                if not notice and updater.has_new_update():
                    print("Updating OPUS to v%s..." % (updater.get_version()))
                    notice = True
            if updater.is_failed():
                print(
                    "OPUS update is failed. Process will try again next time."
                )
            return
    projects = []
    files = os.listdir(".")
    for file_name in files:
        if is_project(file_name):
            projects.append(file_name)
    project = None
    if len(args) >= 2 and is_support(args[1]):
        project = args[1]
        args = args[2:]
    elif len(projects) == 1:
        project = projects[0]
        args = args[1:]
    elif len(projects) > 1:
        print("More than one project exists. " +
              "Please specified it like this...")
        print("  python %s <project file>" % (args[0]))
        return
    elif len(projects) == 0:
        print("No project found. Please specified the project file " +
              "or put it in the current location.")
        return
    elif len(args) >= 2:
        print("%s is not OPUS project file" % (args[1]))
        return
    updater = Updater(VERSION)
    if not debug:
        updater.update()
    print("Working with %s" % (project))
    if is_project(project):
        opus_project = OpusProject(project)
        opus_project.compile(args)
    else:
        # TODO (if needed)
        print("OPUS document compilation is not implemented yet.")
        print("Please contact the developer if you want to use this.")
        opus_doc = OpusDocument(project)
        opus_doc.compile(args)
    if not debug:
        start_time = time.time()
        timeout = False
        notice = False
        updater.ready_to_update()
        while not updater.finish():
            if not timeout and time.time() - start_time > 3:
                print("Please wait while OPUS checking for new update...")
                timeout = True
            if not notice and updater.has_new_update():
                print("Updating OPUS to v%s..." % (updater.get_version()))
                notice = True
        if updater.is_failed():
            print("OPUS update is failed. Process will try again next time.")


if __name__ == "__main__":
    run(sys.argv)
