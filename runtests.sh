#!/bin/sh

git clone https://github.com/camgunz/cmp.git
git clone https://github.com/stapelzeiger/cmp_mem_access.git
mkdir -p build
cd build
cmake ..
make
./tests
cd ..


cd python
python3 -m unittest discover
