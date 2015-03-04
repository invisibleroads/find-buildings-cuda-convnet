sudo yum -y install gcc gcc-c++ cmake
sudo yum -y install perl-Env
sudo yum -y install atlas-devel opencv-devel

cd ~/.virtualenvs/crosscompute/opt
git clone https://code.google.com/p/cuda-convnet2/
cd cuda-convnet2
export CUDA_INSTALL_PATH=/usr/local/cuda
export PYTHON_INCLUDE_PATH=/usr/include/python2.7
export NUMPY_INCLUDE_PATH=/usr/lib64/python2.7/site-packages/numpy/core/include/numpy/
export ATLAS_LIB_PATH=/usr/lib64/atlas/
export LD_LIBRARY_PATH=$CUDA_INSTALL_PATH/lib64:$LD_LIBRARY_PATH
export CUDA_SDK_PATH=$CUDA_INSTALL_PATH/samples
export PATH=$PATH:$CUDA_INSTALL_PATH/bin
cd util && make numpy=1 -j $* && cd ..
cd nvmatrix && make -j $* && cd ..
cd cudaconv3 && make -j $* && cd ..
cd cudaconvnet && make -j $* && cd ..
cd make-data/pyext && make -j $* && cd ../..

mkdir -p ~/Storage/public-datasets/CIFAR10
cd ~/Storage/public-datasets/CIFAR10
wget http://www.cs.toronto.edu/~kriz/cifar-10-py-colmajor.tar.gz
tar xf cifar-10-py-colmajor.tar.gz
