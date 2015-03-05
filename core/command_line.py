import sys
import subprocess


class CommandLine:
    @staticmethod
    def run(command, cwd=None):
        proc = CommandLine.popen(command, cwd)
        while proc.poll() is None:
            pass
        return proc.poll() == 0

    @staticmethod
    def popen(cmd, cwd=None):
        if sys.platform == "darwin":
            return subprocess.Popen(
                ["/bin/bash", "-l", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                shell=False
            )
        elif sys.platform == "linux":
            return subprocess.Popen(
                ["/bin/bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                shell=False
            )
        else:
            return subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                shell=False
            )
