/* Eliminar todas las tablas en Oracle
BEGIN
   FOR rec IN (SELECT table_name FROM user_tables)
   LOOP
      EXECUTE IMMEDIATE 'DROP TABLE ' || rec.table_name || ' CASCADE CONSTRAINTS';
   END LOOP;
END;
/
*/

/* Eliminar todas las tablas en PostgreSQL
DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public')
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || rec.tablename || ' CASCADE';
    END LOOP;
END $$;
*/
