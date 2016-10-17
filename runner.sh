#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR"/venv/bin/activate"

python $DIR"/manage.py" runscript run_from_shell > $DIR"/runner.log" 2>&1

deactivate
