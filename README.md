
## 💻 Installation

These steps assume you are connected to your Raspberry Pi via SSH using the default user (`user`).

### 1. Prerequisites

Ensure your system is up-to-date and has Python 3 and Git installed.

```bash
sudo apt update
sudo apt install python3 python3-venv git -y
````

-----

### 2\. Clone Repository and Create Credentials

Clone the repository and set up your required authentication token.

```bash
# Clone the application repository
git clone https://github.com/bdewitt84/home-automation.git
cd ./home-automation

# Create the credentials file and paste your GitHub Personal Access Token (PAT)
# The PAT must have repository read access.
nano ./config/git_pull_token.env
```

> **File: `config/git_pull_token.env`**
>
> ```
> GIT_PAT=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
> ```

-----

### 3\. Run Setup Script

The setup script handles virtual environment creation, dependency installation, system service deployment, and configuration of passwordless `sudo` for service restart.

```bash
# Ensure the setup script is executable
chmod +x setup.sh

# Run the deployment script
sudo ./setup.sh
```


-----

### 5\. Uninstalling

To remove the system service files (unit file, update script, and `sudoers` rule):

```bash
# Run the uninstall script
sudo ./uninstall.sh
```
