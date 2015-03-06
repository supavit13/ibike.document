import re


class Statements:
    prepare = False
    statements = {
        "empty": {
            "pattern": ["^\\s*$"]
        },
        "comment": {
            "pattern": ["%.*"]
        },
        "property": {
            "pattern": [
                "([^\\s\\n():\\|%]+)(\\(([^():\\|]+)\\))?:([^\\n():\\|%]+)" +
                "(\\|([^\\n():\\|%]+)(\\(([^():\\|]+)\\))?:([^\\n():\\|%]+))?",
                re.I
            ],
            "options": {
                1: {"trim": True, "lower": True},
                3: {"trim": True},
                4: {"trim": True},
                6: {"trim": True, "lower": True},
                8: {"trim": True},
                9: {"trim": True}
            },
            "matches": {
                1: "name",
                3: "property",
                4: "value",
                6: "support_name",
                8: "support_property",
                9: "support_value",
            }
        },
        "property_end": {
            "pattern": ["end\\."]
        },
        "keyword_tag": {
            "pattern": ["%<(?!\\-)((\\w+):)?([^<>%-\\.]+)(\\.([^<>%-]+))?>%"],
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
        },
        "template_include": {
            "pattern": ["%<--((\\w+):)?([^<>%-\\.]+)(\\.([^<>%-]+))?-->%"],
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
