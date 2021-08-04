#!/bin/bash
#
# set local backup dir
#
# example usuage - 
# /var/www/html/weather_obs/noaa_back.sh 'ANZ535*.txt' '/var/www/html'  ndugutime ANZ535.tgz

_local_dir="bkup"
_glob="$1"
_dirs="$2"
_bucket="$3"

echo "glob filter: $1"
echo "dirs:  $2"
echo "bucket: $3"
echo "target file prefix: $4"

_now=$(date "+%Y_%m_%d-%H.%M.%S")

echo "backup is  now at $_now..."

_file="$4.$_now"

echo "file:  $_file"



# echo $_dirs
# disable globbing to create find and aws command
set -f

_find_cmd="find $_dirs -type f -name $_glob  -print0 | xargs -0 tar cfvzP /$_local_dir/$_file"

echo $_find_cmd

_aws_cmd="aws s3 cp /$_local_dir/$_file s3://$_bucket/$_file"


#$aws s3 cp /bkup/$_file  s3://ndugutime/$_file

eval $_find_cmd

echo "glob filter: $1"


echo $_aws_cmd

eval $_aws_cmd
