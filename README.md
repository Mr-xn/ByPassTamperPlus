# ByPassTamperPlus

### **Code By:Tas9er / Assist AI:iFlytek Spark**

*本项目是一个针对SQLMap开发的加强版 Tamper脚本集合（基于Python3.10开发），旨在通过利用特定数据库版本的特性和高级混淆技术，绕过现代Web应用防火墙的防护。*

*This project is an enhanced Tamper script collection developed for SQLMap (based on Python 3.10) that is designed to bypass the protection of modern Web Application Firewall by leveraging the features of specific database versions and advanced obfu*ion techniques.

## 项目简介

*传统的 SQLMap Tamper脚本通常较为通用，容易被 WAF 识别。ByPassTamperPlus 针对 MSSQL、MySQL 和 Oracle 的不同版本（从老旧版本到最新AI版本）进行了深度定制。每个脚本都集成了该版本独有的语法特性、函数和混淆逻辑，最大程度地提高 SQL 注入载荷的存活率。*

*Traditional SQLMap Tamper scripts are usually generic and easily recognized by WAF. ByPassTamperPlus is deeply customized for different versions of MSSQL, MySQL and Oracle, from legacy versions to the latest AI versions. Each script integrates the unique syntax features, functions, and obfu*ion logic of this version to maximize the survival of SQL injection loads.*



## 免责声明

*本工具仅面向具备合法资质的安全研究人员、渗透测试工程师及经明确书面授权的企业/机构内部人员使用，用于授权范围内的网络安全测试、防御能力验证及漏洞研究。严禁任何未经授权的网络攻击、非法入侵、数据窃取或其他违反法律法规的行为。*

*This tool is only used for legally qualified security researchers, penetration test engineers and internal personnel of enterprises/institutions with clear written authorization. It is used for network security testing, defense capability verification and vulnerability research within the scope of authorization. Any unauthorized cyber attacks, illegal intrusions, data theft or other violations of laws and regulations are strictly prohibited.*

*若您未获得目标系统所有者的明确书面许可，或所在司法管辖区未赋予您开展此类活动的法律权限，请勿使用本工具。任何因非法使用导致的直接或间接后果（包括但不限于刑事责任、民事赔偿、行政处罚等），均由使用者自行承担全部责任。*

*Do not use this tool if you do not have express written permission from the owner of the target system or if you are located in a jurisdiction that does not give you legal authority to conduct such activities. Any direct or indirect consequences (including but not limited to criminal liability, civil compensation, administrative penalties, etc.) caused by illegal use shall be fully responsible by the user.*



## 目录结构

项目包含三个主要目录，分别对应三种主流数据库：

*   **MSSQL**: 包含针对 SQL Server 2000 到 2025 的绕过脚本。
*   **MySQL**: 包含针对 MySQL 5.0 到 8.0 的绕过脚本。
*   **Oracle**: 包含针对 Oracle 11g 到 23ai 的绕过脚本。

### MSSQL
涵盖版本: 2000, 2005, 2008, 2012, 2014, 2016, 2017, 2019, 2022, 2025

*   **通用技术**: 大小写随机化、空白符替换、注释分割等。
*   **版本特定**:
    *   **2000**: 利用 `TEXTPTR` 和 `READTEXT` 函数。
    *   **2005+**: 利用 `XML` 路径和 `CTE` (公用表表达式)。
    *   **2016+**: 利用 `JSON` 函数 (`OPENJSON`, `JSON_VALUE`) 进行数据提取和逻辑混淆。
    *   **2019+**: 利用智能查询处理特性和近似计数函数。
    *   **2025 **: 模拟利用 `AI_PREDICT` 和 `VECTOR_DISTANCE` 等 AI 相关函数进行语义绕过。

### MySQL
涵盖版本: 5.0, 5.1, 5.5, 5.6, 5.7, 8.0

*   **通用技术**: 内联注释 (`/*!...*/`)、关键字替换 (`&&`, `||`)、正则替换 (`REGEXP`)等。
*   **版本特定**:
    *   **5.0/5.1**: XML 函数 (`ExtractValue`, `UpdateXML`) 报错注入混淆。
    *   **5.5/5.6**: 时间盲注优化 (`TO_SECONDS` 替代 `SLEEP`)，`GTID` 相关函数混淆。
    *   **5.7**: `JSON` 函数 (`JSON_EXTRACT`, `JSON_OBJECT`) 混淆。
    *   **8.0**: 公用表表达式 (`WITH RECURSIVE`)、窗口函数 (`ROW_NUMBER`)、`TABLE` 语句替代 `SELECT`。

### Oracle
涵盖版本: 11g, 12c, 18c, 19c, 21c, 23ai

*   **通用技术**: 字符串拼接 (`|| CHR(...)`)、标识符双引号包裹、高级空白符噪音等。
*   **版本特定**:
    *   **11g**: `XMLType` 数据提取、`NUMTOYMINTERVAL` 延迟。
    *   **12c**: `JSON_VALUE` 包装、多租户视图 (`V$PDBS`)、私有临时表命名。
    *   **18c/19c**: JSON 对偶视图 (`JSON_SERIALIZE`)、SQL Macros (`LISTAGG`)、多态表函数模拟。
    *   **21c**: 原生 JSON 类型构造、模拟 `DBMS_PYTHON` 调用。
    *   **23ai**: 利用 `AI_SQL_GENERATE` 生成自然语言查询、向量相似度 (`VECTOR_DISTANCE`) 比较。



## 通用性说明

1.**绕过能力非绝对**：受目标WAF的版本迭代频率、规则配置逻辑（涵盖厂商自定义规则、动态规则更新、语义分析算法等）、部署架构（云WAF、硬件WAF、混合防护体系）等多重差异影响，本工具**无法保证100%绕过所有WAF防护系统**。其绕防效果高度依赖目标WAF的实际防护策略，针对规则相对简单、老旧的WAF可实现较高绕过概率，面对具备深度语义分析、AI动态识别能力的先进WAF，绕防效果存在不确定性。

2.**可用性非绝对保障**：本工具目前仍处于持续迭代优化阶段，受限于大规模、多场景、多环境的实测数据积累不足，在部分特定场景下，例如目标应用数据库类型特殊、后端SQL语句结构复杂、存在应用层自定义过滤逻辑等，可能出现Payload变形后与正常SQL语句语法规则冲突的情况，进而导致**正常SQL语句无法正常执行**，甚至可能触发目标系统异常响应，无法确保100%的场景可用性。
