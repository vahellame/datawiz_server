nohup bash -c 'while true; do $PWD/venv/bin/python $PWD/main.py ; done' 1>> $PWD/out.txt 2>> $PWD/errors.txt &

