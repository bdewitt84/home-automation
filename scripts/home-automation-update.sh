#!/bin/bash


# Locate resources

echo "--- home-automation update script ---"
APP_DIR="/home/user/home-automation"
CRED_FILE="$APP_DIR/config/git_pull_token.env"
cd $APP_DIR || {
	echo "Error: failed to change directory to $APP_DIR" >&2
	exit 1
}


# Load credentials for git pull

echo "Looking up credential file..."

if [ -f "$CRED_FILE" ]; then
	source "$CRED_FILE"
else
	echo "Error: failed to find git credentials" >&2; exit 1;
fi
echo "Credential file located."


# Update application files from git repository

echo "Pulling update from git repository..."
git pull https://bdewitt8:$GIT_PAT@github.com/bdewitt84/home-automation.git develop || {
	echo "Error: failed to perform git pull" >&2
	exit 1
	}
echo "Pull successful."


# Update python dependencies

echo "Updating python and dependencies..."
source $APP_DIR/.venv/bin/activate || {
	echo "Error: failed to activate venv; dependency update failed" >&2
	exit 1
	}
pip install --quiet --upgrade pip || {
  echo "Error: failed to upgrade pip" >&2
}
pip install --quiet --requirement "$APP_DIR/requirements.txt" || {
	echo "Error: failed to install dependencies" >&2
	exit 1
	}
deactivate || {
	echo "Error: failed to deactivate venv" >&2
	exit 1
	}
echo "Dependency update successful"


# Copy recently pulled version of this update script to system directory

echo "Refreshing update script..."
sudo cp $APP_DIR/scripts/home-automation-update.sh /usr/local/bin || {
	echo "Error: failed to copy update script" >&2
	exit 1
	}
sudo chmod +x /usr/local/bin/home-automation-update.sh || {
	echo "Error: failed to add execute permissions to update script" >&2
	exit 1
	}
echo "Update script update successful"


# Copy updated systemd unit file to system directory

echo "Refreshing service config..."
sudo cp $APP_DIR/config/home-automation.service /etc/systemd/system || {
	echo "Error: failed to copy systemd unit file" >&2
	exit 1
	}
sudo systemctl daemon-reload || {
	echo "Error: failed to reload configuration changes" >&2
	}
echo "Service configuration update successful."


# Schedule system restart asynchronously

echo "Scheduling service restart..."
(sleep 1 && sudo systemctl restart home-automation.service) &

if [ $? -ne 0 ]; then
	echo "Error: failed to schedule system restart" >&2
	exit 1
fi
echo "Service restart scheduled."


# Script executed successfully

echo "--- home-automation update complete ---"

exit 0
