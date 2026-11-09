\conninfo
SELECT pid, ssl, version, cipher, bits FROM pg_stat_ssl WHERE pid = pg_backend_pid();
