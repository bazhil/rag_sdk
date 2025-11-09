#!/bin/bash

echo "=========================================="
echo "Configuring Ollama for Docker Access"
echo "=========================================="
echo ""

# 1. Create systemd override directory
echo "1. Creating systemd override directory..."
sudo mkdir -p /etc/systemd/system/ollama.service.d

# 2. Create override configuration
echo "2. Creating Ollama override configuration..."
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

echo "   ✅ Override configuration created"

# 3. Reload systemd
echo "3. Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "   ✅ Systemd reloaded"

# 4. Restart Ollama
echo "4. Restarting Ollama service..."
sudo systemctl restart ollama
sleep 2
echo "   ✅ Ollama restarted"

# 5. Verify configuration
echo ""
echo "5. Verifying Ollama is listening on all interfaces..."
echo ""

if ss -tlnp 2>/dev/null | grep -q "0.0.0.0:11434"; then
    echo "   ✅ SUCCESS! Ollama is now listening on 0.0.0.0:11434"
    echo ""
    ss -tlnp 2>/dev/null | grep 11434
    echo ""
    echo "=========================================="
    echo "Configuration complete!"
    echo "Ollama is now accessible from Docker containers."
    echo "=========================================="
else
    echo "   ⚠️  WARNING: Ollama might still be on 127.0.0.1"
    echo ""
    ss -tlnp 2>/dev/null | grep 11434 || netstat -tlnp 2>/dev/null | grep 11434
    echo ""
    echo "If still showing 127.0.0.1, try:"
    echo "  sudo systemctl status ollama"
fi

echo ""
echo "Next steps:"
echo "  1. Refresh your browser (Ctrl+Shift+R)"
echo "  2. Try the 'summary' or 'referat' command"
echo ""

