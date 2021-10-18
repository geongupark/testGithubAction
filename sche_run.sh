#!/bin/bash

# 0. Execute main pgm in venv
CUR_PATH=$(pwd)
source $CUR_PATH/venv_gus/bin/activate
pwd
Sise_trans_style.py
deactivate

echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
# 1. Concat arguments for commit message
# > "$@" : All arguments
for arg in "$@";do
        args="${args} ${arg}"
done

# 2. Concat the current time before arguments
args="$(date +%Y%m%d), ""${args}"

# 3. Command for commit
# > && : Run commands sequentially
git add . && git commit -m "${args}" && git push origin master

