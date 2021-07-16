#################################################################################
#  S3 backup daily retenttion job
#  removes backups older than day specified. 
#
#  aws_s3_backup_retention --days 10 --bucket testbucket  --prefix db_back.tgz
#################################################################################
import boto3
from datetime import datetime, timezone, timedelta
import pprint
import argparse

def app_run():
    parser = argparse.ArgumentParser(description='S3 Backup retention')
    parser.add_argument('--days', help='days to retain ')
    parser.add_argument('--bucket', help='S3 bucket' )
    parser.add_argument('--backup_prefix', help="daily backup file prefix - used\'myback\' not \'myback*\'" )
    parser.add_argument('--dry_run', action="store_true", help='dry-run for testin' )
    args = parser.parse_args()
    # special arg processing if necessary
    def check_args():  
        days_specifed = None
        file_prefix = ""
        my_bucket = ""   
        dry_run = False
        if (args.dry_run):
            dry_run = True
        if ( args.days):
            days_specifed = int(args.days)
        else:
            days_specifed = 10
        file_prefix = args.backup_prefix
        my_bucket = args.bucket    
        return days_specifed, file_prefix, my_bucket, dry_run
    #
    days_specifed, file_prefix, my_bucket, dry_run = check_args()
    today = datetime.now(timezone.utc)
    retention_period = today - timedelta(days = days_specifed )
     
    

    print("today's date is ", today)
    print("Start of retention period (days) ", retention_period )
    print("S3 bucket:  ", my_bucket)
    print("backup prefix", file_prefix )

    delete_candidate_list = []

    s3 = boto3.client('s3')

    objects = s3.list_objects_v2(Bucket=my_bucket, Prefix = file_prefix )

    for o in objects["Contents"]:
            print(o["Key"], " ", o["LastModified"] , " size: ", o["Size"])
            if o["LastModified"] < retention_period:
                print( "older than ", days_specifed )
                delete_candidate_list.append(o)
                
    print("deleeting older files")
    
    for obj in delete_candidate_list:
        print("Deleteing:  ", obj["Key"])
        if ( dry_run == False):
            s3.delete_object(Bucket = my_bucket, Key = obj["Key"])
    return  

    
    

if __name__ == "__main__":
   app_run()

        

        
       
     