# Docker Deployment Guide

## Quick Start

### Development Mode

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Open browser to: http://localhost:8501

# Stop the container
docker-compose down
```

### Production Mode (with Nginx)

```bash
# Start with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Access the application
# HTTP: http://your-domain.com (redirects to HTTPS)
# HTTPS: https://your-domain.com
```

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

## Files Created

- **Dockerfile** - Container build instructions
- **docker-compose.yml** - Development configuration
- **docker-compose.prod.yml** - Production configuration with Nginx
- **.dockerignore** - Files to exclude from Docker build
- **nginx.conf** - Nginx reverse proxy configuration

## Configuration

### Port Configuration

To change the port, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:8501"  # Change 8080 to your desired port
```

### Environment Variables

Available environment variables in `docker-compose.yml`:

- `TZ` - Timezone (default: Australia/Sydney)
- `PYTHONUNBUFFERED` - Python output buffering
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS` - Disable telemetry

### Volume Mounts

Data is persisted through Docker volumes:

- `./data:/app/data` - Database storage
- `./documents:/app/documents` - Document storage
- `./config.ini:/app/config.ini:ro` - Configuration (read-only)

## Common Commands

### Container Management

```bash
# Start container
docker-compose up -d

# Stop container
docker-compose down

# Restart container
docker-compose restart

# View container status
docker-compose ps

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec maintenance-app bash
```

### Image Management

```bash
# Build image
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Remove image
docker rmi maintenance-management-system
```

### Database Operations

```bash
# Backup database
docker-compose exec maintenance-app cp /app/data/maintenance_management.db /app/data/backups/backup_$(date +%Y%m%d).db

# Or from host machine
cp data/maintenance_management.db data/backups/backup_$(date +%Y%m%d).db

# Load sample data
docker-compose exec maintenance-app python create_sample_data.py
```

### Health Check

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' maintenance_management_system

# Test health endpoint
curl http://localhost:8501/_stcore/health
```

## Production Setup

### SSL Certificates

For production with SSL, create an `ssl/` directory with your certificates:

```bash
mkdir ssl
# Copy your SSL certificate files:
# ssl/cert.pem
# ssl/key.pem
```

Or use Let's Encrypt:

```bash
# Install certbot
apt-get install certbot

# Generate certificate
certbot certonly --standalone -d your-domain.com

# Copy certificates
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

### Start Production Environment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Check if port is in use
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac
```

### Database Issues

```bash
# Stop container
docker-compose down

# Remove database (WARNING: deletes all data)
rm data/maintenance_management.db

# Restart
docker-compose up -d
```

### Permission Issues

```bash
# Ensure directories have correct permissions
chmod -R 755 data documents
```

### Rebuild After Code Changes

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Resource Limits

To limit container resources, add to `docker-compose.yml`:

```yaml
services:
  maintenance-app:
    # ... other settings ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Monitoring

### View Resource Usage

```bash
docker stats maintenance_management_system
```

### View Detailed Container Info

```bash
docker inspect maintenance_management_system
```

## Backup and Restore

### Complete Backup

```bash
# Stop container
docker-compose down

# Create backup
tar -czf backup_$(date +%Y%m%d).tar.gz data/ documents/ config.ini

# Restart container
docker-compose up -d
```

### Restore from Backup

```bash
# Stop container
docker-compose down

# Extract backup
tar -xzf backup_20241101.tar.gz

# Restart container
docker-compose up -d
```

## Security Best Practices

1. **Change default passwords** in `config.ini`
2. **Use SSL/TLS** in production (see nginx.conf)
3. **Regular updates**: Rebuild images regularly
4. **Limit resources**: Set CPU/memory limits
5. **Network isolation**: Use custom networks
6. **Read-only mounts**: Config file is read-only

## Getting Help

- Check logs: `docker-compose logs -f`
- Check health: `docker inspect --format='{{.State.Health.Status}}' maintenance_management_system`
- Verify network: `docker network inspect mmsmanagement_app-network`
- Test connectivity: `curl http://localhost:8501/_stcore/health`

## Uninstall

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi maintenance-management-system

# Remove volumes (WARNING: deletes data)
docker volume prune

# Remove all Docker data (WARNING: affects all Docker containers)
docker system prune -a
```

---

**Last Updated:** November 2024

