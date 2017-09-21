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
from troposphere.ec2 import Monitoring, SecurityGroups
from troposphere.autoscaling import AutoScalingGroup, Metadata, ScalingPolicy
from functions import readConfigFile
from functions import getVPC, getSecurityGroups, getSubnets, getSpotFleetRoleArn, getInstanceProfileArn
import troposphere.ec2 as ec2


# Loading the config file based on the argument passed
data = readConfigFile('filename')


## With Boto, get VPC, & Private Subnets with list of AZs
vpc = getVPC(data)

### Array to use bellow
AutoScalingGroupSubnets = []
AutoScalingGroupAvailabilityZones = []
SecurityGroups = []
SecurityGroupArray = []
NetworkInterfaces = []
SubnetIds =''
empty = ''

## get all security group from VPC matching filter from config
securityGroups = getSecurityGroups(vpc, data)

for sg in securityGroups:
    SecurityGroups.append(sg.group_id)
    SecurityGroupArray.append(ec2.SecurityGroups(GroupId=sg.group_id))

### getting subnets
subnets = getSubnets(vpc, data)

for subnet in subnets:
    AutoScalingGroupSubnets.append(subnet.id)
    AutoScalingGroupAvailabilityZones.append(subnet.availability_zone)
    if SubnetIds == empty:
        SubnetIds = subnet.id
    else :
        SubnetIds = SubnetIds + ", " + subnet.id

#print SubnetIds

NetworkInterfaces.append(ec2.NetworkInterfaces(SubnetId=subnets[0].id, DeleteOnTermination=True, DeviceIndex=0))

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
                         ['#!/bin/bash\n',
                          'echo ECS_CLUSTER=',
                           data['ClusterInfo']['Name'],
                           ' >> /etc/ecs/ecs.config\n',
                          ])),
    InstanceType=data['ClusterInfo']['EC2InstanceType'],
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    KeyName=data['ClusterInfo']['KeyName'],
    SecurityGroups=SecurityGroupArray,
    IamInstanceProfile=ec2.IamInstanceProfile(Arn=getInstanceProfileArn(data)),
    Monitoring=fleetMonitoring,
    #WeightedCapacity=data['ClusterInfo']['DesiredCapacity'],
    SubnetId=SubnetIds

)

myFleetLaunchSpecifications2 = ec2.LaunchSpecifications(
    UserData=Base64(Join('',
                         ['#!/bin/bash\n',
                          'echo ECS_CLUSTER=',
                          data['ClusterInfo']['Name'],
                          ' >> /etc/ecs/ecs.config\n',
                          ])),
    InstanceType=data['ClusterInfo']['EC2InstanceType2'],
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    KeyName=data['ClusterInfo']['KeyName'],
    SecurityGroups=SecurityGroupArray,
    IamInstanceProfile=ec2.IamInstanceProfile(Arn=getInstanceProfileArn(data)),
    Monitoring=fleetMonitoring,
    #WeightedCapacity=data['ClusterInfo']['DesiredCapacity'],
    SubnetId=SubnetIds

)



mySpotFleetRequestConfigData = ec2.SpotFleetRequestConfigData(
    LaunchSpecifications=[myFleetLaunchSpecifications,myFleetLaunchSpecifications2],
    SpotPrice="0.108",
    TargetCapacity=data['ClusterInfo']['DesiredCapacity'],
    IamFleetRole=getSpotFleetRoleArn(data),
    TerminateInstancesWithExpiration=True,
    AllocationStrategy='diversified',

)




## SpotFleet
MySpotFleet = t.add_resource(SpotFleet(
    "MySpotFleet",
    SpotFleetRequestConfigData=mySpotFleetRequestConfigData,
))






print(t.to_json())
#print("OK!!! ")
