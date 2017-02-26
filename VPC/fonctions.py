from troposphere import Ref
from troposphere import Tags
from troposphere import GetAtt
from troposphere import Join
from troposphere.ec2 import Route
from troposphere.ec2 import EIP
from troposphere.ec2 import SubnetRouteTableAssociation
from troposphere.ec2 import Subnet
from troposphere.ec2 import RouteTable
from troposphere.ec2 import NatGateway
import json
import argparse

### Read config file
def readConfigFile(filename):
    parser = argparse.ArgumentParser()
    parser.add_argument(filename)
    args = parser.parse_args()
    try:
        with open(args.filename) as file:
            return json.load(file)
    except ValueError:
        print("ERROR: Unable to read your JSON, please check your configuration file.")
        exit(1)


### Add subnet to the routeTable
def addSubnetRouteTableAssociation(template, subnet, routeTable):
    return template.add_resource(
        SubnetRouteTableAssociation(
            subnet.title + routeTable.title,
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
            ))

### Create Route and add Internet Gateway to the routeTable
def addRouteToRouteTableIGW(template, routeTable, Gateway, DestinationCidrBlock, name):
    #name = "PrivateRoute"
    return template.add_resource(Route(
        name,
        GatewayId=Ref(Gateway),
        DestinationCidrBlock=DestinationCidrBlock,
        RouteTableId=Ref(routeTable),
    ))

### Create Route and add Internet Gateway to the routeTable
def addRouteToRouteTableNAT(template, routeTable, Gateway, DestinationCidrBlock, name):
    #name = "PrivateRouteToNatGateway"
    return template.add_resource(Route(
        name,
        DestinationCidrBlock=DestinationCidrBlock,
        NatGatewayId=Ref(Gateway),
        RouteTableId=Ref(routeTable)
    ))



### adding the subnet
def addSubnet(template, Env, Owner, CidrBlock, Name, AvailabilityZone, MapPublicIpOnLaunch, Network):
    return template.add_resource(Subnet(
        Name.replace("-", "").replace(" ", "")+CidrBlock.replace("/","").replace(".", ""),
        CidrBlock=CidrBlock,
        AvailabilityZone=AvailabilityZone,
        MapPublicIpOnLaunch=MapPublicIpOnLaunch,
        VpcId=Ref("VPC"),
        Tags=Tags(**{
            'Name': Name+" - "+Network+" Subnet - "+AvailabilityZone,
            'Network': Network,
            'Env': Env,
            'Owner': Owner,
        })
    ))


### Create a NAT Gateway and attach it to the subnet. Make sure you provide a public Subnet
def addNatGateway(template, subnet):
    ### Create EIP
    NATGatewayEIP = template.add_resource(EIP("NatEIP"+subnet.AvailabilityZone.replace("-", ""),Domain='vpc'))

    ### Create the NATGateway
    NATGateway = template.add_resource(NatGateway(
        "NATGateway"+subnet.AvailabilityZone.replace("-", ""),
        AllocationId=GetAtt(NATGatewayEIP, 'AllocationId'),
        SubnetId=Ref(subnet)
    ))
    return NATGateway

### Adding route table
def addRouteTable(template, az, priv_pubStr, Env, Owner):
    ### Create  Route Table
    myRouteTable = template.add_resource(RouteTable(
        priv_pubStr+"RouteTable"+az.replace("-", ""),
        VpcId=Ref("VPC"),
        Tags=Tags(**{
            'Name': Join("",[Ref("AWS::StackName"),"-"+priv_pubStr]),
            'Env': Env,
            'Owner': Owner,
        })
    ))
    return myRouteTable
