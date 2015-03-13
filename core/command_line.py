# -*- coding: utf-8 -*-
import sys
import subprocess


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
                stdout=None if verbose else subprocess.PIPE,
                stderr=None if verbose else subprocess.PIPE,
                cwd=cwd,
                shell=False
            )
        elif sys.platform == "linux":
            return subprocess.Popen(
                ["/bin/bash", "-c", cmd],
                stdout=None if verbose else subprocess.PIPE,
                stderr=None if verbose else subprocess.PIPE,
                cwd=cwd,
                shell=False
            )
        else:
            return subprocess.Popen(
                cmd,
                stdout=None if verbose else subprocess.PIPE,
                stderr=None if verbose else subprocess.PIPE,
                cwd=cwd,
                shell=False
            )
