#!/usr/bin/env bash

REPOSITORY=/home/ubuntu/sesubway
FLASK_APP_DIR=/home/ubuntu/sesubway
ENV_PATH=$FLASK_APP_DIR/.env
cd $REPOSITORY

# Flask 앱 인스턴스 종료
FLASK_PID=$(pgrep -f gunicorn)
if [ -z "$FLASK_PID" ]; then
  echo "> 종료할 Flask 애플리케이션이 없습니다."
else
  echo "> Flask 애플리케이션 종료 중, PID: $FLASK_PID"
  kill -15 $FLASK_PID
  sleep 5
fi

# 환경 변수 로드
if [ -f $ENV_PATH ]; then
    source $ENV_PATH
fi

echo "> 기존 가상 환경 디렉터리 제거"
rm -rf $FLASK_APP_DIR/venv

echo "> 새로운 가상 환경 설정"
python3 -m venv $FLASK_APP_DIR/venv
source $FLASK_APP_DIR/venv/bin/activate

# Flask 앱 시작
echo "> Flask 앱을 Gunicorn으로 시작"
cd $FLASK_APP_DIR
nohup gunicorn -w 4 app:app -b 0.0.0.0:5002 > /dev/null 2> /dev/null < /dev/null &
