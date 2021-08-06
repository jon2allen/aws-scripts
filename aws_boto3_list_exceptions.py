#!/usr/bin/python
#################################################################
#  List all exceptions in boto3 library for aws.
#################################################################
import botocore
import boto3
import pprint
list1 = [e for e in dir(botocore.exceptions) if e.endswith('Error')]
pprint.pprint(list1)