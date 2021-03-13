#!/bin/bash

MINIMAL_DOCKER_VERSION=${MINIMAL_DOCKER_VERSION-''}
if [ ! -z $MINIMAL_DOCKER_VERSION ]; then
  CURRENT_DOCKER_VERSION=$(docker -v | cut -d',' -f1 | cut -d' ' -f3)
  version_is_less $CURRENT_DOCKER_VERSION $MINIMAL_DOCKER_VERSION && exit_with_error 'You need a docker version >='$MINIMAL_DOCKER_VERSION
fi

MINIMAL_DOCKER_COMPOSE_VERSION=${MINIMAL_DOCKER_COMPOSE_VERSION-''}
if [ ! -z $MINIMAL_DOCKER_COMPOSE_VERSION ]; then
  CURRENT_DOCKER_COMPOSE_VERSION=$(docker -v | cut -d',' -f1 | cut -d' ' -f3)
  version_is_less $CURRENT_DOCKER_COMPOSE_VERSION $MINIMAL_DOCKER_COMPOSE_VERSION && exit_with_error 'You need a docker-compose version >='$MINIMAL_DOCKER_COMPOSE_VERSION
fi
