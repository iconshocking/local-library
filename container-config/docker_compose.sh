#!/bin/bash
# run from container-config directory

# exit on any error
set -e

if [ "$1" = "down" ]; then
  docker compose down --remove-orphans && exit 0
fi

# generate requirements.txt
cd ..
poetry export --without-hashes | awk '{ print $1 }' FS=';' >requirements.txt &&
  sed -i '' "s%.* @ file://$PWD%.%g" requirements.txt
# alternatively, can use pip freeze if witin the poetry shell for a cleaner syntax
#
# pip freeze > requirements.txt && sed -i '' "s%.* @ file://$PWD%.%g" requirements.txt
cd container-config

if [ "$1" = "dev" ]; then
  docker compose \
    --env-file ./secrets/.dev.env \
    --env-file ./git-safe/.dev.safe.env \
    -f compose.yaml \
    -f compose.dev.yaml \
    up "${@:2}"
fi

if [ "$1" = "preprod" ]; then
  # get statics ready for non-Django hosting
  poetry run ./collect_statics.sh ./secrets/.dev.env ./secrets/.preprod.env \
    ./git-safe/.dev.safe.env ./git-safe/.prod.safe.env ./git-safe/.preprod.safe.env

  # don't include prod secrets in preprod; use secrets which should emulate prod requirements
  docker compose \
    --env-file ./secrets/.dev.env \
    --env-file ./secrets/.preprod.env \
    --env-file ./git-safe/.dev.safe.env \
    --env-file ./git-safe/.prod.safe.env \
    --env-file ./git-safe/.preprod.safe.env \
    -f compose.yaml \
    -f compose.prod.yaml \
    -f compose.preprod.yaml \
    up "${@:2}"
fi

# note this just builds the image for pushing to registries; it doesn't run it since a local
# container will likely not be able to properly run the prod images/envs
if [ "$1" = "prod" ]; then
  # get statics ready for non-Django hosting
  # - note: squelch output to avoid leaking secrets into terminal
  poetry run ./collect_statics.sh ./secrets/.dev.env ./secrets/.prod.env \
    ./git-safe/.dev.safe.env ./git-safe/.prod.safe.env 1>/dev/null

  docker compose \
    --env-file ./secrets/.dev.env \
    --env-file ./secrets/.prod.env \
    --env-file ./git-safe/.dev.safe.env \
    --env-file ./git-safe/.prod.safe.env \
    -f compose.yaml \
    -f compose.prod.yaml \
    build "${@:2}"
fi
