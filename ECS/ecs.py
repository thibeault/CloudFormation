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

from data import  ClusterInfo

## move config in json
## with Boto, get VPC, & Private Subnets with list of AZs
## with boto get SecurityGroups under VPC, find one with tag X if Tag X is not null


t = Template()
t.add_version('2010-09-09')

t.add_mapping('RegionMap', {
    "us-east-1": {"AMI": "ami-6df8fe7a"},
    "us-east-2": {"AMI": "ami-c6b5efa3"},
    "us-west-1": {"AMI": "ami-1eda8d7e"},
    "us-west-2": {"AMI": "ami-a2ca61c2"},
    "eu-west-1": {"AMI": "ami-ba346ec9"},
    "eu-west-2": {"AMI": "ami-42c5cf26"},
    "eu-central-1": {"AMI": "ami-e012d48f"},
    "ap-northeast-1": {"AMI": "ami-08f7956f"},
    "ap-southeast-1": {"AMI": "ami-f4832f97"},
    "ap-southeast-2": {"AMI": "ami-774b7314"},
    "ca-central-1": {"AMI": "ami-be45f7da"}
})


t.add_description("""\
AWS CloudFormation ECS Cluster\
""")

# Parameters
ecsClusterName_param = t.add_parameter(Parameter(
    "ECSClusterName",
    Description="ECS Cluster Name",
    Default=ClusterInfo['Name'],
    Type="String"
))


# Creating the ECS Cluster (using the name provided when running CloudFormation.
ECSCluster = t.add_resource(Cluster(
    'ECSCluster',
    ClusterName=Ref(ecsClusterName_param),
))


# Policy Amazon EC2 Container Registry - Enable our ECS Cluster to work with the ECR
PolicyEcr = t.add_resource(PolicyType(
    'PolicyEcr',
    PolicyName='EcrPolicy',
    PolicyDocument={'Version': '2012-10-17',
                    'Statement': [{'Action': ['ecr:GetAuthorizationToken'],
                                   'Resource': ['*'],
                                   'Effect': 'Allow'},
                                  {'Action': ['ecr:GetDownloadUrlForLayer',
                                              'ecr:BatchGetImage',
                                              'ecr:BatchCheckLayerAvailability'
                                              ],
                                   'Resource': [
                                       '*'],
                                   'Effect': 'Allow',
                                   'Sid': 'AllowPull'},
                                  ]},
    Roles=[Ref('EcsClusterRole')],
))

# Policy Amazon EC2 Container Service - Enable our EC2 to work with ECS Cluster
# TODO: update policy to only allow to work with specific cluster we are creating vs "Resource: *"
PolicyEcs = t.add_resource(PolicyType(
    'PolicyEcs',
    PolicyName='EcsPolicy',
    PolicyDocument={'Version': '2012-10-17',
                    'Statement': [
                        {'Action': ['ecs:CreateCluster',
                                    'ecs:RegisterContainerInstance',
                                    'ecs:DeregisterContainerInstance',
                                    'ecs:DiscoverPollEndpoint',
                                    'ecs:Submit*',
                                    'ecs:Poll',
                                    'ecs:StartTelemetrySession'],
                         'Resource': '*',
                         'Effect': 'Allow'}
                    ]},
    Roles=[Ref('EcsClusterRole')],
))

# Policy Amazon CloudWatch - Enable our ECS Cluster/EC2 to send data to CloudWatch
# TODO: update policy to only allow to work with specific cluster we are creating vs "Resource: *"
PolicyCloudwatch = t.add_resource(PolicyType(
    'PolicyCloudwatch',
    PolicyName='Cloudwatch',
    PolicyDocument={'Version': '2012-10-17',
                    'Statement': [{'Action': ['cloudwatch:*'], 'Resource': '*',
                                   'Effect': 'Allow'}]},
    Roles=[Ref('EcsClusterRole')],
))

# Role our EC2 instance will take on to work with ECR, ECS and CloudWatch
EcsClusterRole = t.add_resource(Role(
    'EcsClusterRole',
    RoleName='EcsClusterRole',
    Path='/',
    ManagedPolicyArns=[
        'arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM'
    ],
    AssumeRolePolicyDocument={'Version': '2012-10-17',
                              'Statement': [{'Action': 'sts:AssumeRole',
                                             'Principal': {'Service': 'ec2.amazonaws.com'},
                                             'Effect': 'Allow',
                                             }]}
))

# Linking our EC2 with the Role
EC2InstanceProfile = t.add_resource(InstanceProfile(
    'EC2InstanceProfile',
    Path='/',
    Roles=[Ref('EcsClusterRole')],
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
                                                                    Ref('ECSCluster'),  # NOQA
                                                                    ' >> /etc/ecs/ecs.config'])},  # NOQA
                    '02_install_ssm_agent': {'command': Join('',
                                                             ['#!/bin/bash\n',
                                                              'yum -y update\n',  # NOQA
                                                              'curl https://amazon-ssm-eu-west-1.s3.amazonaws.com/latest/linux_amd64/amazon-ssm-agent.rpm -o amazon-ssm-agent.rpm\n',  # NOQA
                                                              'yum install -y amazon-ssm-agent.rpm'  # NOQA
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
    KeyName=ClusterInfo['KeyName'],
    SecurityGroups=ClusterInfo['SecurityGroups'],
    IamInstanceProfile=Ref('EC2InstanceProfile'),
    InstanceType=ClusterInfo['EC2InstanceType'],
    AssociatePublicIpAddress=ClusterInfo['AssociatePublicIpAddress'],
    InstanceMonitoring=ClusterInfo['DetailMonitoring'],

))

# Amazon EC2 Auto Scaling Group
ECSAutoScalingGroup = t.add_resource(AutoScalingGroup(
    'ECSAutoScalingGroup',
    DesiredCapacity=ClusterInfo['DesiredCapacity'],
    MinSize=ClusterInfo['MinSize'],
    MaxSize=ClusterInfo['MaxSize'],
    VPCZoneIdentifier=ClusterInfo['AutoScalingGroupSubnets'],
    #AvailabilityZones=ClusterInfo['AutoScalingGroupAvailabilityZones'],
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
