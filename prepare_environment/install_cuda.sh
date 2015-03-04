# Install kernel 3.12.9
sudo yum -y install https://kojipkgs.fedoraproject.org/packages/kernel/3.12.9/301.fc20/x86_64/kernel-3.12.9-301.fc20.x86_64.rpm
sudo yum -y install https://kojipkgs.fedoraproject.org/packages/kernel/3.12.9/301.fc20/x86_64/kernel-devel-3.12.9-301.fc20.x86_64.rpm
sudo yum -y install libvdpau-devel
# sudo reboot

# Install cuda 6.5
cd ~/Storage/programs/cuda
wget http://developer.download.nvidia.com/compute/cuda/6_5/rel/installers/cuda_6.5.14_linux_64.run
sudo bash cuda_6.5.14_linux_64.run --override
