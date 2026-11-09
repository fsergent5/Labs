SHOW pgaudit.log;
SET ROLE hr_admin;
CREATE TABLE employees (id serial PRIMARY KEY, name text, dept text, salary numeric, owner_name text);
INSERT INTO employees (name, dept, salary, owner_name) VALUES ('Alice Chen','Sales',62000,'alice'), ('Bob Diaz','IT',71000,'bob'), ('Carla Ruiz','HR',58000,'carla');
UPDATE employees SET salary = 75000 WHERE name = 'Bob Diaz';
SELECT name, salary FROM employees;
RESET ROLE;
