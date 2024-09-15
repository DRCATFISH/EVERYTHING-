#!/bin/bash

# Ultimate APK Build Script with Auto-Update by Ethical Hacker GPT

# Version control
SCRIPT_VERSION="1.0.0"
REMOTE_SCRIPT_URL="https://raw.githubusercontent.com/your-repo/your-project/main/build_apk_auto.sh"  # Replace with your GitHub URL
TMP_SCRIPT_PATH="/tmp/build_apk_auto.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Set up logging
LOG_FILE="build_log_$(date +"%Y%m%d_%H%M%S").log"

# Function to print status messages
function print_status() {
    echo -e "${GREEN}[$(date +"%T")] $1${NC}"
    echo "[$(date +"%T")] $1" >> "$LOG_FILE"
}

# Function to handle errors
function handle_error() {
    echo -e "${RED}Error: $1${NC}" >&2
    echo "Error: $1" >> "$LOG_FILE"
    exit 1
}

# Check for updates
function check_for_updates() {
    print_status "Checking for updates..."

    # Download the latest script version from the remote repository
    curl -s https://github.com/DRCATFISH/EVERYTHING-/blob/main/build_apk_auto.py -o "$TMP_SCRIPT_PATH"

    if [ $? -ne 0 ]; then
        print_status "Failed to check for updates. Continuing with the current version."
        return
    fi

    # Extract the version from the remote script
    REMOTE_VERSION=$(grep -m1 '^SCRIPT_VERSION=' "$TMP_SCRIPT_PATH" | cut -d '"' -f 2)

    if [ "$REMOTE_VERSION" != "$SCRIPT_VERSION" ]; then
        print_status "New version available: $REMOTE_VERSION. Updating..."
        mv "$TMP_SCRIPT_PATH" "$0" || handle_error "Failed to apply the update."
        chmod +x "$0"
        print_status "Update applied successfully. Restarting the script..."
        exec "$0" "$@"
    else
        print_status "You are using the latest version: $SCRIPT_VERSION."
    fi
}

# Call the function to check for updates
check_for_updates "$@"

# Check OS and adapt accordingly
OS=$(uname -s)
print_status "Detected OS: $OS"

case "$OS" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*|MINGW*|MSYS*) MACHINE=WSL;;
    *)          handle_error "Unsupported OS: $OS";;
esac

print_status "Machine type: $MACHINE"

# Step 1: Install dependencies based on the OS
if [ "$MACHINE" == "Linux" ] || [ "$MACHINE" == "WSL" ]; then
    print_status "Installing Linux/WSL dependencies..."
    sudo apt update || handle_error "Failed to update package list"
    sudo apt install -y python3-pip openjdk-8-jdk git unzip || handle_error "Failed to install essential packages"
elif [ "$MACHINE" == "Mac" ]; then
    print_status "Installing macOS dependencies..."
    brew update || handle_error "Failed to update Homebrew"
    brew install python3 git openjdk || handle_error "Failed to install essential packages"
else
    handle_error "OS not supported for automatic installation"
fi

# Step 2: Install Buildozer
if ! command -v buildozer &> /dev/null; then
    print_status "Installing Buildozer..."
    pip3 install --user --upgrade buildozer || handle_error "Failed to install Buildozer"
else
    print_status "Buildozer is already installed."
fi

# Add local bin to PATH if it's not there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
    export PATH=$PATH:$HOME/.local/bin
    print_status "Added ~/.local/bin to PATH."
fi

# Step 3: Gather user input for customization
echo -e "${CYAN}Let's customize your APK build.${NC}"

read -p "Enter the name of your application (default: hackGPT): " app_name
app_name=${app_name:-hackGPT}

read -p "Enter the package domain (default: org.ethicalhacker): " package_domain
package_domain=${package_domain:-org.ethicalhacker}

read -p "Enter the main Python file (default: hackgpt.py): " main_file
main_file=${main_file:-hackgpt.py}

read -p "Enter any additional Python dependencies (comma-separated, default: colorama): " dependencies
dependencies=${dependencies:-colorama}

# Step 4: Initialize Buildozer if needed
if [ ! -f buildozer.spec ]; then
    print_status "Initializing Buildozer..."
    buildozer init || handle_error "Buildozer initialization failed"
else
    print_status "Buildozer already initialized."
fi

# Step 5: Modify buildozer.spec
print_status "Configuring buildozer.spec..."

sed -i "s|# (str) Title of your application|package.name = $app_name|" buildozer.spec
sed -i "s|# (str) Package domain|package.domain = $package_domain|" buildozer.spec
sed -i "s|# (list) Application requirements|requirements = python3, $dependencies|" buildozer.spec
sed -i "s|# (str) Source code file|source.main = $main_file|" buildozer.spec
sed -i "s|# source.include_patterns = assets/*, images/*.png|source.include_patterns = $main_file|" buildozer.spec

# Step 6: Build the APK
print_status "Building the APK. This may take a while..."

buildozer -v android debug >> "$LOG_FILE" 2>&1 || handle_error "APK build failed. Check the log: $LOG_FILE"

# Step 7: Check if the APK was built
APK_PATH="bin/${app_name}-0.1-debug.apk"
if [ -f "$APK_PATH" ]; then
    print_status "APK built successfully!"
    print_status "You can find your APK here: $APK_PATH"
else
    handle_error "APK build failed. Check $LOG_FILE for details."
fi

# Step 8: Optional - Install APK via adb
read -p "Would you like to install the APK on a connected device using adb? (y/N): " install_choice
if [[ "$install_choice" =~ ^[Yy]$ ]]; then
    if command -v adb &> /dev/null; then
        print_status "Installing APK on the connected device..."
        adb install "$APK_PATH" || handle_error "Failed to install APK on the device."
        print_status "APK installed successfully!"
    else
        handle_error "adb not found. Install adb and try again."
    fi
else
    print_status "Skipping APK installation."
fi

print_status "Script completed. Check the log for details: $LOG_FILE"
