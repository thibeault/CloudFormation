# Create basic ECS setup -
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
# docker login -u AWS -p AQECAHjB7/igwMg4NPwaurxSIYx4HfnxuGc/48bDwvwDpNYWZgAAAuUwggLhBgkqhkiG9w0BBwagggLSMIICzgIBADCCAscGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMmgg0+EOHgfTDPSmaAgEQgIICmCBf/pQ9gf70fH+AvP7cRGwmseQB3VH+oBw14AqckhkdsJ8alqQrYmSD1CXCWG6ThXY6eqnlLsPn7QLM7y5RQkLbRIDlhU74zXF6fOwoabTOAjqZIEjT5QWmOO6nRyoesrPObI3QEEEQ9GajttKdvuJb8rZUHr/udjK7T82A3ojzyxqOYWq4QBe8hTB5xA0TvNOx5jHoKZpssPqaR2kZA0x6/PJ0X2RiqiWjN9V+ZwEtjD1H9SVi4S3s4sf6KE5QQcQfZ45K0ajHlmzyG/8mN6D0PF3U40zKq1rf/0TnCXq48FQwHcC3axWS8XHZQZ0MNBNvmuVFGWPAJsbQk7EknqkQqypDGBKiDnXcakJcr2FTDpj0DWsGqtB1DXPwswvm2yFM07bok7JKanooRwgDAhEercMWDDVt3sro0ThE4sYiKBcYAEnqly5eQ9ErKcdqZtxT+Ct2WRNAApFOpSvIxZqYRQMsEcwP0W395hHQsPQ9ep978hqmzrOmfMTZ3whMD+MEV7G+rRzOiWJrwXJPLpalT1lKzpD4RDlC+YUCLAGqveFNEs5LIkf2J3uowO22PqcZSFz0z1hrGwum/2IeVE3+nw+m5uNkrUyfRxoOTcfqB0dCWL7blDJmY3KKXYT6ZstgFixKQci3qI9r9qgzERRFiJDASYCYvNjWzDAaa6SdJ8Cy4fhjfU39cscwGPGPWEr9HOnd/a7A6tBErWkWEWhavV69xIUtbOJklMX37d3h9kBCe8gkp/vX/P67Lil4ImOQ2nq1PrN2BVdvKPgSyobrcjS69jsx9eaS4uJtl2LQ7+VH4yna/zGVAytAES4w4rEkcr25EyF76uaFLCiwi3SBRZL1sVrTTTBVOsXMLeRu/4oCkev3pv8= -e none https://724662056237.dkr.ecr.us-east-2.amazonaws.com

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
```

and use the console or CLI to create your stack

### Reference

[Troposphere](https://github.com/cloudtools/troposphere)

[CloudFormation](https://aws.amazon.com/documentation/cloudformation/)
