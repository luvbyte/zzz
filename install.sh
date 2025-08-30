#!/usr/bin/env bash
set -euo pipefail

# Name of the virtual environment folder
VENV_DIR="$HOME/.zzz/venv"

# Name of the command
CMD_NAME="zzz"

# Ensure python3 exists
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

# Remove old virtual environment only (not the whole ~/.zzz directory)
if [ -d "$VENV_DIR" ]; then
    echo "Removing old virtual environment at $VENV_DIR"
    rm -rf "$VENV_DIR"
fi

# Create fresh virtual environment
echo "Creating virtual environment in $VENV_DIR"
python3 -m venv "$VENV_DIR"

# Upgrade pip and install package
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -e .

# Create wrapper script in ~/.local/bin
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/$CMD_NAME" <<EOL
#!/usr/bin/env bash
exec "$VENV_DIR/bin/$CMD_NAME" "\$@"
EOL

# Make it executable
chmod +x "$HOME/.local/bin/$CMD_NAME"

echo "Installation complete!"
echo "Make sure $HOME/.local/bin is in your PATH"
echo "You can now run '$CMD_NAME' from the terminal"