---
title: "impacket-mssqlclient"
---
#### MS SQL - Enumeration cheat sheet
<!--more-->
---
#### 001: Version

```sql
SELECT @@version;
```

---
#### 002: Databases

Current database
```sql
SELECT DB_NAME();
```

Available databases
```sql
SELECT name FROM sys.databases;
```

Information on available databases
```sql
SELECT name, database_id, create_date FROM sys.databases;
```

Use a database
```sql
USE <database_name>
```

---
#### 003: Tables

Available tables in current database
```sql
SELECT name FROM sys.tables;
```

View table contents
```sql
SELECT * FROM <table_name>
```

---
#### 004: Users

Current user
```sql
SELECT current_user;
```

System user
```sql
SELECT system_user;
```

Available users
```sql
SELECT name FROM sys.sysusers;
```

List login users
```sql
SELECT loginname FROM syslogins;
```

System admin users
```sql
SELECT name FROM master.sys.server_principals WHERE IS_SRVROLEMEMBER('sysadmin', name) = 1;
```

Available users to impersonate
```bash
enum_impersonate
```

Switch user
```sql
EXECUTE AS LOGIN = '<user>';

--- OR ---

EXECUTE AS USER = '<user>';
```

---




