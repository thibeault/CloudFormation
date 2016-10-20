

CIDRLookup = {
    'all': '0.0.0.0/0',
    'cidr': '10.15.0.0/19',
    'NatHA': 'No'
}

# Defining our public subnets,
# note that each AWS accounts may have different names for Availability Zone, you may have
# us-east-1b where in my account I don't. So make sure update with AZ that match what you have on your account.
PublicSubnetsData = [
    {
        "CidrBlock": "10.15.0.0/24",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1a",
        "MapPublicIpOnLaunch": "true",
        "Network": "Public"
    }, {
        "CidrBlock": "10.15.1.0/24",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1c",
        "MapPublicIpOnLaunch": "true",
        "Network": "Public"
    }, {
        "CidrBlock": "10.15.2.0/24",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1d",
        "MapPublicIpOnLaunch": "true",
        "Network": "Public"
    }, {
        "CidrBlock": "10.15.3.0/24",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1e",
        "MapPublicIpOnLaunch": "true",
        "Network": "Public"
    }
]

# Defining our private subnets,
# note that each AWS accounts may have different names for Availability Zone, you may have
# us-east-1b where in my account I don't. So make sure update with AZ that match what you have on your account.
PrivateSubnetsData = [
    {
        "CidrBlock": "10.15.7.0/22",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1a",
        "MapPublicIpOnLaunch": "false",
        "Network": "Private"
    }, {
        "CidrBlock": "10.15.11.0/22",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1c",
        "MapPublicIpOnLaunch": "false",
        "Network": "Private"
    }, {
        "CidrBlock": "10.15.15.0/22",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1d",
        "MapPublicIpOnLaunch": "false",
        "Network": "Private"
    }, {
        "CidrBlock": "10.15.19.0/22",
        "Name": "ECS",
        "AvailabilityZone": "us-east-1e",
        "MapPublicIpOnLaunch": "false",
        "Network": "Private"
    }
]


AllSubnetsData = PrivateSubnetsData + PublicSubnetsData

