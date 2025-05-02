#!/usr/bin/env bash
pip uninstall -y opencv-python
pip install opencv-python-headless
pip install --no-cache-dir --upgrade numpy
pip install --no-cache-dir --upgrade opencv-python-headless
