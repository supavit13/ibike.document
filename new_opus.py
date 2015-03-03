import sys
import os
from core import OpusProject, OpusDocument, InstallValidator


VERSION = "2.0.0"


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
    if "-v" in args or "--version" in args:
        print("OPUS %s" % VERSION)
        return
    validation = InstallValidator.validate()
    if not validation["valid"]:
        components = validation["components"]
        for component in components:
            print("  %s\t= %s" % (
                component,
                "installed" if components[component] else "not installed"
            ))
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
    print("Working with %s" % (project))
    print("Args: %s" % (args))
    if is_project(project):
        opus_project = OpusProject(project)
        opus_project.compile(args)
    else:
        opus_doc = OpusDocument(project)
        opus_doc.compile(args)


if __name__ == "__main__":
    run(sys.argv)
