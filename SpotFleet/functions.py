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
        boto3.setup_default_session(profile_name=data['BotoInit']['ProfileName'])
    if data['BotoInit']['RegionName']:
        boto_ec2 = boto3.resource('ec2', region_name=data['BotoInit']['RegionName'])
    else:
        boto_ec2 = boto3.resource('ec2')
    return boto_ec2

## initialize the ec2 boto3 base on what you have in your config file,
def ini_iam_Boto(data):
    if data['BotoInit']['ProfileName']:
        boto3.setup_default_session(profile_name=data['BotoInit']['ProfileName'])
    if data['BotoInit']['RegionName']:
        boto_iam = boto3.client('iam', region_name=data['BotoInit']['RegionName'])
    else:
        boto_iam = boto3.client('iam')

    return boto_iam

## Look for the RoleArn matching your RoleName from the config file
def getSpotFleetRoleArn(data):

    if data["ClusterInfo"]["IamFleetRoleArn"]:
        return data["ClusterInfo"]["IamFleetRoleArn"]


    boto_iam = ini_iam_Boto(data)

    ### Creating the filter to find the VPC if name provided in config file
    roleName = data['BotoFilterInfo']['EcsSpotFleetRoleName']

    try:
        if roleName:
            try:
                role = boto_iam.get_role(RoleName=roleName)
            except:
                role = ""

        if role == "":
            print("ERROR: Cloud not found any Role matching \""+data['BotoFilterInfo']['RoleName']+"\"" )
            exit(1)
        else:
            return role["Role"]["Arn"]

    except IndexError as e:
        print("ERROR: Boto can't find the "+data['BotoFilterInfo']['RoleName']+". Is it there? [%s]" % e)
        exit(1)

## Look for the instance_profile for role matching your RoleName from the config file
def getInstanceProfileArn(data):
    if data["ClusterInfo"]["IamInstanceProfileArn"]:
        return data["ClusterInfo"]["IamInstanceProfileArn"]

    boto_iam = ini_iam_Boto(data)

    ### Creating the filter to find the VPC if name provided in config file
    roleName = data['BotoFilterInfo']['EcsClusterRoleName']

    try:
        if roleName:
            try:
                roles = boto_iam.list_instance_profiles_for_role(RoleName=roleName)
            except:
                raise

        if len(list(roles["InstanceProfiles"])) == 1:
            return roles["InstanceProfiles"][0]["Arn"]
        else:
            print("ERROR: Found ["+str(len(list(roles["InstanceProfiles"])))+"] InstanceProfile for Role: "+roleName)
            exit(1)

    except IndexError as e:
        print("ERROR: Boto can't find InstanceProfiles for the role "+data['BotoFilterInfo']['RoleName']+". Is it there? [%s]" % e)
        exit(1)


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


### getSubnets(vpc,data):
def getSubnets(vpc, data):
    subnetfilter = [{'Name':'tag:Network', 'Values':[data['BotoFilterInfo']['SubnetName']]}]

    try:
        if data['BotoFilterInfo']['SubnetName']:
            subnets = list(vpc.subnets.filter(Filters=subnetfilter))
        else:
            subnets = list(vpc.subnets.all())
        if len(subnets) > 0:
            return subnets
        else:
            print("ERROR: Unable to find any subnets with Name: "+data['BotoFilterInfo']['SubnetName'])
            exit(1)
    except IndexError as e:
        print("ERROR: Unexpected error: %s" % e)
        exit(1)