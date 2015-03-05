import sys
from .command_line import CommandLine


class InstallValidator:
    tests = {
        "xelatex": "xelatex -version",
        "bibtex": "bibtex -version"
    }

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
