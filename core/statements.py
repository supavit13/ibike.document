# -*- coding: utf-8 -*-
import re


class Statements:
    prepare = False
    statements = {
        "empty": {
            "pattern": ["^\\s*$"]
        },
        "comment": {
            "pattern": ["(?<!\\\\)%.*"]
        },
        "basic_style": {
            "pattern": [
                "(?<!\\\\)\\*(.*)\\*|" +
                "(?<!\\\\)_((\\\\{|\\\\}|\\\\_|[^{}_])*)_|" +
                "(?<!\\\\)`(.*?)`|(?<!\\\\)--((\\\\{|\\\\}|-[^-]|[^{}-])*)--"
            ],
            "matches": {
                1: "bold",
                2: "italic",
                4: "code",
                5: "underline"
            }
        },
        "escaped_character": {
            "pattern": [
                "\\\\([-])|(\\\\[_])"
            ],
            "matches": {
                1: "character",
                2: "return"
            }
        },
        "list_item": {
            "pattern": [
                "(?<!\\\\)#(.*)|(\\[\\[\\s*(end|list|ulist)\\s*\\]\\])"
            ],
            "options": {
                1: {"trim": True}
            },
            "matches": {
                1: "text",
                2: "list_command"
            }
        },
        "markup": {
            "pattern": [
                "(?<!\\\\)\\[\\[([^\\|:()\\[\\]]+)(\\s*\\[((\\][^\\]]|" +
                "[^\\]])+)\\])?(\\s*\\(((\\][^\\]]|[^()\\]])*)\\))?" +
                "(\\s*:\\s*((\\][^\\]]|[^\\]\\|])+))?" +
                "(\\s*\\|\\s*((\\][^\\]]|[^\\]])+)?)?\\]\\]"
            ],
            "options": {
                1: {"trim": True, "lower": True},
                3: {"trim": True},
                6: {"trim": True},
                9: {"trim": True},
                12: {"trim": True, "split": "|"}
            },
            "matches": {
                1: "tag",
                3: "format",
                6: "expression",
                9: "value",
                12: "attributes"
            }
        },
        "markup_keyword": {
            "pattern": [
                "((\\w+):)?(([^<>%\\-]+)<=)?([^<>%\\-\\.]+)" +
                "(\\.([^<>%\\-=]+))?(=>([^<>%\\-]+))?"
            ],
            "options": {
                2: {"trim": True, "lower": True},
                4: {"trim": True, "lower": True},
                5: {"trim": True, "lower": True},
                7: {"trim": True, "lower": True, "split": "."},
                9: {"trim": True, "lower": True}
            },
            "matches": {
                2: "type",
                4: "prefix",
                5: "name",
                7: "selector",
                9: "suffix"
            }
        },
        "property": {
            "pattern": [
                "([^\\s\\n():\\|%]+)(\\(([^():\\|]+)\\))?:([^\\n()\\|%]+)" +
                "(\\s*\\|\\s*(([^\\:\\n]+)\\s*\\:\\s*([^:\\n]+)))?",
                re.I
            ],
            "options": {
                1: {"trim": True, "lower": True},
                3: {"trim": True},
                4: {"trim": True},
                6: {"trim": True, "split": "|"}
            },
            "matches": {
                1: "name",
                3: "property",
                4: "value",
                6: "supports"
            }
        },
        "property_end": {
            "pattern": ["end\\."]
        },
        "keyword_tag": {
            "pattern": [
                "%<(?<!\\-)((\\w+):)?(([^<>%\\-]+)<=)?([^<>%\\-\\.]+)" +
                "(\\.([^<>%\\-=]+))?(=>([^<>%\\-]+))?>%"
            ],
            "options": {
                2: {"trim": True, "lower": True},
                4: {"lower": True},
                5: {"trim": True, "lower": True},
                7: {"trim": True, "lower": True, "split": "."},
                9: {"lower": True}
            },
            "matches": {
                2: "type",
                4: "prefix",
                5: "name",
                7: "selector",
                9: "suffix"
            }
        },
        "template_include": {
            "pattern": [
                "%<\\-\\-(([\\w_]+):)?([^<>%\\-\\.]+)(\\.([^<>%\\-]+))?\\-\\->%"
            ],
            "options": {
                2: {"trim": True, "lower": True},
                3: {"trim": True, "lower": True},
                5: {"trim": True, "lower": True, "split": "."}
            },
            "matches": {
                2: "type",
                3: "name",
                5: "selector"
            }
        }
    }

    @staticmethod
    def prepare_statements():
        for statement in Statements.statements:
            Statements.statements[statement]["pattern"] = re.compile(
                *Statements.statements[statement]["pattern"]
            )
        Statements.prepare = True

    @staticmethod
    def get(statement):
        if not Statements.prepare:
            Statements.prepare_statements()
        if statement not in Statements.statements:
            return None
        return Statements.statements[statement]

    @staticmethod
    def process_match(statement, matches):
        if not matches:
            return None
        if "matches" not in statement:
            return matches.group(0)
        else:
            ret_matches = {"matches": matches}
            for match in statement["matches"]:
                match_string = matches.group(match)
                if not match_string:
                    continue
                match_name = statement["matches"][match]
                if "options" in statement and match in statement["options"]:
                    options = statement["options"][match]
                    if "trim" in options and options["trim"]:
                        match_string = match_string.strip()
                    if "lower" in options and options["lower"]:
                        match_string = match_string.lower()
                    if "split" in options:
                        match_string = match_string.split(options["split"])
                ret_matches[match_name] = match_string
            return ret_matches

    @staticmethod
    def parse(statement_type, string, replacer=None):
        statement = Statements.get(statement_type)
        if not statement:
            return None
        if replacer:
            return statement["pattern"].sub(
                lambda m: replacer(Statements.process_match(statement, m)),
                string
            )
        else:
            return Statements.process_match(
                statement, statement["pattern"].search(string)
            )
