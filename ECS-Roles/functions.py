import json
import argparse
import boto3
from troposphere.iam import Role
from sys import getsizeof

### Read config file
def readConfigFile(filename):
    parser = argparse.ArgumentParser()
    parser.add_argument(filename)
    args = parser.parse_args()
    try:
        with open(args.filename) as file:
            return json.load(file)
    except ValueError:
        print("ERROR: Unable to read your JSON, please check your configuration file.")
        exit(1)

## initialize the ec2 boto3 base on what you have in your config file,
def ini_ec2_Boto(data):
    if data['BotoInit']['ProfileName']:
        boto3.setup_default_session(profile_name=data['BotoInit']['ProfileName'])
    if data['BotoInit']['RegionName']:
        boto_ec2 = boto3.resource('ec2', region_name=data['BotoInit']['RegionName'])
    else:
        boto_ec2 = boto3.resource('ec2')
    return boto_ec2



#################### Functions for roles.py ####################

def createRole(roleName, managedPolicyArns, principalService):
    role = Role(
        roleName,
        RoleName=roleName,
        Path='/',
        ManagedPolicyArns=managedPolicyArns,
        AssumeRolePolicyDocument={'Version': '2012-10-17',
                                  'Statement': [{'Action': 'sts:AssumeRole',
                                                 'Principal': {'Service': principalService},
                                                 'Effect': 'Allow',
                                                 }]}
    )
    return role
####################






