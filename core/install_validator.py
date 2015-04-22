# -*- coding: utf-8 -*-
import sys
import os
from .command_line import CommandLine


class InstallValidator:
    tests = {
        "xelatex": "xelatex -version",
        "bibtex": "bibtex -version"
    }

    @staticmethod
    def update_updater():
        if os.path.exists("core/updater_new.py"):
            print("Updating the OPUS updater...")
            os.remove("core/updater.py")
            os.rename("core/updater_new.py", "core/updater.py")

    @staticmethod
    def validate():
        validation = {
            "components": {}
        }
        validation["valid"] = sys.version_info.major >= 3
        validation["components"]["python"] = validation["valid"]
        for test in InstallValidator.tests:
            validation["components"][test] = CommandLine.run(
                InstallValidator.tests[test]
            )
            if not validation["components"][test]:
                validation["valid"] = False
        return validation
