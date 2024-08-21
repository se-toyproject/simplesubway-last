#!/usr/bin/env bash

REPOSITORY=/home/ubuntu/sesubway
FLASK_APP_DIR=/home/ubuntu/sesubway
ENV_PATH=$FLASK_APP_DIR/.env

# .env 파일 로드 (존재할 경우)
if [ -f $ENV_PATH ]; then
    source $ENV_PATH
fi

# 가상 환경 설정 및 패키지 설치
echo "> Setting up new virtual environment"
python3 -m venv $FLASK_APP_DIR/venv
source $FLASK_APP_DIR/venv/bin/activate

echo "> Installing dependencies"
pip install -r $FLASK_APP_DIR/requirements.txt

# Flask 애플리케이션 시작
echo "> Starting Flask app with gunicorn"
cd $FLASK_APP_DIR
source $FLASK_APP_DIR/venv/bin/activate
nohup gunicorn -w 4 app:app -b 0.0.0.0:5002 > /dev/null 2> /dev/null < /dev/null &
