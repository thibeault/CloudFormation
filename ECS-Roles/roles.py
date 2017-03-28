#from troposphere import Base64, Join
from troposphere import Ref, Template, Parameter, Tags, FindInMap
#from troposphere.cloudformation import Init, InitConfig, InitFiles, InitFile
#from troposphere.cloudformation import InitServices, InitService
from troposphere.iam import PolicyType
from troposphere.iam import InstanceProfile
#from troposphere.iam import Role
#from troposphere.ecs import Cluster
#from troposphere.cloudwatch import Alarm, MetricDimension
#from troposphere.autoscaling import LaunchConfiguration
#from troposphere.autoscaling import AutoScalingGroup, Metadata, ScalingPolicy
from functions import readConfigFile
from functions import createRole
#import troposphere.ec2 as ec2


# Loading the config file based on the argument passed
data = readConfigFile('filename')

t = Template()
t.add_version('2010-09-09')

################### Getting values from config file ####################
EcsClusterRole = 'TedEcsClusterRole'
ecsManagedPolicyArns = ['arn:aws:iam::aws:policy/AmazonEC2ContainerServiceFullAccess']
ecsPrincipalService = 'ec2.amazonaws.com'

EcsSpotFleetRole = 'TedEcsSpotFleetRole'
spotFleetManagedPolicyArns=['arn:aws:iam::aws:policy/service-role/AmazonEC2SpotFleetRole']
spotFleetPrincipalService = 'spotfleet.amazonaws.com'
####################



t.add_description("""\
AWS CloudFormation ECS Cluster EC2 & Spot Fleet Roles\
""")



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
    Roles=[Ref(EcsClusterRole)],
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
    Roles=[Ref(EcsClusterRole)],
))

# Policy Amazon CloudWatch - Enable our ECS Cluster/EC2 to send data to CloudWatch
# TODO: update policy to only allow to work with specific cluster we are creating vs "Resource: *"
PolicyCloudwatch = t.add_resource(PolicyType(
    'PolicyCloudwatch',
    PolicyName='Cloudwatch',
    PolicyDocument={'Version': '2012-10-17',
                    'Statement': [{'Action': ['cloudwatch:*'], 'Resource': '*',
                                   'Effect': 'Allow'}]},
    Roles=[Ref(EcsClusterRole)],
))

# Role our EC2 instance will take on to work with ECR, ECS and CloudWatch
EcsClusterRole = t.add_resource(createRole(EcsClusterRole, ecsManagedPolicyArns, ecsPrincipalService))



# Linking our EC2 with the Role
EC2InstanceProfile = t.add_resource(InstanceProfile(
    'EC2InstanceProfile',
    Path='/',
    Roles=[Ref(EcsClusterRole)],
))



SpotFleetRole = t.add_resource(createRole(EcsSpotFleetRole, spotFleetManagedPolicyArns, spotFleetPrincipalService))


print(t.to_json())