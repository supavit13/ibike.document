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
        "source_tag": {
            "pattern": ["%<(\\w+)>%"],
            "options": {
                1: {"trim": True, "lower": True},
            },
            "matches": {
                1: "name"
            }
        },
        "template_tag": {
            "pattern": ["%<--(\\w+)-->%"],
            "options": {
                1: {"trim": True, "lower": True},
            },
            "matches": {
                1: "name"
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
        return Statements.statements[statement]

    @staticmethod
    def parse(statement_type, string, replacement=None):
        statement = Statements.get(statement_type)
        matches = statement["pattern"].search(string)
        if not matches:
            return None
        if "matches" not in statement:
            return matches.group(0)
        else:
            ret_matches = {}
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
                ret_matches[match_name] = match_string
            return ret_matches
