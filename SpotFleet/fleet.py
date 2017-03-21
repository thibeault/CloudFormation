from troposphere import Base64, Join
from troposphere import Ref, Template, Parameter, Tags, FindInMap
from troposphere.cloudformation import Init, InitConfig, InitFiles, InitFile
from troposphere.cloudformation import InitServices, InitService
from troposphere.iam import PolicyType
from troposphere.iam import InstanceProfile
from troposphere.iam import Role
from troposphere.ecs import Cluster
from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.ec2 import SpotFleet
from troposphere.ec2 import Monitoring
from troposphere.autoscaling import AutoScalingGroup, Metadata, ScalingPolicy
from functions import readConfigFile
from functions import getVPC, getSecurityGroups, getSubnets
import troposphere.ec2 as ec2


# Loading the config file based on the argument passed
data = readConfigFile('filename')


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
    AutoScalingGroupAvailabilityZones.append(subnet.availability_zone)

#print(str(AutoScalingGroupSubnets))
#print(str(AutoScalingGroupAvailabilityZones))
#print(str(SecurityGroups))


t = Template()
t.add_version('2010-09-09')

t.add_mapping('RegionMap', data["RegionMap"])


t.add_description("""\
AWS CloudFormation EC2 Spot Fleet\
""")


fleetMonitoring = ec2.Monitoring(Enabled=data['ClusterInfo']['DetailMonitoring'])

myFleetLaunchSpecifications = ec2.LaunchSpecifications(
    UserData=Base64(Join('',
                         ['#!/bin/bash -xe\n',
                          'yum install -y aws-cfn-bootstrap\n',
                          '/opt/aws/bin/cfn-init -v ',
                          '         --stack ',
                          Ref('AWS::StackName'),
                          '         --resource ContainerInstances ',
                          '         --region ',
                          Ref('AWS::Region'),
                          '\n',
                          '/opt/aws/bin/cfn-signal -e $? ',
                          '         --stack ',
                          Ref('AWS::StackName'),
                          '         --resource LaunchSpecifications ',
                          '         --region ',
                          Ref('AWS::Region'),
                          '\n',
                          'echo ECS_CLUSTER=',  # NOQA
                           data['ClusterInfo']['Name'],  # NOQA
                           ' >> /etc/ecs/ecs.config',
                          ])),
    InstanceType=data['ClusterInfo']['EC2InstanceType'],
    KeyName=data['ClusterInfo']['KeyName'],
    #SecurityGroups=SecurityGroups[0],
    #IamInstanceProfile=Ref('EC2InstanceProfile'),
    ImageId="ami-40286957",
    Monitoring=fleetMonitoring,
    WeightedCapacity=data['ClusterInfo']['DesiredCapacity'],

)

mySpotFleetRequestConfigData = ec2.SpotFleetRequestConfigData(
    LaunchSpecifications=[myFleetLaunchSpecifications],
    SpotPrice="0.067",
    TargetCapacity=data['ClusterInfo']['DesiredCapacity'],
    IamFleetRole="arn:aws:iam::724662056237:role/aws-ec2-spot-fleet-role",
    TerminateInstancesWithExpiration=True,
)

## SpotFleet
MySpotFleet = t.add_resource(SpotFleet(
    "MySpotFleet",
    SpotFleetRequestConfigData=mySpotFleetRequestConfigData,
))






print(t.to_json())
#print("OK!!!")
