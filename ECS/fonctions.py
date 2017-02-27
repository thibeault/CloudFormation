import json
import argparse
import boto3
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
        boto3.setup_default_session(profile_name='t-bo')
    if data['BotoInit']['RegionName']:
        boto_ec2 = boto3.resource('ec2', region_name='us-east-1')
    else:
        boto_ec2 = boto3.resource('ec2')
    return boto_ec2

## Look for the VPC matching your VpcName from the config file
def getVPC(data):
    boto_ec2 = ini_ec2_Boto(data)

    ### Creating the filter to find the VPC if name provided in config file
    vpcName = data['BotoFilterInfo']['VpcName']

    try:
        if vpcName:
            vpcfilters = [{'Name':'tag:Name', 'Values':[vpcName]}]
            VPCs = list(boto_ec2.vpcs.filter(Filters=vpcfilters))
        else:
            VPCs = list(boto_ec2.vpcs.all())

        if len(VPCs) == 1:
            return VPCs[0]
        elif len(VPCs) == 0:
            print("ERROR: Cloud not found any VPCs matching \""+data['BotoFilterInfo']['VpcName']+"\"" )
            exit(1)
        else:
            print("ERROR: Found \""+str(len(VPCs))+"\", please update the BotoFilterInfo.VpcName from your config file")
            exit(1)

    except IndexError as e:
        print("ERROR: Boto can't find the "+data['BotoFilterInfo']['VpcName']+". Is it there? [%s]" % e)
        exit(1)


### get Security attached to this vpc with group_name of data.BotoFilterInfo.SecurityGroupName
def getSecurityGroups(vpc, data):
    securityGroupFilter = data['BotoFilterInfo']['SecurityGroupName']
    if not securityGroupFilter:
        ## Using Default SG for this VPC
        securityGroupFilter = "default"

    securityGroups = list(vpc.security_groups.filter(Filters=[{"Name":"group-name", "Values":
        [securityGroupFilter]}]))

    if len(securityGroups) > 0:
        return securityGroups
    else:
        print("ERROR: Unable to find any SecurityGroup for BotoFilterInfo.SecurityGroupName: "+ securityGroupFilter)
        exit(1)


def old():
    print ("VPC id: "+vpc.id)
    securityGroupFilter = data['BotoFilterInfo']['SecurityGroupName']
    if not securityGroupFilter:
        ## Using Default SG for this VPC
        securityGroupFilter = "default"

    print("SecurityGroupFilter: "+ securityGroupFilter)

    securityGroups = vpc.security_groups.filter(Filters=[{"Name":"group-name", "Values": [securityGroupFilter]}])

    print(securityGroups[0].id)
    if len(securityGroups) == 1:
        return securityGroups[0]
    elif len(securityGroups) > 1:
        print >> sys.stderr, ("ERROR: At this time you can only have 1 security group, please update BotoFilterInfo.SecurityGroupName")
        exit(1)

### getSubnets(vpc,data):
def getSubnets(vpc, data):
    subnetfilter = [{'Name':'tag:Network', 'Values':[data['BotoFilterInfo']['SubnetName']]}]

    try:
        subnets = list(vpc.subnets.filter(Filters=subnetfilter))
        if len(subnets) > 0:
            return subnets
        else:
            print("ERROR: Unable to find any subnets with Name: "+data['BotoFilterInfo']['SubnetName'])
            exit(1)
    except IndexError as e:
        print("ERROR: Unexpected error: %s" % e)
        exit(1)