#!/usr/bin/python
#################################################################################
#  EC2 server backup daily retenttion job
#  removes backups older than day specified in local cache
#
#  ec2_local_backup_retention.py --days 10 --dir /var/backup  --prefix db_bk.tgz
#################################################################################
import sys
import os
import pytz
from datetime import datetime, timezone, timedelta
import argparse


def app_run():
    parser = argparse.ArgumentParser(description='EC2 local Backup retention')
    parser.add_argument('--days', help='days to retain ')
    parser.add_argument('--dir', help='Linux EC2 server dir')
    parser.add_argument(
        '--backup_prefix', help="daily backup file prefix - use \'myback\' not \'myback*\'")
    parser.add_argument(
        '--suffix', help="daily backup file suffix - use 'xls' not '*.xls'")
    parser.add_argument('--dry_run', action="store_true",
                        help='dry-run for testing')
    args = parser.parse_args()
    # special arg processing if necessary

    def check_args():
        days_specifed = None
        file_prefix = ""
        my_dir = ""
        dry_run = False
        if (args.dry_run):
            dry_run = True
        if (args.days):
            days_specifed = int(args.days)
        else:
            days_specifed = 10
        file_prefix = args.backup_prefix
        file_suffix = args.suffix
        if file_prefix is None:
            file_prefix = " "
        if file_suffix is None:
            file_suffix = "... not specified"
        my_dir = args.dir
        return days_specifed, file_prefix, my_dir, dry_run, file_suffix
    #
    days_specifed, file_prefix, my_dir, dry_run, file_suffix = check_args()
    if my_dir == None:
        print("No dir specified - see -h for commands")
        sys.exit(4)

    today = datetime.now(timezone.utc)
    retention_period = today - timedelta(days=days_specifed)

    # main_entry_point
    process_ec2_dir(days_specifed, file_prefix, file_suffix, my_dir,
                    dry_run, today, retention_period)

    return


def process_ec2_dir(days_specifed, file_prefix, suffix, my_dir, dry_run, today, retention_period):

    def print_parms(file_prefix, suffix, my_dir, today, retention_period):
        print("today's date is ", today)
        print("Start of retention period (days) ", retention_period)
        print("EC2 server dir:  ", my_dir)
        print("backup prefix: ", file_prefix)
        print("backup suffix: ", suffix)
        return

    def delete_files(dry_run, delete_candidate_list):
        for obj in delete_candidate_list:
            print("Deleting:  ", obj)
            if (dry_run == False):
                os.remove(obj)
        return

    def deletion_summary(delete_candidate_list):
        if (len(delete_candidate_list) > 0):
            print("Number of files to delete: ", len(delete_candidate_list))
            print("deleting older files")
        return

    def get_dir(my_dir):
        objects = os.listdir(my_dir)
        os.chdir(my_dir)
        return objects

    def get_file_timestamp(utc, o):
        o_time = datetime.fromtimestamp(os.stat(o).st_ctime)
        o_time = utc.localize(o_time)
        return o_time

    def filter_dir_obj(days_specifed, file_prefix, suffix, my_dir, retention_period, filter_lists):
        found_candidate_list = filter_lists[1]
        delete_candidate_list = filter_lists[0]
        objects = get_dir(my_dir)
        utc = pytz.UTC
        for o in objects:
            o_time = get_file_timestamp(utc, o)
            # print("file: ", o, "time: ", o_time )
            if o.startswith(file_prefix) or (o.endswith(suffix)):
                
                found_candidate_list.append(o)
                if o_time < retention_period:
                    print("older than " , days_specifed, " ", end='')
                    delete_candidate_list.append(o)
                print("file: ", o, "time: ", o_time)
        return

    def list_summary(found_candidate_list):
        print("***************Summary***************")
        print("Num of objects found:  ", len(found_candidate_list))
        return

    delete_candidate_list = []
    found_candidate_list = []
    filter_lists = [delete_candidate_list, found_candidate_list]
    # main processing loop ec2 files
    print_parms(file_prefix, suffix, my_dir, today, retention_period)
    filter_dir_obj(days_specifed, file_prefix, suffix, my_dir,
                   retention_period, filter_lists)
    list_summary(found_candidate_list)
    deletion_summary(delete_candidate_list)
    delete_files(dry_run, delete_candidate_list)
    return


if __name__ == "__main__":
    app_run()
