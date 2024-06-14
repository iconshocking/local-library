#!/bin/bash

poetry run ./collect_statics.sh ./secrets/.dev.env ./secrets/.preprod.env \
  ./git-safe/.dev.safe.env ./git-safe/.prod.safe.env ./git-safe/.preprod.safe.env
