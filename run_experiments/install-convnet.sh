cd /tmp
wget http://developer.download.nvidia.com/compute/cuda/6_0/rel/installers/cuda_6.0.37_linux_64.run
sudo yum -y install libGLU-devel libX11-devel libXmu-devel
sudo bash cuda_6.0.37_linux_64.run --override

cd ~/.virtualenvs/crosscompute/opt
git clone https://github.com/dnouri/cuda-convnet.git
cd cuda-convnet
sudo yum -y install cmake
sudo yum -y install perl-Env
sudo yum -y install atlas-devel
cmake -DBLAS_INCLUDE_DIRS=/usr/lib64/atlas/libcblas.so .
make
