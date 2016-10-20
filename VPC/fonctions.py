# from troposphere import Join, Output
from troposphere import Parameter, Ref, Tags, Template, GetAtt
from troposphere.ec2 import PortRange
from troposphere.ec2 import NetworkAcl
from troposphere.ec2 import Route
from troposphere.ec2 import EIP
from troposphere.ec2 import VPCGatewayAttachment
from troposphere.ec2 import SubnetRouteTableAssociation
from troposphere.ec2 import Subnet
# from troposphere.ec2 import CustomerGateway
# from troposphere.ec2 import VPNConnectionRoute
from troposphere.ec2 import RouteTable
from troposphere.ec2 import VPC
from troposphere.ec2 import NetworkAclEntry
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import NatGateway
# from troposphere.ec2 import VPNGateway
from troposphere.ec2 import SubnetNetworkAclAssociation
# from troposphere.ec2 import VPNConnection
from troposphere import Ref, Template, Tags, Join


def addSubnetRouteTableAssociation(template, subnet, routeTable):
    return template.add_resource(
        SubnetRouteTableAssociation(
            subnet.title + routeTable.title,
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
            )
    )

def addRouteToRouteTable(template, routeTable, Gateway, DestinationCidrBloc):
    name = "PrivateRoute"
    return template.add_resource(Route(
        name,
        GatewayId=Ref(Gateway),
        DestinationCidrBlock=DestinationCidrBlock,
        RouteTableId=Ref(routeTable),
    ))

def addNaclEntry(template, nacl, RuleNumber, Protocol, PortRange, Egress, CidrBlock, RuleAction):
    name = RuleNumber
    return template.add_resource(NetworkAclEntry(
        name,
        NetworkAclId=Ref(nacl),
        RuleNumber=RuleNumber,
        Protocol=Protocol,
        PortRange=PortRange,
        Egress=Egress,
        RuleAction=RuleAction,
        CidrBlock=CidrBlock,
    ))

def addSubnetNaclAssociation(template, subnet, nacl):
    name = subnet.title+nacl.title
    return template.add_resource(
        SubnetNetworkAclAssociation(
            name,
            SubnetId=Ref(subnet),
            NetworkAclId=Ref(nacl),
        )
    )


def addSubnet(template, CidrBlock, Name, AvailabilityZone, MapPublicIpOnLaunch, Network):
    return template.add_resource(Subnet(
        "Subnet"+Name.replace("-", "").replace(" ", "").replace("/","").replace(".", "")+Network+AvailabilityZone.replace("-","")+CidrBlock.replace("/","").replace(".", ""),
        CidrBlock=CidrBlock,
        AvailabilityZone=AvailabilityZone,
        MapPublicIpOnLaunch=MapPublicIpOnLaunch,
        VpcId=Ref("VPC"),
        Tags=Tags(**{
            'Name': Name+" - "+Network+" Subnet - "+AvailabilityZone+" - "+CidrBlock,
            'Network': Network,
        })
    ))

#NatGatewayArray = [addNatGateway(t, subnet) for subnet in PublicSubnets]
def addNatGateway(template, subnet, CidrBlock, priv_subnet):
    ### Create EIP
    NATGatewayEIP = template.add_resource(EIP("NatEIP"+subnet.AvailabilityZone.replace("-", ""),Domain='VPC'))
    PrivateNATGateway = template.add_resource(NatGateway(
        "NATGateway"+subnet.AvailabilityZone.replace("-", ""),
        AllocationId=GetAtt(NATGatewayEIP, 'AllocationId'),
        SubnetId=Ref(subnet)
    ))
    ### Create Public Route Table for all Public Subnets
    PrivateRouteTable = template.add_resource(RouteTable(
        "PrivateRouteTable"+subnet.AvailabilityZone.replace("-", ""),
        VpcId=Ref("VPC"),
        Tags=Tags(
            Name=Join("",[Ref("AWS::StackName"),"-private"])
        )
    ))
    ### Add a route to the internet from the Public Route Table
    PrivateRouteToNATGateway = template.add_resource(Route(
        "PrivateRouteToNatGateway"+subnet.AvailabilityZone.replace("-", ""),
        DestinationCidrBlock=CidrBlock,
        NatGatewayId=Ref(PrivateNATGateway),
        RouteTableId=Ref(PrivateRouteTable),
    ))
    addSubnetRouteTableAssociation(template, priv_subnet, PrivateRouteTable)
    return PrivateNATGateway

