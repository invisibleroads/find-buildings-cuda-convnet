v

cd /tmp
sudo yum -y install kernel-devel libvdpau-devel
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/331.67/NVIDIA-Linux-x86_64-331.67.run
sudo bash NVIDIA-Linux-x86_64-331.67.run

cd /tmp
wget http://developer.download.nvidia.com/compute/cuda/6_0/rel/installers/cuda_6.0.37_linux_64.run
sudo yum -y install libGLU-devel libX11-devel libXmu-devel
sudo bash cuda_6.0.37_linux_64.run --override
# sudo reboot

sudo yum -y install gcc gcc-c++ cmake
sudo yum -y install perl-Env
sudo yum -y install atlas-devel opencv-devel

# cd ~/.virtualenvs/crosscompute/opt
# git clone https://code.google.com/p/cuda-convnet2/
# cd cuda-convnet2
# vim build.sh
    # export NUMPY_INCLUDE_PATH=/usr/lib64/python2.7/site-packages/numpy/core/include/numpy/
    # export ATLAS_LIB_PATH=/usr/lib64/atlas/
# bash build.sh
