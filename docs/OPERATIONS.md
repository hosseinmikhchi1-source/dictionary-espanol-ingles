# Operations Guide

## Server Requirements

- **vCPU:** 2
- **RAM:** 4 GB
- **Disk:** 40 GB (v1 with audio)
- **OS:** Ubuntu 22.04 LTS

## Deployment

### 1. Initial Setup

```bash
# Clone the repository
git clone <repository-url> /opt/dictionary
cd /opt/dictionary

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Start services
docker compose up -d

# Check status
docker compose ps
docker compose logs -f
```

### 2. Environment Variables

Create a `.env` file in the `deploy/` directory:

```env
DATABASE_PASSWORD=your_secure_password
ALLOWED_ORIGINS=https://yourdomain.com
SITE_URL=https://yourdomain.com
```

### 3. HTTPS with Let's Encrypt

```bash
# Obtain certificate
docker compose run --rm certbot certonly --webroot \
  --webroot-path /var/www/certbot \
  -d yourdomain.com

# Auto-renewal is handled by the certbot service
```

### 4. Database Backups

```bash
# Nightly backup (add to crontab)
0 2 * * * cd /opt/dictionary && docker compose exec -T postgres pg_dump -U dictionary dictionary > /backups/dictionary_$(date +\%Y\%m\%d).sql

# Restore from backup
docker compose exec -T postgres psql -U dictionary dictionary < /backups/dictionary_20260930.sql
```

### 5. Updating

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

### 6. Rebuilding the Database

```bash
# Run ETL pipeline
docker compose exec api python -m etl.etl

# Ingest enrichment (if applicable)
docker compose exec api python -m enrich.ingest
```

## Monitoring

```bash
# Service status
docker compose ps

# Logs
docker compose logs -f [service]

# Resource usage
docker stats
```

## Troubleshooting

### Database connection issues
```bash
docker compose exec postgres pg_isready -U dictionary
docker compose logs postgres
```

### API not responding
```bash
docker compose logs api
docker compose restart api
```

### Website not loading
```bash
docker compose logs web
docker compose logs nginx
```
