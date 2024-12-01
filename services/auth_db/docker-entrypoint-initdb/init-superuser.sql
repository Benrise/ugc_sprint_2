DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'admin'
    ) THEN
        RAISE NOTICE 'Role admin exists, altering to add superuser privileges';
        ALTER ROLE admin WITH SUPERUSER;
    ELSE
        RAISE NOTICE 'Creating role admin with superuser privileges';
        CREATE ROLE admin LOGIN SUPERUSER;
    END IF;
END $$;