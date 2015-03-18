# -*- coding: utf-8 -*-
import os
import shutil
from .command_line import CommandLine


class LatexCompiler:
    def __init__(self, project, tex_file, ref_file, keep=False):
        self.keep = keep
        self.project = project
        self.tex_file = tex_file
        self.ref_file = ref_file

    def run(self, verbose=False):
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        xelatex_command = [
            "xelatex",
            "-output-directory=%s" % (output_dir),
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-no-pdf",
            self.project["output_name"]
        ]
        bibtex_command = [
            "bibtex",
            "%s/%s" % (output_dir, self.project["output_name"])
        ]
        print("Generating auxilary files...")
        if not CommandLine.run(
            " ".join(xelatex_command),
            cwd=os.path.abspath(""),
            verbose=verbose
        ):
            print("Failed. Add \"--verbose\" flag to show error messages.")
            return
        if self.project["expander"]["citations"]:
            print("Linking references...")
            if not CommandLine.run(
                " ".join(bibtex_command),
                cwd=os.path.abspath(""),
                verbose=verbose
            ):
                print("Failed. Add \"--verbose\" flag to show error messages.")
                return
        xelatex_command.remove("-no-pdf")
        print("Generating PDF file...")
        if not CommandLine.run(
            " ".join(xelatex_command),
            cwd=os.path.abspath(""),
            verbose=verbose
        ):
            print("Failed. Add \"--verbose\" flag to show error messages.")
            return
        pdf_file_name = self.project["output_name"]+".pdf"
        pdf_path = os.path.join(output_dir, pdf_file_name)
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)
        if os.path.exists(pdf_path):
            os.rename(pdf_path, pdf_file_name)
        if not self.keep:
            print("Cleaning...")
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            if os.path.exists(self.tex_file):
                os.remove(self.tex_file)
            if os.path.exists(self.ref_file):
                os.remove(self.ref_file)
