#!/bin/bash
set -x  # This turns on "execution tracing"

python3 "$(dirname "$0")/Brand.py" "$@"
