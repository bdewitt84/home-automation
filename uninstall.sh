#!/bin/bash
# uninstall.sh: Reverses changes made by setup.sh


SERVICE_NAME="home-automation.service"
SUDOERS_FILE="/etc/sudoers.d/home-automation"


# --- SERVICE DEACTIVATION AND REMOVAL ---

# Stop and Disable Service
echo "Stopping and disabling service..."

# Stop the service if it is active.
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "Stopping $SERVICE_NAME..."
    sudo systemctl stop "$SERVICE_NAME" || { echo "ERROR: Failed to stop $SERVICE_NAME." >&2; ERROR_LEVEL=1; }
else
    echo "Service $SERVICE_NAME is already stopped or inactive."
fi

# Disable the service only if it is enabled.
if sudo systemctl is-enabled --quiet "$SERVICE_NAME"; then
    echo "Disabling $SERVICE_NAME..."
    sudo systemctl disable "$SERVICE_NAME" || { echo "ERROR: Failed to disable $SERVICE_NAME." >&2; ERROR_LEVEL=1; }
else
    echo "Service $SERVICE_NAME is not enabled."
fi

# Remove the unit file if it exists
UNIT_PATH="/etc/systemd/system/$SERVICE_NAME"
if [ -f "$UNIT_PATH" ]; then
    echo "Removing unit file..."
    sudo rm -f "$UNIT_PATH" || { echo "ERROR: Could not remove unit file at $UNIT_PATH. Check permissions." >&2; ERROR_LEVEL=1; }
else
    echo "Unit file not found."
fi

# Reload daemon if a file was removed.
if [ "$UNIT_PATH" ]; then # Check if removal was attempted
    echo "Reloading system configuration..."
    sudo systemctl daemon-reload || { echo "ERROR: Failed to reload system configuration files." >&2; ERROR_LEVEL=1; }
fi

echo "Service removal steps complete."


# --- SUPPORT FILES REMOVAL ---


# Remove Sudoers File
echo "Removing sudoers configuration..."
if [ -f "$SUDOERS_FILE" ]; then
    sudo rm -f "$SUDOERS_FILE" || { echo "ERROR: Failed to remove sudoers configuration file" >&2; ERROR_LEVEL=1; }
    echo "Sudoers entry removed."
else
    echo "Sudoers entry not found."
fi


# --- MAIN APPLICATION REMOVAL ---

# Optional: Remove source code (requires confirmation)
read -r -p "Do you want to remove the local application directory (./home-automation)? [y/N]: " confirmation

if [[ "$confirmation" =~ ^[Yy]$ ]]; then
    # Assuming the user runs this from the parent directory of home-automation
    rm -rf ../home-automation || { echo "ERROR: Failed to remove ./home-automation directory" >&2; ERROR_LEVEL=1; }
    echo "Local application directory removed."
fi

echo "--- UNINSTALL COMPLETE ---"

exit $ERROR_LEVEL
