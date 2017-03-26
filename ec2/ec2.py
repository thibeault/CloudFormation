from troposphere import cloudformation
from troposphere import Base64, FindInMap, GetAtt
from troposphere import Parameter, Ref, Tags, Template, GetAtt, Join, Output
import troposphere.ec2 as ec2
from troposphere.route53 import RecordSetType
import argparse
import sys
import os
import boto3
import json
from functions import readConfigFile
from functions import getVPC, getSecurityGroups, getSubnets

# Loading the config file based on the argument passed
data = readConfigFile('filename')

t = Template()
t.add_version("2010-09-09")
t.add_description("CF to create %s EC2 instance(s) for %s environment" % (data['ServerInfo']['Name'],data['ServerTags']['Env']))

t.add_mapping('RegionMap', data["RegionMap"])

## With Boto, get VPC, & Private Subnets with list of AZs
vpc = getVPC(data)

### Array to use bellow
AutoScalingGroupSubnets = []
AutoScalingGroupAvailabilityZones = []
SecurityGroups = []

## get all security group from VPC matching filter from config
securityGroups = getSecurityGroups(vpc, data)

for sg in securityGroups:
    SecurityGroups.append(sg.group_id)

### getting subnets
subnets = getSubnets(vpc, data)

for subnet in subnets:
    AutoScalingGroupSubnets.append(subnet.id)
    #print(subnet.id)
    AutoScalingGroupAvailabilityZones.append(subnet.availability_zone)


# Get all instance details from json
instances = data['Instances']

#Creating instances
for instance in instances:
    servername = instance['ServerName']
    t.add_resource(ec2.Instance(
        servername,
        ImageId= FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
        #ImageId='ami-0b33d91d',
        KeyName= instance['KeyPairName'],
        SubnetId = AutoScalingGroupSubnets[0],
        SecurityGroupIds=SecurityGroups,
        Tenancy= instance['Tenancy'],
        InstanceType= instance['InstanceType'],
        UserData=Base64(Join('', [
            '#!/bin/bash\n',
            'apt-get update\n',
            'apt-get install python-pip -y \n',
            'yum install -y aws-cfn-bootstrap\n',
            '/opt/aws/bin/cfn-init -s \'',
            Ref('AWS::StackName'),
            '\' -r Ec2Instance -c ascending',
            ' --region \'',
            Ref('AWS::Region'),
            '\'\n',
        ])),
        Tags=Tags(**{
          'Name': '%s' % instance['ServerName'],
          'Env': '%s' % data['ServerTags']['Env'],
          'Owner': '%s' % data['ServerTags']['Owner'],
          'Cost Center': '%s' % data['ServerTags']['CostCenter']
        })
))


print(t.to_json())

