cd ~/Projects
git clone git@github.com:invisibleroads/crosscompute.git
git clone git@github.com:invisibleroads/count-buildings.git
git clone git@github.com:invisibleroads/noccn.git
v
cd ~/Projects/crosscompute
git checkout -b 0.7 origin/0.7
python setup.py develop
cd ~/Projects/count-buildings
python setup.py develop
cd ~/Projects/noccn
git checkout -b patch-1 origin/patch-1
python setup.py develop
