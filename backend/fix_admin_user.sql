-- SQL script to create or reset admin user
-- Run this in your Supabase SQL Editor

-- Step 1: Check current admin user status (if exists)
SELECT 
    username, 
    email, 
    role, 
    is_active,
    CASE WHEN password_hash IS NOT NULL THEN 'Has password' ELSE 'No password' END as password_status,
    LEFT(password_hash, 60) as hash_preview,
    CASE 
        WHEN password_hash LIKE '$pbkdf2-sha256$%' THEN 'pbkdf2_sha256'
        WHEN password_hash LIKE '$2b$%' OR password_hash LIKE '$2a$%' THEN 'bcrypt'
        ELSE 'unknown'
    END as hash_scheme
FROM users 
WHERE username = 'admin';

-- Step 2: Delete existing admin (if you want to reset)
DELETE FROM users WHERE username = 'admin';

-- Step 3: Insert new admin user with pbkdf2_sha256 password hash for "admin123"
INSERT INTO users (username, email, password_hash, role, is_active)
VALUES (
    'admin',
    'admin@qpaper.ai',
    '$pbkdf2-sha256$29000$0Prfe48xJgRAaM25N0aoFQ$R3GpnL/UVgtmRrmWJlGCyx7D8NKy6ctbD.H9MTFgRck',
    'ADMIN',
    true
);

-- Step 4: Verify the admin user was created correctly
SELECT 
    username, 
    email, 
    role, 
    is_active,
    CASE WHEN password_hash IS NOT NULL THEN 'Has password' ELSE 'No password' END as password_status,
    LEFT(password_hash, 60) as hash_preview
FROM users 
WHERE username = 'admin';
