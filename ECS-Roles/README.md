# Create ECS Cluster roles and ECS Spot Fleet Role


## EC2 Cluster

    "EcsClusterRoleName": "EDEEcsClusterRole",
    "ecsManagedPolicyArns": ["arn:aws:iam::aws:policy/AmazonEC2ContainerServiceFullAccess"],
    "ecsPrincipalService": "ec2.amazonaws.com",
    "EcsSpotFleetRoleName": "EDEEcsSpotFleetRole",
    "spotFleetManagedPolicyArns": ["arn:aws:iam::aws:policy/service-role/AmazonEC2SpotFleetRole"],
    "spotFleetPrincipalService": "spotfleet.amazonaws.com"

Need to add some better info here

just run: 
```bash
python roles.py confg/roles-config.json > myECSRoles.json

## use this bash script to create or update the stack, it will return exit(1) on failure and loop until it's completed
## very useful if run within Jenkins... 
## $1 == file of the Cloud formation json
## $2 == aws profile name
## $3 == aws region, ex: us-east-1
## $4 == Name of the Cloud Formation Stack
./create-update.sh myECSRoles.json default us-east-1  ecs-dev-Roles

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
