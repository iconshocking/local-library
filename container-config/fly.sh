#!/bin/bash
# run from container-config directory

# NOTE: make sure to add any secrets with 'fly secrets set --stage' before running this script
# ('--stage' prevents the new secrets from re-deploying apps)!

# exit on any error
set -e

# env subst for fly.io toml
cp "fly_${1}.toml" "fly_${1}_with_env.toml"
# sort 'unique' keys (equal keys are not overwritten, so use reverse order of standard env override)
# separated by '=' and only use first column (range 1 to 1) to sort on
sort -u -t '=' -k 1,1 git-safe/.prod.safe.env git-safe/.dev.safe.env >>"fly_${1}_with_env.toml"
# sed wraps all appended env line values with single quotes (other lines have spaces surrounding the
# '=', so we check for the absence of that)
sed -E -i '' "s%([^ ]+)=([^ ]+)%\1='\2'%g" "fly_${1}_with_env.toml"

# build the image if needed
if [ "$2" = "build" ]; then
  ./docker_compose.sh prod "${1}"
fi

if [ "$2" != "deploy-only" ]; then
  # tag and push image to fly.io
  docker tag "library-${1}" "registry.fly.io/cshock-library-${1}"
  docker push "registry.fly.io/cshock-library-${1}"
fi

# deploy to fly.io without high availability, which always spins up 1 more than min instances set
fly deploy -c "fly_${1}_with_env.toml" --ha=false
