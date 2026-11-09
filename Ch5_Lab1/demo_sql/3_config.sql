CREATE ROLE auditor NOLOGIN;
ALTER SYSTEM SET pgaudit.role = 'auditor';
ALTER SYSTEM SET pgaudit.log = 'ddl';
SELECT pg_reload_conf();
