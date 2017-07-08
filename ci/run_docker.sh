#!/bin/bash

err=0
trap 'err=1' ERR

# Start Xvfb
XVFB_WHD=${XVFB_WHD:-1280x720x16}

Xvfb :99 -ac -screen 0 $XVFB_WHD -nolisten tcp &
xvfb=$!

export DISPLAY=:99

pip install --upgrade pip
pip install -r requirements/test.pip

python setup.py install
make resources

make test-all
# See: https://docs.codecov.io/docs/testing-with-docker for details
bash <(curl -s https://codecov.io/bash)
test $err = 0
