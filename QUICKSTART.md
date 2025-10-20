# Quick Start Guide

Get your Swarm Homepage running in 5 minutes!

## Option 1: Docker Compose (Recommended for testing)

1. Clone and enter the repository:
```bash
git clone https://github.com/remotephone/swarm-homepage.git
cd swarm-homepage
```

2. Start the services:
```bash
docker-compose up -d
```

3. Open your browser to `http://localhost:5000`

That's it! The dashboard will automatically discover any services with Traefik labels.

## Option 2: Docker Swarm Stack

For production Docker Swarm deployments:

1. Initialize Swarm (if not already done):
```bash
docker swarm init
```

2. Create the network:
```bash
docker network create --driver overlay traefik
```

3. Build the image:
```bash
docker build -t swarm-homepage:latest .
```

4. Deploy the stack:
```bash
docker stack deploy -c docker-stack.example.yml homepage
```

5. Access at `http://home.example.com` (adjust hostname in the stack file)

## Testing with Example Services

Want to see it in action with sample services?

```bash
docker-compose -f docker-compose.example.yml up -d
```

This will start:
- Traefik reverse proxy
- Swarm Homepage
- Several example services (Adminer, Prometheus, Grafana, etc.)

Access the homepage at `http://localhost:5000` and you'll see all services listed!

## Adding Your Services

To make your services appear on the homepage, just add these labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.myapp.rule=Host(`myapp.example.com`)"
  - "homepage.name=My Application"
  - "homepage.description=What this service does"
  - "homepage.category=Applications"
```

## Configuration

Customize with environment variables:

```yaml
environment:
  - TRAEFIK_API_URL=http://traefik:8080/api
  - REFRESH_INTERVAL=60
  - PORT=5000
```

## Troubleshooting

**No services showing up?**
- Ensure containers have `traefik.enable=true`
- Check Docker socket is mounted: `-v /var/run/docker.sock:/var/run/docker.sock:ro`
- Verify Traefik router rules in labels

**Permission errors?**
- Make sure the Docker socket has read permissions
- Or run with appropriate user permissions

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [docker-compose.example.yml](docker-compose.example.yml) for more examples
- Customize the CSS in `static/css/style.css` to match your branding
