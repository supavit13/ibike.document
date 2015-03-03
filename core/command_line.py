import sys
import subprocess


class CommandLine:
    @staticmethod
    def run(command):
        proc = CommandLine.popen(command)
        while proc.poll() is None:
            pass
        return proc.poll() == 0

    @staticmethod
    def popen(cmd):
        if sys.platform == "darwin":
            return subprocess.Popen(
                ["/bin/bash", "-l", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
        elif sys.platform == "linux":
            return subprocess.Popen(
                ["/bin/bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
        else:
            return subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
