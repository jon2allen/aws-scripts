#################################################################################
#  S3 backup daily retenttion job
#  removes backups older than day specified. 
#
#  aws_s3_backup_retention --days 10 --bucket testbucket  --prefix db_back.tgz
#################################################################################
import boto3
import os, pytz
from datetime import datetime, timezone, timedelta
import pprint
import argparse

from botocore.exceptions import ServiceNotInRegionError

class objRetention:
    def __init__(self, service, period, location, prefix):
        self.service = service
        self.period = period
        self.location = location
        self.prefix = prefix
        self.period_interval = "d"
        self.obj_list = []
        self.delete_list = []
    def list_obs(self):
        pass
    def delete_candidate(self):
        pass
    def process_deletes(self):
        pass
      
    

def app_run():
    parser = argparse.ArgumentParser(description='EC2 local Backup retention')
    parser.add_argument('--days', help='days to retain ')
    parser.add_argument('--dir', help='Linux EC2 server dir' )
    parser.add_argument('--backup_prefix', help="daily backup file prefix - used\'myback\' not \'myback*\'" )
    parser.add_argument('--dry_run', action="store_true", help='dry-run for testing' )
    args = parser.parse_args()
    # special arg processing if necessary
    def check_args():  
        days_specifed = None
        file_prefix = ""
        my_dir = ""   
        dry_run = False
        if (args.dry_run):
            dry_run = True
        if ( args.days):
            days_specifed = int(args.days)
        else:
            days_specifed = 10
        file_prefix = args.backup_prefix
        my_dir = args.dir  
        return days_specifed, file_prefix, my_dir, dry_run
    #
    days_specifed, file_prefix, my_dir, dry_run = check_args()
    today = datetime.now(timezone.utc)
    retention_period = today - timedelta(days = days_specifed )
     
    

    print("today's date is ", today)
    print("Start of retention period (days) ", retention_period )
    print("EC2 server dir:  ", my_dir)
    print("backup prefix", file_prefix )

    delete_candidate_list = []
    found_candidate_list = []

    objects = os.listdir(my_dir)
    
    os.chdir(my_dir)
    utc=pytz.UTC
    
    for o in objects:
        o_time = datetime.fromtimestamp(os.stat(o).st_ctime)
        #o_time = time.ctime(os.stat(o).st_ctime)
        o_time = utc.localize(o_time)
        # print("file: ", o, "time: ", o_time ) 
        if o.startswith(file_prefix):
            print("file: ", o, "time: ", o_time )
            found_candidate_list.append(o)
            if o_time < retention_period:
                print("older than ", days_specifed )
                delete_candidate_list.append(o)  
    
    print("***************Summary***************")
    print("Num of objects found:  ", len(found_candidate_list))            
                  
    if ( len( delete_candidate_list) > 0 ):
        print ( "Number of files to delete: " , len(delete_candidate_list))
        print("deleting older files")      

    for obj in delete_candidate_list:
        print("Deleting:  ", obj )
        if ( dry_run == False):
            os.remove(obj)
    return  

if __name__ == "__main__":
   app_run()

        

        
       
     