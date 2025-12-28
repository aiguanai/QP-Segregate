# Environment Variables Setup Guide

This guide explains how to find and configure each value in your `.env` file.

## 📋 Quick Reference

| Variable | Required? | Local Dev | Cloud Setup |
|----------|-----------|-----------|-------------|
| `DATABASE_URL` | ✅ Yes | Use localhost | Get from Supabase/Cloud DB |
| `MONGODB_URL` | ⚠️ Optional | Use localhost | Get from MongoDB Atlas |
| `REDIS_URL` | ⚠️ Optional | Use localhost | Get from Redis Cloud |
| `JWT_SECRET_KEY` | ✅ Yes | Generate random string | Generate random string |
| `AWS_*` | ⚠️ Optional | Skip if using local storage | Get from AWS Console |
| `PINECONE_API_KEY` | ⚠️ Optional | Skip for basic setup | Get from Pinecone |
| `MATHPIX_API_KEY` | ⚠️ Optional | Skip for basic setup | Get from Mathpix |

---

## 🗄️ Database Configuration

### 1. DATABASE_URL (PostgreSQL)

#### Option A: Local Development (Docker)
If using `docker-compose.yml`, the default values work:
```env
DATABASE_URL=postgresql://qpaper_user:qpaper_password@localhost:5432/qpaper_ai
```

#### Option B: Cloud - Supabase (Recommended - Free Tier)
1. Go to [supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click **"New Project"**
4. Fill in:
   - **Name**: `qpaper-ai` (or any name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
5. Wait 2-3 minutes for project to initialize
6. Go to **Settings** → **Database**
7. Scroll to **Connection string** → **URI**
8. Copy the connection string
9. It looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
10. Replace `[YOUR-PASSWORD]` with your actual password
11. Paste into `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:your-actual-password@db.xxxxx.supabase.co:5432/postgres
   ```

#### Option C: Cloud - Neon (Serverless PostgreSQL)
1. Go to [neon.tech](https://neon.tech)
2. Sign up with GitHub
3. Click **"Create Project"**
4. Choose a name and region
5. Copy the connection string from the dashboard
6. Format: `postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb`

#### Option D: Cloud - Google Cloud SQL
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Cloud SQL API
3. Create SQL instance → PostgreSQL
4. Get connection string from instance details

---

### 2. MONGODB_URL (MongoDB)

#### Option A: Local Development (Docker)
If using `docker-compose.yml`, the default values work:
```env
MONGODB_URL=mongodb://qpaper_user:qpaper_password@localhost:27017/qpaper_ai?authSource=admin
```

#### Option B: Cloud - MongoDB Atlas (Recommended - Free Tier)
1. Go to [cloud.mongodb.com](https://cloud.mongodb.com)
2. Sign up / Log in
3. Click **"Build a Database"**
4. Choose **FREE (M0)** tier
5. Select **Cloud Provider** (AWS recommended) and **Region**
6. Click **"Create"** (takes 3-5 minutes)
7. **Create Database User**:
   - Username: `qpaper_user` (or any username)
   - Password: Create strong password (save it!)
   - Database User Privileges: **Read and write to any database**
8. **Network Access**:
   - Click **"Add IP Address"**
   - For development: Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - For production: Add your server IP only
9. **Get Connection String**:
   - Click **"Connect"** → **"Connect your application"**
   - Driver: **Node.js** (version doesn't matter)
   - Copy the connection string
   - It looks like:
     ```
     mongodb+srv://qpaper_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
10. Replace `<password>` with your actual password
11. Add database name: `?retryWrites=true&w=majority` → `qpaper_ai?retryWrites=true&w=majority`
12. Paste into `.env`:
    ```env
    MONGODB_URL=mongodb+srv://qpaper_user:your-password@cluster0.xxxxx.mongodb.net/qpaper_ai?retryWrites=true&w=majority
    ```

---

### 3. REDIS_URL (Redis)

#### Option A: Local Development (Docker)
If using `docker-compose.yml`, the default values work:
```env
REDIS_URL=redis://localhost:6379
```

#### Option B: Cloud - Redis Cloud (Recommended - Free Tier)
1. Go to [redis.com/redis-enterprise-cloud](https://redis.com/redis-enterprise-cloud/)
2. Sign up / Log in
3. Click **"New Subscription"** → **"Fixed"** (Free tier)
4. Click **"Create Database"**
5. Choose:
   - **Name**: `qpaper-redis`
   - **Region**: Closest to you
   - **Memory**: 30MB (free tier)
6. Click **"Activate"**
7. Wait 1-2 minutes
8. Click on your database
9. Copy the **"Public endpoint"** or **"Endpoint"**
10. Format: `redis://default:password@redis-xxxxx.cloud.redislabs.com:12345`
11. Paste into `.env`:
    ```env
    REDIS_URL=redis://default:your-password@redis-xxxxx.cloud.redislabs.com:12345
    ```

#### Option C: Cloud - Upstash (Alternative Free Tier)
1. Go to [upstash.com](https://upstash.com)
2. Sign up with GitHub
3. Create database → Redis
4. Copy REST URL or Redis URL
5. Format: `redis://default:password@xxxxx.upstash.io:6379`

---

## 🔐 Security Configuration

### 4. JWT_SECRET_KEY

**Required for authentication!** Generate a random secure string.

#### Option A: Generate Online
1. Go to [randomkeygen.com](https://randomkeygen.com)
2. Copy a **CodeIgniter Encryption Keys** (256-bit)
3. Or use: [1password.com/password-generator](https://1password.com/password-generator) (64+ characters)

#### Option B: Generate via Command Line
```powershell
# PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Example:**
```env
JWT_SECRET_KEY=your-super-secure-random-string-at-least-32-characters-long-change-this
```

⚠️ **Important**: Use a different secret key for production!

---

## ☁️ External APIs (Optional)

### 5. AWS S3 Configuration (Optional - for cloud file storage)

Only needed if you want to store files in AWS S3 instead of local storage.

1. Go to [AWS Console](https://console.aws.amazon.com)
2. Sign up / Log in
3. Go to **IAM** → **Users** → **Create User**
4. Enable **Programmatic access**
5. Attach policy: **AmazonS3FullAccess** (or create custom policy)
6. **Create Access Key**:
   - Click **"Create access key"**
   - Choose **"Application running outside AWS"**
   - Copy **Access Key ID** and **Secret Access Key** (shown only once!)
7. **Create S3 Bucket**:
   - Go to **S3** → **Create bucket**
   - Name: `qpaper-ai-storage` (must be globally unique)
   - Region: Choose closest
   - Uncheck **"Block all public access"** (if you need public files)
   - Click **"Create bucket"**

Paste into `.env`:
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET=qpaper-ai-storage
```

---

### 6. PINECONE_API_KEY (Optional - for vector search)

Only needed for advanced semantic search features.

1. Go to [pinecone.io](https://www.pinecone.io)
2. Sign up / Log in
3. Go to **API Keys** section
4. Click **"Create API Key"**
5. Copy the API key
6. Paste into `.env`:
   ```env
   PINECONE_API_KEY=your-pinecone-api-key-here
   ```

---

### 7. MATHPIX_API_KEY (Optional - for math OCR)

Only needed for extracting mathematical equations from PDFs.

1. Go to [mathpix.com](https://mathpix.com)
2. Sign up / Log in
3. Go to **Dashboard** → **API Credentials**
4. Copy **App ID** and **App Key** (or just the API key if available)
5. Paste into `.env`:
   ```env
   MATHPIX_API_KEY=your-mathpix-api-key-here
   ```

---

## 📁 File Storage (Usually No Changes Needed)

These are local file paths. Only change if you want custom locations:

```env
UPLOAD_DIR=storage/papers          # Where PDFs are stored
TEMP_UPLOAD_DIR=tmp/uploads        # Temporary uploads
PAGE_IMAGES_DIR=storage/page_images # Extracted page images
```

---

## ⚙️ Processing Configuration (Optional - Defaults Usually Fine)

These control AI/ML processing thresholds. Defaults work for most cases:

```env
OCR_CONFIDENCE_THRESHOLD=0.4              # OCR confidence (0.0-1.0)
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7    # Classification confidence
SIMILARITY_THRESHOLD=0.85                  # Question similarity threshold
TEMP_UPLOAD_EXPIRE_HOURS=24                # Temp file cleanup time
```

---

## 📄 Pagination (Optional - Defaults Usually Fine)

```env
DEFAULT_PAGE_SIZE=20    # Default items per page
MAX_PAGE_SIZE=100       # Maximum items per page
```

---

## ✅ Quick Setup Checklist

### Minimum Required (Local Development)
- [ ] `DATABASE_URL` - Use localhost (works with Docker)
- [ ] `JWT_SECRET_KEY` - Generate random string

### Recommended (Cloud Setup)
- [ ] `DATABASE_URL` - Get from Supabase
- [ ] `MONGODB_URL` - Get from MongoDB Atlas
- [ ] `REDIS_URL` - Get from Redis Cloud
- [ ] `JWT_SECRET_KEY` - Generate random string

### Optional (Advanced Features)
- [ ] `AWS_*` - Only if using S3 storage
- [ ] `PINECONE_API_KEY` - Only for vector search
- [ ] `MATHPIX_API_KEY` - Only for math OCR

---

## 🧪 Testing Your Configuration

After setting up your `.env` file, test connections:

```powershell
cd backend
python test_connections.py
```

This will verify:
- ✅ PostgreSQL connection
- ✅ MongoDB connection
- ✅ Redis connection

---

## 🆘 Troubleshooting

### "Connection refused" or "Can't connect"
- Check if database service is running (for local)
- Verify connection string format
- Check firewall/network access (for cloud)
- Ensure IP is whitelisted (MongoDB Atlas)

### "Authentication failed"
- Double-check username and password
- Make sure special characters in password are URL-encoded
- Verify database user has correct permissions

### "Database not found"
- Create the database first (for PostgreSQL)
- For MongoDB, database is created automatically on first use

---

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com)
- [Redis Cloud Documentation](https://redis.com/redis-enterprise-cloud/documentation/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

