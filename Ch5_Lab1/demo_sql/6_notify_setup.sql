CREATE FUNCTION salary_alert() RETURNS trigger AS $$
BEGIN
  IF NEW.salary > OLD.salary * 1.10 THEN
    PERFORM pg_notify('security_alerts', format('ALERT: %s salary changed %s -> %s by %s', NEW.name, OLD.salary, NEW.salary, current_user));
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_salary_alert AFTER UPDATE OF salary ON employees FOR EACH ROW EXECUTE FUNCTION salary_alert();
