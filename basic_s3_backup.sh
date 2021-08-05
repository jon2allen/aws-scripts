#!/bin/bash
#
# set local backup dir
# this is direcotry on the server where the tar.gz is stored before transit to S3
#
# example usuage - 
# /var/www/html/weather_obs/noaa_back.sh 'ANZ535*.txt' '/var/www/html'  ndugutime ANZ535.tgz
# 4 parms
# $1 = glob filter for find
# $2 = directory to do the glob in 
# $3 = S3 bucket
# $4 = prefix of file - it is automatically appended with time "now"
#    ANZ535.tgz.2021_08_01-03.00.01  ( Y/M/D/)


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

if ! [[ $4 =~ ^[0-9a-zA-Z._-]+$ ]]; then
    # Checks whether valid characters exist
    echo "bad file name";
    exit
fi

if ! [[ $2 =~ ^[0-9a-zA-Z._-\/\ ]+$ ]]; then
    # Checks whether valid characters exist
    echo "supicious path";
    exit
fi



_file="$4.$_now"

echo "file:  $_file"



# echo $_dirs
# disable globbing to create find and aws command
set -f

_find_cmd="find $_dirs -type f -name $_glob  -print0 | xargs -0 tar cfvzP /$_local_dir/$_file"

echo $_find_cmd

_aws_cmd="aws s3 cp /$_local_dir/$_file s3://$_bucket/$_file"


eval $_find_cmd

echo "glob filter: $1"


echo $_aws_cmd

eval $_aws_cmd
