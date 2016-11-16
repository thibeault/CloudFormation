# Create basic VPC setup - AWS Scenario 2 - VPC with Public and Private Subnets (NAT)

https://drive.google.com/file/d/0B3xEJ9a0fctDY2FfZ1gxTHRoaEU/view?usp=sharing

### Install the following Python libraries 

```bash
pip install troposphere
pip install awacs
```

Update the data.py with your subnet information, note that each AWS Account has different AZ name, make sure to set yours.
Also ensure the CIDR are unique to your account. If you don't, the Stack will simply rollback and give you a message like this: "Value (us-east-1d) for parameter availabilityZone is invalid. Subnets can currently only be created in the following availability zones: us-east-1a, us-east-1b, us-east-1c, us-east-1e."

In data.py, set NatHA=Yes, to create an Availability Zone-independent architecture. It will create a NAT gateweay in each Availability Zone and configure your routing to ensure that resources use the NAT gateway in the same Availability Zone.

just run: 
```bash
python vpc.py > myVPCCloudFormation.json
```

and use the console or CLI to create your stack

### Reference

[Troposphere](https://github.com/cloudtools/troposphere)

[CloudFormation](https://aws.amazon.com/documentation/cloudformation/)
