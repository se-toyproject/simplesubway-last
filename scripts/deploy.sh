#!/usr/bin/env bash

REPOSITORY=/home/ubuntu/moduform
cd $REPOSITORY

APP_NAME=moduform
PYTHON_SCRIPT=$(ls $REPOSITORY/ | grep '.py' | tail -n 1)
PYTHON_PATH=$REPOSITORY/$PYTHON_SCRIPT

CURRENT_PID=$(pgrep -f $APP_NAME)

if [ -z "$CURRENT_PID" ]
then
  echo "> 종료할 애플리케이션이 없습니다."
else
  echo "> 종료 중 - kill -15 $CURRENT_PID"
  kill -15 $CURRENT_PID
  sleep 5
fi

echo "> Deploy - $PYTHON_PATH"
nohup python3 $PYTHON_PATH > /dev/null 2> /dev/null < /dev/null &