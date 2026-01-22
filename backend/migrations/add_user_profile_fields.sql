-- SQL script to add profile_picture_url and display_name columns to users table
-- Run this in your Supabase SQL Editor

-- Add profile_picture_url column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_picture_url VARCHAR(500);

-- Add display_name column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS display_name VARCHAR(100);

-- Verify the columns were added
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'users' 
  AND column_name IN ('profile_picture_url', 'display_name');

