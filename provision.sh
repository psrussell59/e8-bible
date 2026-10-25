#!/bin/bash
# one-shot E8 narrator provisioning — runs ON the EC2 box as root
set -euo pipefail

TOKEN="$(openssl rand -hex 32)"
printf 'HB_TOKEN=%s\n' "$TOKEN" > /etc/e8-bible.env
chmod 600 /etc/e8-bible.env

cat > /etc/systemd/system/e8-bible.service <<'EOF'
[Unit]
Description=E8 Digital Bible narrator (edge-tts)
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/home/ubuntu/e8-bible
EnvironmentFile=/etc/e8-bible.env
Environment=PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/ubuntu/.local/bin/uv run --with edge-tts python bible-tts-server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now e8-bible
sleep 8
systemctl is-active e8-bible
curl -s --max-time 5 http://127.0.0.1:8747/tts/ping && echo " <- ping ok"
printf 'TOKEN=%s\n' "$TOKEN" > /root/e8-token.txt
chmod 600 /root/e8-token.txt
echo "PROVISION_DONE"
