# -*- coding: utf-8 -*-
import sys
import subprocess
try:
    from subprocess import DEVNULL
except ImportError:
    import os
    DEVNULL = open(os.devnull, "wb")


class CommandLine:
    @staticmethod
    def run(command, cwd=None, verbose=False):
        proc = CommandLine.popen(command, cwd, verbose)
        while proc.poll() is None:
            pass
        return proc.poll() == 0

    @staticmethod
    def popen(cmd, cwd=None, verbose=False):
        if sys.platform == "darwin":
            return subprocess.Popen(
                ["/bin/bash", "-l", "-c", cmd],
                stdout=None if verbose else DEVNULL,
                stderr=None if verbose else DEVNULL,
                cwd=cwd,
                shell=False
            )
        elif sys.platform == "linux":
            return subprocess.Popen(
                ["/bin/bash", "-c", cmd],
                stdout=None if verbose else DEVNULL,
                stderr=None if verbose else DEVNULL,
                cwd=cwd,
                shell=False
            )
        else:
            return subprocess.Popen(
                cmd,
                stdout=None if verbose else DEVNULL,
                stderr=None if verbose else DEVNULL,
                cwd=cwd,
                shell=True
            )
