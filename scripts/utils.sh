#!/bin/bash

function check {
  STATE=$1
  CONTAINER=${APP_NAME}-${2}
  GREP=$(docker ps | grep $CONTAINER)
  if [[ "$GREP" ]]; then
    if [[ "$STATE" == "stop" ]]; then
      exit_with_error "$CONTAINER is running. You should stop it before applying your command."
    fi
  elif [[ "$STATE" == "start" ]]; then
    exit_with_error "$CONTAINER is not running. You should start it before applying your command."
  fi
}


function exit_with_error {
  MESSAGE=${1-"end of $APP_NAME command."}
  RED='\033[0;31m'
  NO_COLOR='\033[0m'
  echo -e "${RED}""ERROR : $MESSAGE""${NO_COLOR}"
  exit 1
}


function exit_with_success {
  MESSAGE=${1-"end of $APP_NAME command."}
  GREEN='\033[0;32m'
  NO_COLOR='\033[0m'
  echo -e "${GREEN}""SUCCESS : $MESSAGE""${NO_COLOR}"
  exit 0
}
