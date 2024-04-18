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
import humanize


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
        sorted_files = sorted(
            objects, key=lambda f: os.path.getmtime(os.path.join(my_dir, f)))
        return sorted_files
        # return objects

    def get_file_timestamp(utc, o):
        o_time = datetime.fromtimestamp(os.stat(o).st_mtime)
        o_time = utc.localize(o_time)
        return o_time

    def get_file_size(o):
        try:
            # Get the file size in bytes
            file_size = os.path.getsize(o)
            return file_size
        except FileNotFoundError:
            print(f"File '{o}' not found.")
            return -1
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return -1

    def calculate_percentage_change(values):
       percentage_changes = []
       for i in range(1, len(values)):
           prev_value = values[i - 1]
           current_value = values[i]
           if prev_value != 0:
               percentage_change = ((current_value - prev_value) / prev_value) * 100 
               percentage_changes.append(percentage_change)
           else:
               # Handle division by zero (if previous value is zero)
               percentage_changes.append(0.0)
       return percentage_changes

    def list_files_found( tuple_list ):
        percent_list = [0.0]
        for t in tuple_list:
           percent_list.append(t[2])
        # print( "p: ", percent_list, "len: ", len(percent_list ) )
        t_changes = calculate_percentage_change( percent_list )
        # print( "t: ", t_changes, "len: ", len(t_changes) )
        for t in tuple_list:
            print("file: ", t[0] , "time: ", t[1], 
                " size: ", humanize.naturalsize(t[2], gnu=True),
                " size_bytes: ", t[2],
                "pchange:", f'{t_changes.pop(0):.4}', "%")
        return

    def filter_dir_obj(days_specifed, file_prefix, suffix, my_dir, retention_period, filter_lists):
        found_candidate_list = filter_lists[1]
        delete_candidate_list = filter_lists[0]
        objects = get_dir(my_dir)
        utc = pytz.UTC
        for o in objects:
            o_time = get_file_timestamp(utc, o)
            o_size = get_file_size(o)
            # print("file: ", o, "time: ", o_time )
            if o.startswith(file_prefix) or (o.endswith(suffix)):

                found_candidate_list.append((o, o_time, o_size))
                if o_time < retention_period:
                    print("file", o, "older than ", days_specifed, " " )
                    delete_candidate_list.append(o)
                #print("file: ", o, "time: ", o_time, " size: ", o_size)
        list_files_found(found_candidate_list)
        return

    def list_summary(found_candidate_list):
        print("***************Summary***************")
        print("Num of objects found:  ", len(found_candidate_list))
        return

    def fail_safe(found_canditate_list):
        if len(found_candidate_list) < 2:
            print("only one backup exist - fail safe")
            return False
        else:
            return True

    def fail_safe2(found_canditate_list, delete_candidate_list):
        my_del_list = delete_candidate_list
        if len(found_candidate_list) == len(delete_candidate_list):
            my_del_list = delete_candidate_list[1:]
            print("************************************************* ")
            print("failsafe2 - delete list and candidate are the same")
            print("removing oldest from delete list                  ")
            print("************************************************* ")
            print(" ")
        return my_del_list

    delete_candidate_list = []
    found_candidate_list = []
    filter_lists = [delete_candidate_list, found_candidate_list]
    # main processing loop ec2 files
    print_parms(file_prefix, suffix, my_dir, today, retention_period)
    filter_dir_obj(days_specifed, file_prefix, suffix, my_dir,
                   retention_period, filter_lists)
    list_summary(found_candidate_list)
    if fail_safe(found_candidate_list) == False:
        return
    delete_candidate_list = fail_safe2(
        found_candidate_list, delete_candidate_list)
    deletion_summary(delete_candidate_list)
    delete_files(dry_run, delete_candidate_list)
    return


if __name__ == "__main__":
    app_run()
