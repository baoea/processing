#!/usr/bin/env bash
set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd $DIR
python -m unittest discover -s lib -p "*_test.py"