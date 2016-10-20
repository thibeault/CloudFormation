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


### Add subnet to the routeTable
def addSubnetRouteTableAssociation(template, subnet, routeTable):
    return template.add_resource(
        SubnetRouteTableAssociation(
            subnet.title + routeTable.title,
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
            )
    )

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


### Create a NAT Gateway and attach it to the subnet. Make sure you provide a public Subnet
def addNatGateway(template, subnet):
    ### Create EIP
    NATGatewayEIP = template.add_resource(EIP("NatEIP"+subnet.AvailabilityZone.replace("-", ""),Domain='VPC'))

    ### Create the NATGateway
    NATGateway = template.add_resource(NatGateway(
        "NATGateway"+subnet.AvailabilityZone.replace("-", ""),
        AllocationId=GetAtt(NATGatewayEIP, 'AllocationId'),
        SubnetId=Ref(subnet)
    ))
    return NATGateway

### Adding route table
def addRouteTable(template, az, priv_pubStr):
    ### Create  Route Table
    myRouteTable = template.add_resource(RouteTable(
        priv_pubStr+"RouteTable"+az.replace("-", ""),
        VpcId=Ref("VPC"),
        Tags=Tags(
            Name=Join("",[Ref("AWS::StackName"),"-"+priv_pubStr])
        )
    ))
    return myRouteTable