#!/bin/bash

# Custom entrypoint for CPU-compatible Stable Diffusion WebUI
# This script ensures xformers is NOT used on CPU and fixes permission issues

echo "Starting Stable Diffusion WebUI in CPU mode..."

# Set environment variable to disable xformers
export COMMANDLINE_ARGS="--api --listen --port 8080 --enable-insecure-extension-access --skip-torch-cuda-test --no-half --use-cpu all --precision full --disable-opt-split-attention --opt-sub-quad-attention --lowvram --allow-code"

# Change to the webui directory
cd /app/stable-diffusion-webui

# Install ControlNet extension
CONTROLNET_DIR="extensions/sd-webui-controlnet"
if [ ! -d "$CONTROLNET_DIR" ]; then
    echo "Installing ControlNet extension..."
    git clone https://github.com/Mikubill/sd-webui-controlnet.git "$CONTROLNET_DIR"
else
    echo "ControlNet extension already installed."
fi

# Install IP-Adapter models
CONTROLNET_MODELS_DIR="models/ControlNet"
IP_ADAPTER_FACE_MODEL="ip-adapter-plus-face_sd15.pth"
IP_ADAPTER_MODEL="ip-adapter-plus_sd15.pth"

mkdir -p "$CONTROLNET_MODELS_DIR"

if [ ! -f "$CONTROLNET_MODELS_DIR/$IP_ADAPTER_FACE_MODEL" ]; then
    echo "Downloading IP-Adapter face model..."
    wget -O "$CONTROLNET_MODELS_DIR/$IP_ADAPTER_FACE_MODEL" https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus-face_sd15.pth
else
    echo "IP-Adapter face model already exists."
fi

if [ ! -f "$CONTROLNET_MODELS_DIR/$IP_ADAPTER_MODEL" ]; then
    echo "Downloading IP-Adapter model..."
    wget -O "$CONTROLNET_MODELS_DIR/$IP_ADAPTER_MODEL" https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.pth
else
    echo "IP-Adapter model already exists."
fi


# Get current user info
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

echo "Running as user: $CURRENT_USER, group: $CURRENT_GROUP"

# Create necessary directories with proper permissions for current user
echo "Creating output directories and setting permissions..."
mkdir -p /app/stable-diffusion-webui/outputs/txt2img-images
mkdir -p /app/stable-diffusion-webui/outputs/img2img-images
mkdir -p /app/stable-diffusion-webui/outputs/extras-images
mkdir -p /app/stable-diffusion-webui/log

# Set permissions for directories
chmod -R 755 /app/stable-diffusion-webui/outputs
chmod -R 755 /app/stable-diffusion-webui/log
echo "Set permissions to 755"

# Create a custom webui-user.sh that exports our command line args
cat > webui-user.sh << 'EOF'
#!/bin/bash
# Custom webui-user.sh to ensure CPU mode
export COMMANDLINE_ARGS="--api --listen --port 8080 --enable-insecure-extension-access --skip-torch-cuda-test --no-half --use-cpu all --precision full --disable-opt-split-attention --opt-sub-quad-attention --lowvram --allow-code"
EOF

# Make it executable
chmod +x webui-user.sh

echo "Starting WebUI with fixed permissions..."

# Run the original webui.sh script
./webui.sh