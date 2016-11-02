#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR"/venv/bin/activate"

python $DIR"/manage.py" runscript update_from_shell > $DIR"/runner_update.log" 2>&1 &&

python $DIR"/manage.py" runscript all_persons_runner > $DIR"/runner_all_m.log" 2>&1  &
python $DIR"/manage.py" runscript pgs_runner > $DIR"/runner_pgs.log" 2>&1  &
python $DIR"/manage.py" runscript sessions_runner > $DIR"/runner_sessions.log" 2>&1  &
python $DIR"/manage.py" runscript single_person_runner > $DIR"/runner_single.log" 2>&1  &

wait

deactivate
