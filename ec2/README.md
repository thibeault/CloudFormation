EC2 Host creation
=====================

Cloudformation scripts in this directory launches ec2 instances based on the json configuration passed as an argument.


Example commands
----------------
Bastion
-------
- Generate cf template from json for bastion
```bash
python ec2.py config/bastion-dev.json > cf_bastion-ec2.template
```
- Create the bastion server with cloudformation aws cli
```bash
CFTEMPLATE=$(cat cf_bastion-ec2.template)
aws cloudformation --region us-east-1 create-stack --stack-name dev-bastion --template-body "$CFTEMPLATE"
```
- Commands to check the newly created Server
```bash
aws --profile t-bo --region us-east-2 ec2 describe-instances --filters Name=tag-value,Values=bastion,Name=tag-value,Values=BastionServer --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value | [0], InstanceId, Placement.AvailabilityZone, InstanceType, LaunchTime, State.Name, PublicDnsName]' --output table
```
- Sample output
```bash
----------------------------------------------------------------------------------------------------------------------------------------------------------------
|                                                                       DescribeInstances                                                                      |
+---------------+----------------------+-------------+-----------+---------------------------+----------+------------------------------------------------------+
|  BastionServer|  i-04dd890b7dbfa846e |  us-east-2a |  t2.micro |  2017-03-24T16:22:40.000Z |  running |  ec2-52-14-223-225.us-east-2.compute.amazonaws.com   |
+---------------+----------------------+-------------+-----------+---------------------------+----------+------------------------------------------------------+
```

Author Information
------------------
thibeault@gmail.com
