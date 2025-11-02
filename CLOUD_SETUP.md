# QPaper AI - Cloud Database Setup Guide

This guide will help you configure QPaper AI to use cloud-based databases instead of local ones.

## Supported Cloud Databases

### PostgreSQL Options
- **AWS RDS PostgreSQL**
- **Google Cloud SQL**
- **Azure Database for PostgreSQL**
- **Supabase**
- **PlanetScale**
- **Neon**

### MongoDB Options
- **MongoDB Atlas**
- **AWS DocumentDB**
- **Azure Cosmos DB**

### Redis Options
- **AWS ElastiCache**
- **Google Cloud Memorystore**
- **Azure Cache for Redis**
- **Redis Cloud**
- **Upstash**

## Configuration Examples

### 1. AWS RDS + MongoDB Atlas + ElastiCache

```env
# PostgreSQL (AWS RDS)
DATABASE_URL=postgresql://username:password@your-rds-endpoint.amazonaws.com:5432/qpaper_ai

# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai?retryWrites=true&w=majority

# Redis (AWS ElastiCache)
REDIS_URL=redis://your-elasticache-endpoint.cache.amazonaws.com:6379

# AWS S3 for file storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
```

### 2. Supabase + MongoDB Atlas + Redis Cloud

```env
# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai?retryWrites=true&w=majority

# Redis Cloud
REDIS_URL=redis://username:password@your-redis-cloud-endpoint:port

# Cloud storage
UPLOAD_DIR=s3://your-bucket/papers
```

### 3. Google Cloud Setup

```env
# Cloud SQL PostgreSQL
DATABASE_URL=postgresql://username:password@your-instance-ip:5432/qpaper_ai

# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai?retryWrites=true&w=majority

# Cloud Memorystore Redis
REDIS_URL=redis://your-memorystore-ip:6379

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_BUCKET=your-bucket-name
```

## Step-by-Step Setup

### Option 1: AWS Setup

#### 1. Create AWS RDS PostgreSQL
```bash
# Using AWS CLI
aws rds create-db-instance \
    --db-instance-identifier qpaper-postgres \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username qpaper_user \
    --master-user-password your-secure-password \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-your-security-group
```

#### 2. Create MongoDB Atlas Cluster
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a new cluster
3. Set up database user
4. Configure network access (0.0.0.0/0 for development)
5. Get connection string

#### 3. Create ElastiCache Redis
```bash
# Using AWS CLI
aws elasticache create-cache-cluster \
    --cache-cluster-id qpaper-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

#### 4. Create S3 Bucket
```bash
aws s3 mb s3://your-qpaper-bucket
aws s3api put-bucket-cors --bucket your-qpaper-bucket --cors-configuration file://cors.json
```

### Option 2: Supabase + MongoDB Atlas

#### 1. Create Supabase Project
1. Go to [Supabase](https://supabase.com)
2. Create new project
3. Get database URL from Settings > Database
4. Note the connection string format

#### 2. Setup MongoDB Atlas
1. Create cluster on MongoDB Atlas
2. Create database user
3. Whitelist IP addresses
4. Get connection string

#### 3. Setup Redis Cloud
1. Go to [Redis Cloud](https://redis.com/redis-enterprise-cloud/)
2. Create database
3. Get connection details

### Option 3: Google Cloud Setup

#### 1. Create Cloud SQL Instance
```bash
# Using gcloud CLI
gcloud sql instances create qpaper-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=your-secure-password
```

#### 2. Create Cloud Memorystore
```bash
gcloud redis instances create qpaper-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_6_x
```

## Updated Docker Compose for Cloud

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      # Cloud database URLs
      - DATABASE_URL=${CLOUD_DATABASE_URL}
      - MONGODB_URL=${CLOUD_MONGODB_URL}
      - REDIS_URL=${CLOUD_REDIS_URL}
      
      # Cloud storage
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_S3_BUCKET=${AWS_S3_BUCKET}
      
      # Other settings
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
    volumes:
      - ./storage:/app/storage
    depends_on: []

  celery_worker:
    build: ./backend
    environment:
      - DATABASE_URL=${CLOUD_DATABASE_URL}
      - MONGODB_URL=${CLOUD_MONGODB_URL}
      - REDIS_URL=${CLOUD_REDIS_URL}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_S3_BUCKET=${AWS_S3_BUCKET}
    volumes:
      - ./storage:/app/storage

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
```

## Environment Variables for Cloud

Create a `.env` file with your cloud database URLs:

```env
# Cloud Database URLs
CLOUD_DATABASE_URL=postgresql://username:password@your-cloud-postgres:5432/qpaper_ai
CLOUD_MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai
CLOUD_REDIS_URL=redis://username:password@your-cloud-redis:6379

# Cloud Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret

# External APIs
PINECONE_API_KEY=your-pinecone-key
MATHPIX_API_KEY=your-mathpix-key
```

## Database Migration Script

Create a migration script to set up your cloud databases:

```python
# migrate_to_cloud.py
import os
from sqlalchemy import create_engine, text
from app.core.database import Base
from app.models import *

def migrate_to_cloud():
    """Migrate database schema to cloud database"""
    
    # Get cloud database URL
    cloud_db_url = os.getenv('CLOUD_DATABASE_URL')
    if not cloud_db_url:
        print("❌ CLOUD_DATABASE_URL not set")
        return
    
    # Create engine
    engine = create_engine(cloud_db_url)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connected to cloud database")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema created successfully")
        
        # Create initial data
        create_initial_data(engine)
        print("✅ Initial data created")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

def create_initial_data(engine):
    """Create initial data in cloud database"""
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create admin user
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_user = User(
            username="admin",
            email="admin@qpaper.ai",
            password_hash=pwd_context.hash("admin123"),
            role="ADMIN"
        )
        session.add(admin_user)
        
        # Create sample courses
        courses = [
            Course(course_code="CS301", course_name="Database Management Systems", credits=4, course_type="CORE"),
            Course(course_code="CS302", course_name="Computer Networks", credits=4, course_type="CORE"),
            Course(course_code="MA201", course_name="Mathematics", credits=3, course_type="CORE"),
        ]
        
        for course in courses:
            session.add(course)
        
        session.commit()
        print("✅ Initial data created successfully")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Failed to create initial data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    migrate_to_cloud()
```

## Cloud Storage Configuration

### AWS S3 Setup

```python
# backend/app/core/cloud_storage.py
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.AWS_S3_BUCKET
    
    def upload_file(self, file_path: str, s3_key: str):
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        except ClientError as e:
            raise Exception(f"S3 upload failed: {e}")
    
    def download_file(self, s3_key: str, local_path: str):
        """Download file from S3"""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
        except ClientError as e:
            raise Exception(f"S3 download failed: {e}")
    
    def delete_file(self, s3_key: str):
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
        except ClientError as e:
            raise Exception(f"S3 delete failed: {e}")
```

### Google Cloud Storage Setup

```python
# backend/app/core/gcs_storage.py
from google.cloud import storage
from app.core.config import settings

class GCSStorage:
    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = settings.GOOGLE_CLOUD_BUCKET
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload_file(self, file_path: str, gcs_key: str):
        """Upload file to GCS"""
        blob = self.bucket.blob(gcs_key)
        blob.upload_from_filename(file_path)
        return f"https://storage.googleapis.com/{self.bucket_name}/{gcs_key}"
```

## Deployment Options

### 1. AWS ECS/Fargate
```yaml
# ecs-task-definition.json
{
  "family": "qpaper-ai",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-ecr-repo/qpaper-backend:latest",
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "MONGODB_URL", "value": "mongodb+srv://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ]
    }
  ]
}
```

### 2. Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/qpaper-ai', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/qpaper-ai']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'qpaper-ai', '--image', 'gcr.io/$PROJECT_ID/qpaper-ai', '--platform', 'managed', '--region', 'us-central1']
```

### 3. Azure Container Instances
```yaml
# azure-deploy.yaml
apiVersion: 2018-10-01
location: eastus
name: qpaper-ai
properties:
  containers:
  - name: backend
    properties:
      image: your-registry/qpaper-backend:latest
      environmentVariables:
      - name: DATABASE_URL
        value: postgresql://...
      - name: MONGODB_URL
        value: mongodb+srv://...
      resources:
        requests:
          cpu: 1
          memoryInGb: 2
```

## Cost Optimization

### Database Sizing
- **Development**: Use smallest instances (db.t3.micro, M0 Atlas)
- **Production**: Scale based on usage patterns
- **Monitoring**: Set up alerts for costs and performance

### Storage Optimization
- Use S3 Intelligent Tiering for long-term storage
- Implement lifecycle policies
- Compress images and documents

### Caching Strategy
- Use Redis for session storage
- Cache frequently accessed data
- Implement CDN for static assets

## Security Best Practices

1. **Database Security**
   - Use SSL/TLS connections
   - Enable encryption at rest
   - Implement VPC peering
   - Use IAM roles and policies

2. **Access Control**
   - Implement least privilege access
   - Use connection pooling
   - Monitor database access logs

3. **Backup Strategy**
   - Automated daily backups
   - Point-in-time recovery
   - Cross-region replication

## Monitoring and Alerting

### CloudWatch (AWS)
```python
# backend/app/core/monitoring.py
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='QPaperAI',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
        ]
    )
```

### Google Cloud Monitoring
```python
from google.cloud import monitoring_v3

def create_custom_metric(project_id, metric_type, value):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = metric_type
    series.resource.type = "global"
    series.points = [monitoring_v3.Point(value=monitoring_v3.TypedValue(double_value=value))]
    
    client.create_time_series(name=project_name, time_series=[series])
```

This cloud setup will give you a scalable, production-ready QPaper AI system with proper database management and monitoring. Choose the cloud provider that best fits your needs and budget!
