#!/bin/bash
cd "/home/parlauser/hr-parser/"
echo "parse"
source /home/parlauser/.virtualenvs/hrparser/bin/activate
echo "parse votes"
scrapy crawl votes > sorl_export.log 2>&1 &&
echo "parse speeches"
scrapy crawl speeches > sorl_export.log 2>&1 &&
echo "parse questions"
scrapy crawl questions > sorl_export.log 2>&1 &&


#python manage.py runscript export_to_solr > sorl_export.log 2>&1 &&
deactivate


cd "/home/parlauser/parlalize"
source /home/parlauser/.virtualenvs/parlalize/bin/activate
echo "parlalize"


echo "Start update"
python manage.py runscript update_from_shell --script-args fastUpdate > runner_update.log 2>&1 &&


#echo "Start runner all mps"
#python $DIR"/manage.py" runscript all_persons_runner > $DIR"/runner_all_m.log" 2>&1  &
#echo "Start runner pgs"
#python $DIR"/manage.py" runscript pgs_runner > $DIR"/runner_pgs.log" 2>&1  &
#echo "Start runner sessions"
#python $DIR"/manage.py" runscript sessions_runner > $DIR"/runner_sessions.log" 2>&1  &
#echo "Start runner signle persons"
#python $DIR"/manage.py" runscript single_person_runner > $DIR"/runner_single.log" 2>&1  &

wait
echo "End update"
deactivate
