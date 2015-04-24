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
        self.output_dir = "output"

    def clean(self):
        bbl_file_name = self.project["output_name"]+".bbl"
        if not self.keep:
            print("Cleaning...")
            if os.path.exists(bbl_file_name):
                os.remove(bbl_file_name)
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
            if os.path.exists(self.tex_file):
                os.remove(self.tex_file)
            if os.path.exists(self.ref_file):
                os.remove(self.ref_file)

    def run(self, verbose=False):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        xelatex_command = [
            "xelatex",
            "-output-directory=%s" % (self.output_dir),
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-no-pdf",
            self.project["output_name"]
        ]
        bibtex_command = [
            "bibtex",
            "%s/%s" % (self.output_dir, self.project["output_name"])
        ]
        print("Generating auxilary files...")
        if not CommandLine.run(
            " ".join(xelatex_command),
            cwd=os.path.abspath(""),
            verbose=verbose
        ):
            print("Failed. Add \"--verbose\" flag to show error messages.")
            return
        bbl_file_name = self.project["output_name"]+".bbl"
        bbl_file = os.path.join(self.output_dir, bbl_file_name)
        if self.project["expander"]["citations"]:
            print("Linking references...")
            if not CommandLine.run(
                " ".join(bibtex_command),
                cwd=os.path.abspath(""),
                verbose=verbose
            ):
                print("Failed. Add \"--verbose\" flag to show error messages.")
                return
            if os.path.exists(bbl_file_name):
                os.remove(bbl_file_name)
            if os.path.exists(bbl_file):
                shutil.copy(bbl_file, bbl_file_name)
        print("Regenerating auxilary files...")
        if not CommandLine.run(
            " ".join(xelatex_command),
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
        pdf_path = os.path.join(self.output_dir, pdf_file_name)
        notice = False
        while os.path.exists(pdf_file_name):
            try:
                os.remove(pdf_file_name)
            except IOError:
                if not notice:
                    print("Please close the \"%s\" file..." % (pdf_file_name))
                    notice = True
        if os.path.exists(pdf_path):
            os.rename(pdf_path, pdf_file_name)
