#!/bin/bash

TEST_SCRIPT_DIR=$(cd $(dirname $0); pwd)

pushd ${TEST_SCRIPT_DIR} > /dev/null

INPUT_DIR="data/20230312"
OUTPUT_DIR=${INPUT_DIR}

python main.py \
    --input-dir ${INPUT_DIR}
    # --output-dir ${OUTPUT_DIR}

popd > /dev/null
