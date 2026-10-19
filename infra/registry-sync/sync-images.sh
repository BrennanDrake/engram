#!/usr/bin/env bash
# Copy new image tags from GHCR to the NAS registry (ADR-0004).
#
# Usage: sync-images.sh SRC_PREFIX DST_PREFIX
#   e.g. sync-images.sh ghcr.io/brennandrake/engram 192.168.1.203:3300/carvinaxe3
#
# Copies immutable tags (robot:<sha>, base:<date>-<sha>) once, and re-copies the
# moving tags (robot:main, base:latest) when their digest changed. Per-arch base
# tags are skipped: the multi-arch base:<date>-<sha> already contains them.
# Needs `crane` logged in to both registries. DST_INSECURE=1 (default) allows
# the plain-HTTP NAS registry.
set -euo pipefail

src_prefix=${1:?source prefix}
dst_prefix=${2:?destination prefix}
dst_flags=()
if [[ ${DST_INSECURE:-1} == 1 ]]; then
  dst_flags=(--insecure)
fi

# image name -> regex of immutable tags | space-separated moving tags
declare -A immutable=([robot]='^[0-9a-f]{7}$' [base]='^[0-9]{8}-[0-9a-f]{7}$')
declare -A moving=([robot]='main' [base]='latest')

copied=0
for image in robot base; do
  src="$src_prefix/$image"
  dst="$dst_prefix/$image"
  if ! src_tags=$(crane ls "$src" 2> /dev/null); then
    echo "skip $image: not in source registry yet"
    continue
  fi
  # A missing destination repository just means nothing has been copied yet.
  dst_tags=$(crane ls "${dst_flags[@]}" "$dst" 2> /dev/null || true)

  for tag in $src_tags; do
    if [[ $tag =~ ${immutable[$image]} ]]; then
      if grep -qx -- "$tag" <<< "$dst_tags"; then
        continue
      fi
    elif [[ " ${moving[$image]} " == *" $tag "* ]]; then
      src_digest=$(crane digest "$src:$tag")
      dst_digest=$(crane digest "${dst_flags[@]}" "$dst:$tag" 2> /dev/null || true)
      if [[ $src_digest == "$dst_digest" ]]; then
        continue
      fi
    else
      continue
    fi
    echo "copy $image:$tag"
    crane copy "${dst_flags[@]}" "$src:$tag" "$dst:$tag"
    copied=$((copied + 1))
  done
done
echo "done: $copied tag(s) copied"
