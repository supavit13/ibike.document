class OpusHelp:
    @staticmethod
    def print_help(args=None):
        args = args or []
        if len(args) < 1:
            args.append("opus.py")
        print(
            "usage:" +
            " python " + args[0] +
            " [project file or document file] [output type] [flag] ..."
        )
        print("where flags are...")
        flags = {
            "--debug | -d": "enable debugging mode",
            "--force-update | -fu": "force update opus",
            "--help | -h | -?": "print this help messages",
            "--keep | -k": "keep all output files",
            "--update | -u": "check for opus updates",
            "--version | -v": "print opus version",
            "--verbose | -V": "print all command line output",
            "--validate": "print install validation summary"
        }
        for key in flags:
            print(key)
            print("    " + flags[key])
