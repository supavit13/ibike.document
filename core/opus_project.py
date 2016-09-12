# -*- coding: utf-8 -*-
from .logger import Logger
from .statements import Statements
from .template_expander import TemplateExpander
from .latex_compiler import LatexCompiler


class OpusProject:
    def __init__(self, filename):
        self.project_file = open(filename, "r", encoding="utf8")

    def validate_project(self, project):
        missing = []
        properties = {
            "output_language": "Output Language",
            "output_name": "Output File Name",
            "output_type": "Output Type",
            "name": "Project Name (TH & EN)",
            "authors": "Project Authors (TH & EN)",
            "advisor": "Project Advisor (TH & EN)",
            "committee1": "Project Committee #1",
            "committee2": "Project Committee #2",
            "headdepartment": "Head of Department",
            "abstract": "Abstract (TH & EN)",
            "acknowledgement": "Acknowledgement",
            "proposal": "Proposal Content",
            "reference": "Reference",
            "chapters": "Project Contents (Chapters)"
        }
        for prop in properties:
            if prop not in project:
                missing.append(properties[prop])
        if len(missing) == 0:
            if len(project["authors"]) == 0:
                missing.append(
                    "Authors must have at least 1 person"
                )
            else:
                for author in project["authors"]:
                    if len(author) < 2:
                        missing.append(
                            "Authors must have both Thai and English name" +
                            " for every person"
                        )
                        break
            if len(properties["chapters"]) == 0:
                missing.append(
                    "Chapters must have at least 1 chapter"
                )
            if len(properties["name"]) < 2:
                missing.append(
                    "Project Name must have both Thai and English name"
                )
            if len(properties["advisor"]) < 2:
                missing.append(
                    "Project Advisor must have both Thai and English name"
                )
            else:
                for lang in ["th", "en"]:
                    language = "Thai" if lang == "th" else "English"
                    if lang not in project["advisor"]:
                        missing.append(
                            "Project Advisor must have %s name" % (language)
                        )
                        continue
                    if "name" not in project["advisor"][lang] or (
                        "degree" not in project["advisor"][lang] and
                        "prefix" not in project["advisor"][lang]
                    ):
                        missing.append(
                            "Project Advisor must have" +
                            " name and degree or prefix in %s" % (language)
                        )
            if len(properties["abstract"]) < 2:
                missing.append(
                    "Abstract must have both Thai and English version"
                )
        missing.sort()
        return missing

    def parse_properties(self, prop):
        properties = {}
        if "supports" in prop:
            for support in prop["supports"]:
                comp = [c.strip() for c in support.split(":")]
                if len(comp) > 1:
                    properties[comp[0]] = comp[1]
                else:
                    properties[comp[0]] = True
        return properties

    def set_property(self, project, prop):
        properties = self.parse_properties(prop)
        if prop["name"] == "document":
            if "property" in prop:
                project["output_name"] = prop["property"]
            project["output_type"] = prop["value"].lower()
        elif prop["name"] == "language":
            project["output_language"] = prop["value"].lower()
        elif prop["name"] in ["chapter", "appendix"]:
            field = "chapters" if prop["name"] == "chapter" else "appendices"
            if field not in project:
                project[field] = []
            data = {}
            if "property" in prop:
                data["name"] = prop["property"]
            data["file"] = prop["value"]
            project[field].append(data)
        elif (prop["name"].startswith("name-") or
                prop["name"].startswith("abstract")):
            field = "name" if prop["name"].startswith("name-") else "abstract"
            if field not in project:
                project[field] = {}
            for lang in ["en", "th"]:
                if prop["name"].endswith(lang):
                    project[field][lang] = prop["value"]
        elif prop["name"].startswith("advisor-"):
            if "advisor" not in project:
                project["advisor"] = {}
            for lang in ["en", "th"]:
                if not prop["name"].endswith(lang):
                    continue
                if lang not in project["advisor"]:
                    project["advisor"][lang] = {}
                project["advisor"][lang]["name"] = prop["value"]
                if "degree" in properties:
                    project["advisor"][lang]["degree"] = properties["degree"]
                if "prefix" in properties:
                    project["advisor"][lang]["prefix"] = properties["prefix"]
                else:
                    project["advisor"][lang]["prefix"] = (
                        "อาจารย์" if lang == "th" else ""
                    )
        elif prop["name"].startswith("author-"):
            if "authors" not in project:
                project["authors"] = []
            for lang in ["en", "th"]:
                if not prop["name"].endswith(lang):
                    continue
                add = False
                for author in project["authors"]:
                    if lang not in author:
                        author[lang] = prop["value"]
                        add = True
                        break
                if not add:
                    project["authors"].append({
                        lang: prop["value"]
                    })
        else:
            professor_fields = ["committee1", "committee2", "headdepartment"]
            fields = ["acknowledgement", "proposal", "reference"]
            for field in professor_fields:
                if prop["name"].startswith(field):
                    if field not in project:
                        project[field] = {}
                    project[field]["name"] = prop["value"]
                    if "prefix" in properties:
                        project[field]["prefix"] = properties["prefix"]
                    else:
                        project[field]["prefix"] = "อาจารย์"
            for field in fields:
                if not prop["name"].startswith(field):
                    continue
                project[field] = prop["value"]

    def parse_project(self, args):
        lines = self.project_file.readlines()
        project_info = {}
        line_no = 0
        for line in lines:
            line = Statements.parse("comment", line, replacer=lambda m: "")
            line_no += 1
            if Statements.parse("empty", line):
                continue
            prop = Statements.parse("property", line)
            prop_end = Statements.parse("property_end", line)
            if not prop and not prop_end:
                Logger.error(
                    self.project_file, line_no,
                    "InvalidProperty", "Invalid property"
                )
                return (None, None, None)
            if prop_end:
                break
            if prop:
                if "name" not in prop or "value" not in prop:
                    Logger.error(
                        self.project_file, line_no,
                        "InvalidProperty", "Property did not have name or value"
                    )
                    return (None, None, None)
                self.set_property(project_info, prop)
        if len(args) > 0:
            project_info["output_type"] = args[0].lower()
        validation = self.validate_project(project_info)
        if len(validation) > 0:
            print("Error! Following project properties are missing...")
            for miss in validation:
                print("  - %s" % (miss))
            return (None, None, None)
        print("Compiling project as %s..." % (project_info["output_type"]))
        expander = TemplateExpander(project_info)
        expander.expand()
        return expander.close()

    def compile(self, args):
        verbose = False
        keep = False
        for key in ["--verbose", "-V"]:
            if key in args:
                verbose = True
                args.remove(key)
                break
        for key in ["--keep", "-k"]:
            if key in args:
                keep = True
                args.remove(key)
                break
        project_info, tex_file, ref_file = self.parse_project(args)
        if not tex_file or not ref_file:
            return
        compiler = LatexCompiler(project_info, tex_file, ref_file, keep)
        compiler.run(verbose)
        compiler.clean()
