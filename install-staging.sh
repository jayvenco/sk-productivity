#!/bin/bash
# SKP Staging — Unraid installatie
docker pull ghcr.io/jayvenco/sk-productivity:staging

docker run -d \
  --name skp-staging \
  -p 4433:4442 \
  -v /mnt/user/appdata/sk-productivity:/app/data \
  --restart unless-stopped \
  ghcr.io/jayvenco/sk-productivity:staging