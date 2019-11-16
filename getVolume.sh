#!/bin/bash
vol=$(awk '/%/ {gsub(/[\[\]]/,""); print $4}' <(amixer sget Master))
echo $vol