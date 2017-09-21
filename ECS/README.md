# Create basic ECS Cluster - EC2 Autoscaling Group - Spot Fleet Autoscaling Group

Still a work in progress, I got the ECS + basic EC2 Autoscaling group done, still need to clean this up and then create
the scripts for creating the Spot Fleet autoscaling group.

The plan is to have your ECS cluster running on Spot Fleet in HA leveraging multiple instance types to be resiliant to
spot market. With a EC2 Autoscaling group setup to pickup if for some reason the Spot fleet can't self heal. 



# Create basic ECS setup -

The following are just random notes...

# IAM Role: ECS-Cluster
# Security Group: for ECS EC2
# ECS wizard run: https://console.aws.amazon.com/ecs/home#/firstRun
#
# Need VPC, Subnets, ECS-Cluster-Name (user data), ECS ami (Note user agreement need to be accepted)
#
### Roles:
# http://docs.aws.amazon.com/AmazonECS/latest/developerguide/IAMPolicyExamples.html#first-run-permissions
#
# ECS-Cluster
#    Policy: AmazonEC2ContainerServiceForEC2Role
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:CreateCluster",
        "ecs:DeregisterContainerInstance",
        "ecs:DiscoverPollEndpoint",
        "ecs:Poll",
        "ecs:RegisterContainerInstance",
        "ecs:StartTelemetrySession",
        "ecs:Submit*",
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
# Trusted Entities: The identity provider(s) ec2.amazonaws.com
#
# aws-ec2-spot-fleet-role
#     Policy: AmazonEC2SpotFleetRole
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
       "ec2:DescribeImages",
       "ec2:DescribeSubnets",
       "ec2:RequestSpotInstances",
       "ec2:TerminateInstances",
       "iam:PassRole"
        ],
    "Resource": ["*"]
  }]
}
# Trusted Entities: The identity provider(s) spotfleet.amazonaws.com
#
#
# Service IAM role
  The Amazon ECS service scheduler makes calls to the Amazon EC2 and Elastic Load Balancing APIs on your behalf to register and deregister container instances with your load balancers. If you do not have the ecsServiceRole already, we can create one for you.
 Compare: ECS_Access with new one

#
#
#Security group
 By default, your instances are accessible from any IP address. We recommend that you update the below security group ingress rule to allow access from known IP addresses only. ECS automatically opens up port 80 to facilitate access to the application or service you're running.
#
#
# Container instance IAM role
  The Amazon ECS container agent makes calls to the Amazon ECS API actions on your behalf, so container instances that run the agent require the ecsInstanceRole IAM policy and role for the service to know that the agent belongs to you. If you do not have the ecsInstanceRole already, we can create one for you.
#  Compare: ECS-Cluster - S3_Access with new one
#
#
#
#
# User Data:
#!/bin/bash
yum update -y
echo ECS_CLUSTER=ECS-Dev >> /etc/ecs/ecs.config
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# docker login -u AWS -p AQECAHjB7/i...v3pv8= -e none https://724662056237.dkr.ecr.us-east-2.amazonaws.com

#
#
#


https://drive.google.com/file/d/0B3xEJ9a0fctDY2FfZ1gxTHRoaEU/view?usp=sharing

### Install the following Python libraries 

```bash
pip install troposphere
pip install awacs
```

Update the data.py with your subnet information, note that each AWS Account has different AZ name, make sure to set yours.
Also ensure the CIDR are unique to your account. If you don't, the Stack will simply rollback and give you a message like this: "Value (us-east-1d) for parameter availabilityZone is invalid. Subnets can currently only be created in the following availability zones: us-east-1a, us-east-1b, us-east-1c, us-east-1e."


just run: 
```bash
python vpc.py > myVPCCloudFormation.json

python ecs.py config/ecs-config.json > myECSCloudFormation.json

CFTEMPLATE=$(cat  myECSCloudFormation.json)
aws --profile t-bo --region us-east-1 cloudformation create-stack --stack-name ecs-cluster --template-body "$CFTEMPLATE" --capabilities CAPABILITY_NAMED_IAM


```

and use the console or CLI to create your stack

### Reference

[Troposphere](https://github.com/cloudtools/troposphere)

[CloudFormation](https://aws.amazon.com/documentation/cloudformation/)

http://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI_launch_latest.html