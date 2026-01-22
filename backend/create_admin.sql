-- SQL script to create or reset admin user
-- Run this in your Supabase SQL Editor

-- First, check if admin exists and delete if needed (optional - uncomment if you want to reset)
-- DELETE FROM users WHERE username = 'admin';

-- Create admin user with pbkdf2_sha256 password hash for "admin123"
-- Note: This hash was generated using passlib with pbkdf2_sha256 scheme
-- If this doesn't work, you'll need to generate a new hash using Python

-- Option 1: Insert new admin (if doesn't exist)
INSERT INTO users (username, email, password_hash, role, is_active)
VALUES (
    'admin',
    'admin@qpaper.ai',
    '$pbkdf2-sha256$29000$Yk1JaS3lHMN4D8FYy1krJQ$IbVuSfKqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJq',  -- This is a placeholder - you need to generate the actual hash
    'ADMIN',
    true
)
ON CONFLICT (username) DO UPDATE
SET 
    password_hash = EXCLUDED.password_hash,
    email = EXCLUDED.email,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;

-- Option 2: If admin already exists, update the password hash
-- UPDATE users 
-- SET password_hash = '$pbkdf2-sha256$29000$Yk1JaS3lHMN4D8FYy1krJQ$IbVuSfKqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJq',
--     is_active = true
-- WHERE username = 'admin';

-- To generate a proper password hash, run this Python code:
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
-- print(pwd_context.hash("admin123"))

