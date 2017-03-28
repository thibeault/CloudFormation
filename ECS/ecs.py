from troposphere import Base64, Join
from troposphere import Ref, Template, Parameter, Tags, FindInMap
from troposphere.cloudformation import Init, InitConfig, InitFiles, InitFile
from troposphere.cloudformation import InitServices, InitService
from troposphere.iam import PolicyType
from troposphere.iam import InstanceProfile
from troposphere.iam import Role
from troposphere.ecs import Cluster
from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.autoscaling import LaunchConfiguration
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
AWS CloudFormation ECS Cluster\
""")

# Parameters
ecsClusterName_param = t.add_parameter(Parameter(
    "ECSClusterName",
    Description="ECS Cluster Name",
    Default=data['ClusterInfo']['Name'],
    Type="String"
))


# Creating the ECS Cluster (using the name provided when running CloudFormation.
ECSCluster = t.add_resource(Cluster(
    'ECSCluster',
    ClusterName=Ref(ecsClusterName_param),
))



# Amazon EC2 Launch Configuration
ContainerInstances = t.add_resource(LaunchConfiguration(
    'ContainerInstances',
    Metadata=Metadata(
        Init({
            'config': InitConfig(
                files=InitFiles({
                    '/etc/cfn/cfn-hup.conf': InitFile(
                        content=Join('', ['[main]\n', 'stack=', Ref('AWS::StackId'),  # NOQA
                                          '\n', 'region=', Ref('AWS::Region'), '\n']),  # NOQA
                        mode='000400',
                        owner='root',
                        group='root'
                    ),
                    '/etc/cfn/hooks.d/cfn-auto-reloader.conf': InitFile(
                        content=Join('', ['[cfn-auto-reloader-hook]\n',
                                          'triggers=post.update\n',
                                          'path=Resources.ContainerInstances.Metadata.AWS::CloudFormation::Init\n',  # NOQA
                                          'action=/opt/aws/bin/cfn-init -v ', '--stack ', Ref(  # NOQA
                                'AWS::StackName'), ' --resource ContainerInstances ', ' --region ', Ref('AWS::Region'), '\n',  # NOQA
                                          'runas=root\n']),
                        mode='000400',
                        owner='root',
                        group='root'
                    )},
                ),
                services=InitServices({
                    'cfn-hup': InitService(
                        ensureRunning='true',
                        enabled='true',
                        files=['/etc/cfn/cfn-hup.conf',
                               '/etc/cfn/hooks.d/cfn-auto-reloader.conf']
                    )}
                ),
                commands={
                    '01_add_instance_to_cluster': {'command': Join('',
                                                                   ['#!/bin/bash\n',  # NOQA
                                                                    'echo ECS_CLUSTER=',  # NOQA
                                                                    Ref(ecsClusterName_param),  # NOQA
                                                                    ' >> /etc/ecs/ecs.config'])},  # NOQA
                    '02_install_ssm_agent': {'command': Join('',
                                                             ['#!/bin/bash\n',
                                                              'yum -y update\n' # NOQA
                                                              ])}
                }
            )
        }
        ),
    ),
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
                          '         --resource ECSAutoScalingGroup ',
                          '         --region ',
                          Ref('AWS::Region'),
                          '\n'])),
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    KeyName=data['ClusterInfo']['KeyName'],
    SecurityGroups=SecurityGroups,
    #IamInstanceProfile=Ref('EC2InstanceProfile'),
    IamInstanceProfile=data['ClusterInfo']['IamInstanceProfile'],
    InstanceType=data['ClusterInfo']['EC2InstanceType'],
    AssociatePublicIpAddress=data['ClusterInfo']['AssociatePublicIpAddress'],
    InstanceMonitoring=data['ClusterInfo']['DetailMonitoring'],

))

# Amazon EC2 Auto Scaling Group
ECSAutoScalingGroup = t.add_resource(AutoScalingGroup(
    'ECSAutoScalingGroup',
    DesiredCapacity=data['ClusterInfo']['DesiredCapacity'],
    MinSize=data['ClusterInfo']['MinSize'],
    MaxSize=data['ClusterInfo']['MaxSize'],
    VPCZoneIdentifier=AutoScalingGroupSubnets,
    AvailabilityZones=AutoScalingGroupAvailabilityZones,
    LaunchConfigurationName=Ref('ContainerInstances'),
    Tags=[{'Key':'Name1','Value':'MyAutoScalingGroup','PropagateAtLaunch':'false'},
          {'Key':'Name','Value':'ECSInstancesEC2','PropagateAtLaunch':'true'}],
    #Tags=Tags(
    #    Name="MyAutoScalingGroup",
    #),
))

CloudWatchEC2CPUAlarm = t.add_resource(Alarm(
    "EC2CPUAlarm",
    AlarmDescription="Alarm if CPU too high or metric disappears indicating instance is down",
    EvaluationPeriods= "5",
    Statistic= "Average",
    Threshold= "10",
    Period= "60",
    AlarmActions= [Ref('EC2CPUScalingPolicy'),],
    Namespace= "AWS/EC2",
    Dimensions= [ MetricDimension(
        Name= "AutoScalingGroupName",
        Value= Ref('ECSAutoScalingGroup')
    )],
    ComparisonOperator= "GreaterThanThreshold",
    MetricName= "CPUUtilization"
))


EC2CPUScalingPolicy = t.add_resource(ScalingPolicy(
    "EC2CPUScalingPolicy",
    AdjustmentType= "ChangeInCapacity",
    AutoScalingGroupName= Ref('ECSAutoScalingGroup'),
    Cooldown= "100",
    ScalingAdjustment= "1",
))

print(t.to_json())
#print("OK!!!")