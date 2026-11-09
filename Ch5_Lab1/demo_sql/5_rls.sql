CREATE ROLE alice LOGIN; CREATE ROLE bob LOGIN;
GRANT SELECT ON employees TO alice, bob;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
CREATE POLICY own_row ON employees FOR SELECT USING (owner_name = current_user);
SET ROLE alice;
SELECT name, dept, salary FROM employees;
SET ROLE bob;
SELECT name, dept, salary FROM employees;
RESET ROLE;
