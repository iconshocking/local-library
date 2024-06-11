#!/bin/bash

# exporting shell envs from files
for env_file in "${@}"; do
  # do not quote the evaluation because it will prevent the shell from splitting the file lines into
  # separate arguments
  # shellcheck disable=SC2046
  export $(grep -v "^#" "$env_file")
done

cd ../library || exit 1

python manage.py collectstatic --noinput --clear

cd ../container-config || exit 1