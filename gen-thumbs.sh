#!/usr/bin/env bash

set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

prefix="static/screenshots"

find "$prefix" -type f -name '*.png' | while read input; do
    output="$prefix/thumb${input##$prefix}"
    output="${output%%png}jpg"
    mkdir -p "$(dirname "$output")"
    convert -verbose -thumbnail 480x360 -quality 90 "$input" "$output"
done

find "$prefix/thumb" -type f -name '*.jpg' | parallel leanify
