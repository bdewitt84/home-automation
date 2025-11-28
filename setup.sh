#!/bin/bash
# setup.sh: Deploys the home-automation FastAPI service.

# --- Configuration ---
APP_DIR=$(pwd)
SERVICE_NAME="home-automation.service"
UNIT_FILE="$APP_DIR/config/$SERVICE_NAME"
UPDATE_SCRIPT="$APP_DIR/scripts/home-automation-update.sh"

echo "--- home-automation deployment script ---"

# Install Python Virtual Environment and Dependencies
echo "Setting up Python virtual environment..."
if [ ! -d "$APP_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$APP_DIR/.venv" || { echo "Error: failed to create venv."; exit 1; }
fi

# Install dependencies
source "$APP_DIR/.venv/bin/activate"
pip install --quiet --upgrade pip || { echo "Error: failed to perform upgrade on pip."; exit 1; }
pip install --quiet --requirement "$APP_DIR/requirements.txt" || { echo "Error: failed to install dependencies."; exit 1; }
deactivate
echo "Virtual environment ready."

# Configure sudoers for passwordless restart
# This is required for the update script to run 'sudo systemctl restart' without a password.
echo "Configuring passwordless sudo for service restart..."
SUDOERS_FILE="/etc/sudoers.d/home-automation"
SUDO_ENTRY="user ALL=NOPASSWD: /usr/sbin/systemctl restart $SERVICE_NAME"

# Check if the user already exists in the file, if not, add it.
# TODO: We assume the user is 'user'. Create a dynamic approach.
if ! grep -q "$SUDO_ENTRY" $SUDOERS_FILE 2>/dev/null; then
    # We use tee to write to a root-owned file
    echo "$SUDO_ENTRY" | sudo tee $SUDOERS_FILE > /dev/null || { echo "Error: failed to update sudoers file."; exit 1; }
    echo "Sudoers configured for 'user'."
else
    echo "Sudoers entry already exists."
fi

# Deploy System Files
echo "Deploying unit file..."
# Copy unit file and reload daemon
sudo cp "$UNIT_FILE" /etc/systemd/system/ || { echo "Error: failed to copy unit file."; exit 1; }
sudo systemctl daemon-reload || { echo "Error: failed to reload daemon."; exit 1; }
echo "Unit file deployed."

echo "Deploying update script..."
# Copy and enable execute permissions for update script
sudo cp "$UPDATE_SCRIPT" /usr/local/bin/ || { echo "Error: failed to copy update script."; exit 1; }
sudo chmod +x /usr/local/bin/home-automation-update.sh || { echo "Error: failed to set executable permissions."; exit 1; }
echo "Update script deployed."

# Enable and Start Service
echo "Enabling and starting service..."
sudo systemctl enable $SERVICE_NAME || { echo "Error: failed to enable service."; exit 1; }
sudo systemctl start $SERVICE_NAME || { echo "Error: failed to start service."; exit 1; }

# Final Status Check
echo "--- POST-INSTALL SERVICE STATUS CHECK ---"
sudo systemctl status $SERVICE_NAME --no-pager | head -n 5
echo "--- DEPLOYMENT COMPLETE ---"

echo "Service should now be accessible at:"
echo "http://$(hostname):8000"

# Display accessible IPs
ip a | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | while read -r IP_CIDR; do
    # Remove the CIDR suffix (e.g., /24)
    IP=$(echo "$IP_CIDR" | cut -d/ -f1)
    echo "http://$IP:8000"
done

exit 0
