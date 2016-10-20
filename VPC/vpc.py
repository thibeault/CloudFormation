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
from fonctions import addNatGateway, addSubnetRouteTableAssociation, addRouteToRouteTable, addNaclEntry, addSubnetNaclAssociation, addSubnet

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

NatGatewayArray = [addNatGateway(t, pub_subnet, CIDRLookup['all'], [priv_subnet for priv_subnet in PrivateSubnets if priv_subnet.AvailabilityZone == pub_subnet.AvailabilityZone][0]) for pub_subnet in PublicSubnets]



# us-east-1a
# us-east-1c
# us-east-1d
# us-east-1e



#print(NatGatewayArray)
print(t.to_json())