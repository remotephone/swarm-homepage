# Swarm Homepage 🐝

A service discovery dashboard for Docker Swarm running behind Traefik. Automatically discovers and displays your services with their favicons in a beautiful, responsive dashboard.

## Features

- 🔍 **Automatic Service Discovery**: Reads Docker labels to find services
- 🎨 **Beautiful Dashboard**: Clean, responsive interface with favicon support
- 🔄 **Auto-refresh**: Keeps your service list up-to-date
- 🏷️ **Category Support**: Organize services into categories
- 🐳 **Docker Native**: Works with Docker socket or Traefik API
- 🚀 **Easy Deployment**: Simple Docker container deployment

## How It Works

The application connects to the Docker socket to read service labels from Docker Swarm services and discover services running behind Traefik. It can also connect to the Traefik API as a fallback.

For Docker Swarm deployments, the application uses the Docker Swarm services API to read labels from service definitions (under `deploy.labels` in your stack files).

## Quick Start

### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/remotephone/swarm-homepage.git
cd swarm-homepage
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. Access the dashboard at `http://localhost:5000`

### Using Docker

#### Using Pre-built Image from GitHub Container Registry

```bash
# Pull and run the latest image
docker run -d \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e TRAEFIK_API_URL=http://traefik:8080/api \
  -e REFRESH_INTERVAL=60 \
  ghcr.io/remotephone/swarm-homepage:latest
```

#### Building Locally

```bash
# Build the image
docker build -t swarm-homepage .

# Run the container
docker run -d \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e TRAEFIK_API_URL=http://traefik:8080/api \
  -e REFRESH_INTERVAL=60 \
  swarm-homepage
```

## Configuration

Configure the application using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TRAEFIK_API_URL` | URL to Traefik API | `http://traefik:8080/api` |
| `DOCKER_SOCKET` | Path to Docker socket | `unix://var/run/docker.sock` |
| `REFRESH_INTERVAL` | Auto-refresh interval in seconds | `60` |
| `PORT` | Port to run the application on | `5000` |

## Service Labels

To make your services appear on the homepage, add labels to your services:

### For Docker Swarm (Recommended)

In Docker Swarm mode, labels should be placed under `deploy.labels`:

```yaml
services:
  myservice:
    image: myimage:latest
    deploy:
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.myservice.rule=Host(`myservice.example.com`)"
```

### For Docker Compose

In Docker Compose mode (non-swarm), labels are placed directly on the service:

```yaml
services:
  myservice:
    image: myimage:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myservice.rule=Host(`myservice.example.com`)"
```

### Required Labels

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.myservice.rule=Host(`myservice.example.com`)"
```

**Note:** For Docker Swarm deployments, these labels should be placed under `deploy.labels` as shown in the Docker Swarm example above.

### Optional Homepage Labels

Enhance your service's appearance with these optional labels:

```yaml
labels:
  # Display name (defaults to service name)
  - "homepage.name=My Service"
  
  # Description shown under the service
  - "homepage.description=A great service for doing things"
  
  # Custom icon URL
  - "homepage.icon=https://example.com/icon.png"
  
  # Category for grouping services
  - "homepage.category=Applications"
  
  # Custom URL (if different from Traefik rule)
  - "homepage.url=https://myservice.example.com"
```

**Note:** For Docker Swarm deployments, these labels should be placed under `deploy.labels`.

### Label Format Alternatives

The application supports multiple label formats:
- `homepage.*` (recommended)
- `swarm.homepage.*` (alternative)

## Example Service Configuration

### Docker Compose Example

Here's a complete example of a service with homepage labels for Docker Compose:

```yaml
version: '3.8'

services:
  myapp:
    image: myapp:latest
    networks:
      - traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`myapp.example.com`)"
      - "traefik.http.routers.myapp.entrypoints=websecure"
      - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
      - "traefik.http.services.myapp.loadbalancer.server.port=80"
      
      # Homepage labels
      - "homepage.name=My Application"
      - "homepage.description=Main application dashboard"
      - "homepage.category=Applications"
      - "homepage.icon=https://myapp.example.com/favicon.ico"

networks:
  traefik:
    external: true
```

### Docker Swarm Example

Here's the same service configured for Docker Swarm (note labels under `deploy.labels`):

```yaml
version: '3.8'

services:
  myapp:
    image: myapp:latest
    networks:
      - traefik
    deploy:
      replicas: 1
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.myapp.rule=Host(`myapp.example.com`)"
        - "traefik.http.routers.myapp.entrypoints=websecure"
        - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
        - "traefik.http.services.myapp.loadbalancer.server.port=80"
        
        # Homepage labels
        - "homepage.name=My Application"
        - "homepage.description=Main application dashboard"
        - "homepage.category=Applications"
        - "homepage.icon=https://myapp.example.com/favicon.ico"

networks:
  traefik:
    driver: overlay
    external: true
```

## Integration with Traefik

### Docker Compose with Traefik

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    networks:
      - traefik

  swarm-homepage:
    image: swarm-homepage:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - TRAEFIK_API_URL=http://traefik:8080/api
    networks:
      - traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.homepage.rule=Host(`home.example.com`)"
      - "traefik.http.services.homepage.loadbalancer.server.port=5000"

networks:
  traefik:
    driver: bridge
```

## Development

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access at `http://localhost:5000`

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/services` - JSON list of discovered services
- `GET /health` - Health check endpoint

## Screenshots

The dashboard features:
- Responsive grid layout
- Automatic favicon fetching
- Category-based organization
- Smooth hover effects
- Auto-refresh capability

## Troubleshooting

### No services showing up

1. Ensure containers have `traefik.enable=true` label
2. Check Docker socket is mounted: `-v /var/run/docker.sock:/var/run/docker.sock:ro`
3. Verify Traefik labels are correctly formatted
4. Check application logs: `docker logs swarm-homepage`

### Permission issues

The application runs as a non-root user. Ensure the Docker socket has appropriate permissions:
```bash
# Add read permissions to Docker socket
sudo chmod 644 /var/run/docker.sock
```

Or add the user to the docker group:
```bash
sudo usermod -aG docker $USER
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.
