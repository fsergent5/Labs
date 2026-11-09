CREATE ROLE hr_admin LOGIN PASSWORD 'Adm1nPass!';
GRANT CREATE ON SCHEMA public TO hr_admin;
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
ALTER SYSTEM SET pgaudit.log_relation = on;
SELECT pg_reload_conf();
