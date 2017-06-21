# Create basic VPC setup - AWS Scenario 2 - VPC with Public and Private Subnets (NAT)

https://drive.google.com/file/d/0B3xEJ9a0fctDY2FfZ1gxTHRoaEU/view?usp=sharing

### Install the following Python libraries 

```bash
pip install troposphere
pip install awacs
```

Update the config/vpc-config.json with your subnet information, note that each AWS Account has different AZ name, make sure to set yours.
Also ensure the CIDR are unique to your account. If you don't, the Stack will simply rollback and give you a message like this: "Value (us-east-1d) for parameter availabilityZone is invalid. Subnets can currently only be created in the following availability zones: us-east-1a, us-east-1b, us-east-1c, us-east-1e."

In config/vpc-config.json, set NatHA=Yes, to create an Availability Zone-independent architecture. It will create a NAT gateweay in each Availability Zone and configure your routing to ensure that resources use the NAT gateway in the same Availability Zone.

just run: 
```bash
python vpc.py confg/vpc-config.json > myVPCCloudFormation.json

## use this bash script to create or update the stack, it will return exit(1) on failure and loop until it's completed
## very useful if run within Jenkins... 
## $1 == file of the Cloud formation json
## $2 == aws profile name
## $3 == aws region, ex: us-east-1
## $4 == Name of the Cloud Formation Stack
./create-update.sh myVPCCloudFormation.json default us-east-1  ecs-dev-vpc

## or just run cli yourself

CFTEMPLATE=$(cat  myVPCCloudFormation.json)
aws --profile default --region us-east-1 cloudformation create-stack --stack-name ecs-vpc --template-body "$CFTEMPLATE"


```

You can also use the console to create your stack

### Reference

[Troposphere](https://github.com/cloudtools/troposphere)

[CloudFormation](https://aws.amazon.com/documentation/cloudformation/)

Author Information
------------------
thibeault@gmail.com
