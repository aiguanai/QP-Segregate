-- Migration: Make password_hash nullable for OAuth users
-- This allows Google OAuth users to have NULL password_hash

-- Check if column is NOT NULL, then make it nullable
DO $$
BEGIN
    -- Check if password_hash is currently NOT NULL
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'password_hash' 
        AND is_nullable = 'NO'
    ) THEN
        -- Make password_hash nullable
        ALTER TABLE users 
        ALTER COLUMN password_hash DROP NOT NULL;
        
        RAISE NOTICE 'Successfully made password_hash nullable';
    ELSE
        RAISE NOTICE 'password_hash is already nullable';
    END IF;
END $$;

