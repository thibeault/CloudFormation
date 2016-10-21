from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import Route
from troposphere.ec2 import VPCGatewayAttachment
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import VPC
from troposphere import Ref, Template, Tags, Join

from data import  CIDRInfo, PrivateSubnetsData, PublicSubnetsData
from fonctions import addRouteTable, addNatGateway, addSubnetRouteTableAssociation, addSubnet, addRouteToRouteTableIGW, addRouteToRouteTableNAT

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
    CidrBlock=CIDRInfo['cidr'],
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
PublicRouteTable = addRouteTable(t, "AllAZ","Public")


### Add a route to the internet from the Public Route Table
PublicRouteToInternetGateway = addRouteToRouteTableIGW(t, PublicRouteTable, InternetGateway, CIDRInfo['all'], "PublicRoute")

### Add all public subnets to the RouteTable
PublicRouteTableSubnetAssociations = [addSubnetRouteTableAssociation(t, subnet, PublicRouteTable) for subnet in PublicSubnets]

if "Yes" in CIDRInfo['NatHA']:
    ### to be fully HA, we need to create a NAT per AZ.
    NatGatewayArray = {}
    for pub_subnet in PublicSubnets:
        if NatGatewayArray.has_key(pub_subnet.AvailabilityZone) == False:
            ### We only need to create a NAT per AZ
            NatGatewayArray[pub_subnet.AvailabilityZone] = addNatGateway(t, pub_subnet)

    PrivateRouteTableArray = {}
    for priv_subnet in PrivateSubnets:
        if PrivateRouteTableArray.has_key(priv_subnet.AvailabilityZone) == False:
            ### We only need to create one routetable per AZ
            PrivateRouteTableArray[priv_subnet.AvailabilityZone] = addRouteTable(t, priv_subnet.AvailabilityZone,"Private")
            ### Create Route and add NATGateway and RouteTable
            addRouteToRouteTableNAT(t, PrivateRouteTableArray[priv_subnet.AvailabilityZone], NatGatewayArray[priv_subnet.AvailabilityZone], CIDRInfo['all'], "PrivateRouteToNatGateway"+priv_subnet.AvailabilityZone.replace("-", ""))
        ### Add Subnet to the Private RoteTable
        addSubnetRouteTableAssociation(t, priv_subnet, PrivateRouteTableArray[priv_subnet.AvailabilityZone])
else :
    ### Create the NAT Gateway
    NatGateway = addNatGateway(t, PublicSubnets[0])
    PrivateRouteTable = addRouteTable(t, "allAZ", "Private")
    ### Create Route and add NATGateway and RouteTable
    myprivateRoute = addRouteToRouteTableNAT(t, PrivateRouteTable, NatGateway, CIDRInfo['all'], "PrivateRouteToNatGateway")

    ### Add Subnet to the Private RoteTable
    for priv_subnet in PrivateSubnets:
        addSubnetRouteTableAssociation(t, priv_subnet, PrivateRouteTable)



print(t.to_json())
