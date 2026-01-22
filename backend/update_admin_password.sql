-- Alternative: Just update the password if admin exists
-- Run this if the admin user already exists

UPDATE users 
SET 
    password_hash = '$pbkdf2-sha256$29000$0Prfe48xJgRAaM25N0aoFQ$R3GpnL/UVgtmRrmWJlGCyx7D8NKy6ctbD.H9MTFgRck',
    email = 'admin@qpaper.ai',
    role = 'ADMIN',
    is_active = true
WHERE username = 'admin';

-- Check if update worked
SELECT 
    username, 
    email, 
    role, 
    is_active,
    CASE WHEN password_hash IS NOT NULL THEN 'Has password' ELSE 'No password' END as password_status
FROM users 
WHERE username = 'admin';

