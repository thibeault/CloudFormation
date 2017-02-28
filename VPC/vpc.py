from troposphere import Parameter
from troposphere import Ref
from troposphere import Tags
from troposphere import Template
from troposphere.ec2 import VPCGatewayAttachment
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import VPC
from functions import readConfigFile
from functions import addRouteTable
from functions import addNatGateway
from functions import addSubnetRouteTableAssociation
from functions import addSubnet
from functions import addRouteToRouteTableIGW
from functions import addRouteToRouteTableNAT

# Loading the config file based on the argument passed
data = readConfigFile('filename')

t = Template()
t.add_version('2010-09-09')

t.add_description("""\
AWS CloudFormation Template VPC with Public and Private Subnets following AWS Scenario 2\
""")


# Parameters
vpcName_param = t.add_parameter(Parameter(
    "VpcName",
    Description="VPC for %s environment" % data['EnvInfo']['Name'],
    Default="%s-VPC" % data['EnvInfo']['Name'],
    Type="String"
))


### Create the VPC, with Name from Parameter and CIDR from the defined environment
VPC = t.add_resource(VPC(
    "VPC",
    EnableDnsSupport="true",
    CidrBlock=data['CIDRInfo']['cidr'],
    EnableDnsHostnames="true",
    Tags=Tags(**{
        'Name': '%s' % data['Tags']['Name'],
        'Env': '%s' % data['Tags']['Env'],
        'Owner': '%s' % data['Tags']['Owner']
    })
))

### Create Internet Gateway for VPC, to enable VMs to access Internet
InternetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(**{
        'Name': '%s - Public Network IGW' % data['EnvInfo']['Name'],
        'Env': '%s' % data['Tags']['Env'],
        'Owner': '%s' % data['Tags']['Owner']
    })
))

### Attached InternetGateway to the VPC
VPCGatewayAttachment = t.add_resource(VPCGatewayAttachment(
    "VPCGatewayAttachment",
    VpcId=Ref("VPC"),
    InternetGatewayId=Ref("InternetGateway"),
))

### Create Private Subnets from json with addSubnet from functions.py
PrivateSubnets = [addSubnet(t, data['Tags']['Env'], data['Tags']['Owner'], **SubnetData) for SubnetData in data['PrivateSubnetsData']]

### Create Public Subnets from json with addSubnet from functions.py
PublicSubnets = [addSubnet(t, data['Tags']['Env'], data['Tags']['Owner'], **SubnetData) for SubnetData in data['PublicSubnetsData']]

### Create Public Route Table for all Public Subnets
### We are using the same route table for all public subnets
PublicRouteTable = addRouteTable(t, "AllAZ","Public",data['Tags']['Env'],data['Tags']['Owner'])


### Add a route to the internet from the Public Route Table
PublicRouteToInternetGateway = addRouteToRouteTableIGW(t, PublicRouteTable, InternetGateway, data['CIDRInfo']['all'],
                                                       "PublicRoute")

### Add all public subnets to the RouteTable
PublicRouteTableSubnetAssociations = [addSubnetRouteTableAssociation(t, subnet, PublicRouteTable)
                                      for subnet in PublicSubnets]

if "Yes" in data['CIDRInfo']['NatHA']:
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
            PrivateRouteTableArray[priv_subnet.AvailabilityZone] = addRouteTable(t, priv_subnet.AvailabilityZone,
                                                                                 "Private",data['Tags']['Env'],
                                                                                 data['Tags']['Owner'])
            ### Create Route and add NATGateway and RouteTable
            addRouteToRouteTableNAT(t, PrivateRouteTableArray[priv_subnet.AvailabilityZone],
                                    NatGatewayArray[priv_subnet.AvailabilityZone], data['CIDRInfo']['all'],
                                    "PrivateRouteToNatGateway"
                                    +priv_subnet.AvailabilityZone.replace("-", ""))
        ### Add Subnet to the Private RoteTable
        addSubnetRouteTableAssociation(t, priv_subnet, PrivateRouteTableArray[priv_subnet.AvailabilityZone])
else :
    ### CIDRInfo['NatHA'] = No so we don't need to have NAT HA, we will only create 1 NAT gateway and have
    ### all private subnet point to it.

    ### Create the NAT Gateway
    NatGateway = addNatGateway(t, PublicSubnets[0])
    PrivateRouteTable = addRouteTable(t, "allAZ", "Private",data['Tags']['Env'],data['Tags']['Owner'])
    ### Create Route and add NATGateway and RouteTable
    myprivateRoute = addRouteToRouteTableNAT(t, PrivateRouteTable, NatGateway, data['CIDRInfo']['all'],
                                             "PrivateRouteToNatGateway")

    ### Add Subnet to the Private RoteTable
    for priv_subnet in PrivateSubnets:
        addSubnetRouteTableAssociation(t, priv_subnet, PrivateRouteTable)

print(t.to_json())
