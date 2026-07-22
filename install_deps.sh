#!/usr/bin/env bash

set -e # terminate on any call failure


echo "[EyeBin] Updating package lists..."
sudo apt-get update


echo "[EyeBin] Please keep any connected RealSense camera unplugged until installation is completed. \
Installation will be continued after 10 seconds..."
sleep 10

echo "[EyeBin] Installing dependencies..."
sudo apt-get install -y \
    python3 \
    python3-dev \
    libusb-1.0-0-dev \
    libudev-dev \
    libssl-dev \
    pkg-config \
    libgtk-3-dev \
    git \
    wget \
    cmake \
    build-essential \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    v4l-utils # undocumented but required

echo "[EyeBin] Installing librealsense..."
if [ ! -d "librealsense" ]; then
    git clone https://github.com/realsenseai/librealsense.git
else
    echo "[EyeBin] Skipping installation of librealsense, it already exists."
fi


echo "[EyeBin] Setting up permissions for librealsense..."
cd librealsense # navigate to the librealsense root directory
./scripts/setup_udev_rules.sh

echo "[EyeBin] Trying to apply patched kernel modules for librealsense..."
if ./scripts/patch-realsense-ubuntu-lts-hwe.sh; then
    echo "[EyeBin] Patched kernel modules are applied."
else
    echo "[EyeBin] Patched kernel modules couldn't be applied. \
This generally doesn't cause issues, it can be ignored for this project."
fi


echo "[EyeBin] Creating virtual environment for Python..."
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate # activate the virtual environment


echo "[EyeBin] Building librealsense..."
mkdir -p build && cd build
cmake ../ -DBUILD_EXAMPLES=true -DBUILD_PYTHON_BINDINGS=true -DPYTHON_EXECUTABLE=$(which python3)
(sudo make uninstall || true) && make clean && make -j$(($(nproc)-1)) && sudo make install

deactivate # deactivate the virtual environment

echo "[EyeBin] Installation is completed successfully."