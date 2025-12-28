# Script to update .env file to use localhost databases
$envFile = ".env"
$content = Get-Content $envFile -Raw

# Replace Supabase URL with localhost
$content = $content -replace 'DATABASE_URL=postgresql://.*', 'DATABASE_URL=postgresql://qpaper_user:qpaper_password@localhost:5432/qpaper_ai'

# Replace MongoDB URL with localhost (if exists)
$content = $content -replace 'MONGODB_URL=mongodb.*', 'MONGODB_URL=mongodb://qpaper_user:qpaper_password@localhost:27017/qpaper_ai?authSource=admin'

# Replace Redis URL with localhost (if exists)
$content = $content -replace 'REDIS_URL=redis://.*', 'REDIS_URL=redis://localhost:6379'

Set-Content -Path $envFile -Value $content
Write-Host "✅ Updated .env to use localhost databases" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Start Docker: docker-compose up postgres mongodb redis -d" -ForegroundColor Cyan
Write-Host "   2. Run: python init_db.py" -ForegroundColor Cyan

