#!/usr/bin/python
#################################################################################
#  S3 backup daily retenttion job
#  removes backups older than day specified.
#
#  aws_s3_backup_retention --days 10 --bucket testbucket  --prefix db_back.tgz
#################################################################################
import sys
import boto3
import botocore
from datetime import datetime, timezone, timedelta
import pprint
import argparse


def app_run():
    parser = argparse.ArgumentParser(description='S3 Backup retention')
    parser.add_argument('--days', help='days to retain ')
    parser.add_argument('--bucket', help='S3 bucket')
    parser.add_argument(
        '--backup_prefix', help="daily backup file prefix - used\'myback\' not \'myback*\'")
    parser.add_argument('--dry_run', action="store_true",
                        help='dry-run for testing')
    parser.add_argument('--min', help="lower min threshold")
    args = parser.parse_args()
    # special arg processing if necessary

    def check_args():
        days_specifed = None
        file_prefix = ""
        my_bucket = ""
        dry_run = False
        if (args.dry_run):
            dry_run = True
        if (args.days):
            days_specifed = int(args.days)
        else:
            days_specifed = 10
        if (args.min):
            min_entries = int(args.min)
        else:
            min_entries = 1
        if (args.backup_prefix):
            file_prefix = args.backup_prefix
        else:
            print("Error: No prefix specified")
            sys.exit(8)
        if (args.bucket):
            my_bucket = args.bucket
        else:
            print("Error:  No bucket specified")
            sys.exit(8)
        return days_specifed, file_prefix, my_bucket, dry_run, min_entries
    #
    days_specifed, file_prefix, my_bucket, dry_run, min_entries = check_args()
    today = datetime.now(timezone.utc)
    retention_period = today - timedelta(days=days_specifed)

    del_list, found_list = process_s3_bucket(days_specifed, file_prefix, my_bucket,
                                             dry_run, today, retention_period,
                                             min_entries)
    return


def process_s3_bucket(days_specifed, file_prefix, my_bucket, dry_run, today, retention_period, min_entries):
    def s3_summary(file_prefix, my_bucket, today, retention_period):
        print("today's date is ", today)
        print("Start of retention period (days) ", retention_period)
        print("S3 bucket:  ", my_bucket)
        print("backup prefix", file_prefix)

    def s3_get_objects(s3, days_specifed, file_prefix, my_bucket, retention_period, delete_candidate_list):
        s3 = boto3.client('s3')
        list_found = []
        try:
            objects = s3.list_objects_v2(Bucket=my_bucket, Prefix=file_prefix)
        except botocore.exceptions.ParamValidationError as e:
            print("S3 Error: check bucket name and prefix: ",
                  my_bucket, ", prefix =  ", file_prefix)
            sys.exit(8)
        except botocore.exceptions.ClientError as e:
            print("Unexpected error: %s" % e)
            sys.exit(8)

        objects = s3.list_objects_v2(Bucket=my_bucket, Prefix=file_prefix)

        for o in objects["Contents"]:
            print(o["Key"], " ", o["LastModified"], " size: ", o["Size"])
            list_found.append(o["Key"])
            if o["LastModified"] < retention_period:
                print("older than ", days_specifed)
                delete_candidate_list.append(o["Key"])
        print("***************Summary***************")
        print("Num of objects found:  ", len(objects["Contents"]))
        return list_found

    def delete_summary(delete_candidate_list):
        if (len(delete_candidate_list) > 0):
            print("Number of files to delete: ", len(delete_candidate_list))
            print("deleting older files")

    def process_deletes(my_bucket, dry_run, delete_candidate_list, s3):
        for obj in delete_candidate_list:
            print("Deleting:  ", obj)
            if (dry_run == False):
                s3.delete_object(Bucket=my_bucket, Key=obj)

    def check_min_entries(min_entries, found_list):
        print( "check_min function")
        if (min_entries > len(found_list)):
            print("min_entries:" + str(min_entries))
            print("Number of items " + str(len(found_list)) +" less than min entries ")
            print("**** exiting - check backup process - may not be running")
            sys.exit(5)

    delete_candidate_list = []
    found_candidate_list = []
    s3 = boto3.client('s3')
    s3_summary(file_prefix, my_bucket, today, retention_period)
    found_candidate_list = s3_get_objects(s3, days_specifed, file_prefix, my_bucket,
                                          retention_period, delete_candidate_list)
    check_min_entries(min_entries, found_candidate_list)
    delete_summary(delete_candidate_list)
    process_deletes(my_bucket, dry_run, delete_candidate_list, s3)
    return delete_candidate_list, found_candidate_list


if __name__ == "__main__":
    app_run()
