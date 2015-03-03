v

cd /tmp
sudo yum -y install kernel-devel libvdpau-devel
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/331.67/NVIDIA-Linux-x86_64-331.67.run
sudo bash NVIDIA-Linux-x86_64-331.67.run

cd /tmp
wget http://developer.download.nvidia.com/compute/cuda/6_0/rel/installers/cuda_6.0.37_linux_64.run
sudo yum -y install libGLU-devel libX11-devel libXmu-devel
sudo bash cuda_6.0.37_linux_64.run --override
sudo reboot

cd ~/.virtualenvs/crosscompute/opt
git clone https://github.com/dnouri/cuda-convnet.git
cd cuda-convnet
sudo yum -y install gcc gcc-c++ cmake
sudo yum -y install perl-Env
sudo yum -y install atlas-devel
cmake -DBLAS_LIBRARIES=/usr/lib64/atlas/libcblas.so  .
make

cd ~/Downloads
wget http://www.cs.toronto.edu/~kriz/cifar-10-py-colmajor.tar.gz
tar xzvf cifar-10-py-colmajor.tar.gz
