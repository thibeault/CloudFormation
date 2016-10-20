from troposphere import Base64, FindInMap, GetAtt, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import Route
from troposphere.ec2 import RouteTable
from troposphere.ec2 import SubnetRouteTableAssociation
from troposphere.ec2 import VPCGatewayAttachment
from troposphere.ec2 import Subnet
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import NatGateway
from troposphere.ec2 import EIP
from troposphere.ec2 import VPC
from troposphere import ec2
from troposphere import Ref, Template, Tags, Join

from data import  CIDRLookup, PrivateSubnetsData, PublicSubnetsData, AllSubnetsData
from fonctions import addRouteTable, addNatGateway, addSubnetRouteTableAssociation, addRouteToRouteTable, addNaclEntry, addSubnetNaclAssociation, addSubnet

t = Template()

t.add_description("""\
AWS CloudFormation Template VPC with Public and Private Subnets following AWS Scenario 2\
""")


# Parameters
vpcName_param = t.add_parameter(Parameter(
    "VpcName",
    Description="VPC Name",
    Default="TestVPC",
    Type="String"
))


### Create the VPC, with Name from Parameter and CIDR from data.py
VPC = t.add_resource(VPC(
    "VPC",
    EnableDnsSupport=True,
    CidrBlock=CIDRLookup['cidr'],
    EnableDnsHostnames=True,
    Tags=Tags(
        Name=Ref("AWS::StackName")
    )
))

### Create Internet Gateway for VPC, to enable VMs to access Internet
InternetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(
        Name=Ref("AWS::StackName")
    )
))

### Attached InternetGateway to the VPC
VPCGatewayAttachment = t.add_resource(VPCGatewayAttachment(
    "VPCGatewayAttachment",
    VpcId=Ref("VPC"),
    InternetGatewayId=Ref("InternetGateway"),
))

### Create Private Subnets from data.py with addSubnet from functions.py
PrivateSubnets = [addSubnet(t, **SubnetData) for SubnetData in PrivateSubnetsData]

### Create Public Subnets from data.py with addSubnet from functions.py
PublicSubnets = [addSubnet(t, **SubnetData) for SubnetData in PublicSubnetsData]

### Create Public Route Table for all Public Subnets
### We are using the same route table for all public subnets
PublicRouteTable = t.add_resource(RouteTable(
    "PublicRouteTable",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("",[Ref("AWS::StackName"),"-public"])
    )
))

### Add a route to the internet from the Public Route Table
PublicRouteToInternetGateway = t.add_resource(Route(
    "PublicRouteToInternetGateway",
    DestinationCidrBlock=CIDRLookup['all'],
    GatewayId=Ref(InternetGateway),
    RouteTableId=Ref(PublicRouteTable),
))

### Add all public subnets to the RouteTable
PublicRouteTableSubnetAssociations = [addSubnetRouteTableAssociation(t, subnet, PublicRouteTable) for subnet in PublicSubnets]

#NatGatewayArray = [addNatGateway(t, pub_subnet, CIDRLookup['all'], [priv_subnet for priv_subnet in PrivateSubnets if priv_subnet.AvailabilityZone == pub_subnet.AvailabilityZone][0]) for pub_subnet in PublicSubnets]


if "Yes" in CIDRLookup['NatHA']:
    ### to be fully HA, we need to create a NAT per AZ.
    NatGatewayArray = {}
    for pub_subnet in PublicSubnets:
        NatGatewayArray[pub_subnet.AvailabilityZone] = addNatGateway(t, pub_subnet)


    PrivateRouteTableArray = {}
    for priv_subnet in PrivateSubnets:
        PrivateRouteTableArray[priv_subnet.AvailabilityZone] = addRouteTable(t, priv_subnet.AvailabilityZone,"Private")
        ### Create Route and add NATGateway and RouteTable
        t.add_resource(Route(
            "PrivateRouteToNatGateway"+priv_subnet.AvailabilityZone.replace("-", ""),
            DestinationCidrBlock=CIDRLookup['all'],
            NatGatewayId=Ref(NatGatewayArray[priv_subnet.AvailabilityZone]),
            RouteTableId=Ref(PrivateRouteTableArray[priv_subnet.AvailabilityZone]),
            ))
        ### Add Subnet to the Private RoteTable
        addSubnetRouteTableAssociation(t, priv_subnet, PrivateRouteTableArray[priv_subnet.AvailabilityZone])
else :
    ### Create the NAT Gateway
    NatGateway = addNatGateway(t, PublicSubnets[0])
    PrivateRouteTable = addRouteTable(t, "allAZ", "Private")
    ### Create Route and add NATGateway and RouteTable
    t.add_resource(Route(
        "PrivateRouteToNatGateway"+"allPrivateAZ",
        DestinationCidrBlock=CIDRLookup['all'],
        NatGatewayId=Ref(NatGateway),
        RouteTableId=Ref(PrivateRouteTable),
        ))
    ### Add Subnet to the Private RoteTable
    for priv_subnet in PrivateSubnets:
        addSubnetRouteTableAssociation(t, priv_subnet, PrivateRouteTable)



print(t.to_json())
