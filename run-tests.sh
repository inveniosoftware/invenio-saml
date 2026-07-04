#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down docker services
function cleanup() {
    eval "$(docker-services-cli down --env)"
}
trap cleanup EXIT


python -m sphinx.cmd.build -qnNW docs docs/_build/html
eval "$(docker-services-cli up --db ${DB:-postgresql} --cache ${CACHE:-redis} --env)"
python -m pytest
tests_exit_code=$?
exit "$tests_exit_code"
