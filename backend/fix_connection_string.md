# Fix Supabase Connection String

Your current connection string has a malformed hostname. Here's how to fix it:

## Current (WRONG):
```
postgresql://postgres.sjngjegkghyfzdiiukhf:TgoFEfZbrRpigIuB@db@aws-1-ap-southeast-1...
```

## Correct Format:
```
postgresql://postgres.sjngjegkghyfzdiiukhf:TgoFEfZbrRpigIuB@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

## Steps to Fix:

1. Open your Supabase Dashboard
2. Go to **Settings → Database → Connection Pooling**
3. Select **Session mode** (not Transaction mode)
4. Copy the **exact** connection string shown
5. It should look like:
   ```
   postgresql://postgres.sjngjegkghyfzdiiukhf:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
6. Update your `backend/.env` file:
   ```env
   DATABASE_URL=postgresql://postgres.sjngjegkghyfzdiiukhf:TgoFEfZbrRpigIuB@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```

## Key Points:
- Remove any `@db@` from the hostname
- Hostname should be: `aws-0-ap-southeast-1.pooler.supabase.com` (or `aws-1-...` depending on your region)
- Port should be `6543` (not `5432`)
- Username format: `postgres.[PROJECT_REF]` (e.g., `postgres.sjngjegkghyfzdiiukhf`)

## After Fixing:
1. Save the `.env` file
2. Restart your backend server
3. Try logging in again

