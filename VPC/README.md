# Basic VPC setup - AWS Scenario 2 - VPC with Public and Private Subnets (NAT)

https://drive.google.com/file/d/0B3xEJ9a0fctDY2FfZ1gxTHRoaEU/view?usp=sharing

### Install the following Python libraries 

```bash
pip install troposphere
pip install awacs
```

Update the data.py with your subnet information, not that each AWS Account has different AZ name, make sure to set yours.
Also make sure the CIDR are unic to your account

just run: 
```bash
python vpc.py > myVPCCloudFormation.json
```

and use the console or CLI to create your stack

### Reference

[Troposphere](https://github.com/cloudtools/troposphere)

[CloudFormation](https://aws.amazon.com/documentation/cloudformation/)
