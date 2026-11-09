SHOW pgaudit.role;
GRANT SELECT (salary) ON employees TO auditor;
SELECT name, dept FROM employees;
SELECT name, salary FROM employees WHERE dept = 'IT';
