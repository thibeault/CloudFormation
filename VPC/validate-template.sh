#!/bin/bash
# This script uses the AWS CLI tools to initiate and monitor an OpsWorks application deployment
# The AWS CLI tools expect ENV vars set for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# Expected arguments:
## 1 - file of the CloudFormation.json
## 2 - profile name
## 3 - aws region, ex: us-east-1
## ./validate-template.sh myVPCCloudFormation.json t-bo us-east-1

status_re="\{(.*)\}"
#status_re=".*(ValidationError).*"

# VAlidating the cloud formation template
echo "---- Claoudformation validation Start ----"
CURRENTSTACK=`CFTEMPLATE=$(cat  "${1}");aws --profile "${2}" --region "${3}" --output json cloudformation validate-template --template-body "$CFTEMPLATE"`
echo "---- Template Start ----"
echo " "
echo `cat  "${1}"`
echo " "
echo "---- Template End ----"
echo "aws --profile "${2}" --region "${3}" --output json cloudformation validate-template --template-body \$CFTEMPLATE"
echo "---- Response Start ----"
echo " "
echo $CURRENTSTACK
echo " "
echo "---- Response End ----"

## Look for ValidationError
if [[ $CURRENTSTACK =~ $status_re ]]
then
  echo "VALID template."
else
  echo "INVALID template."
  echo "---- Claoudformation validation End ----"
  exit 2
fi
echo "---- Claoudformation validation End ----"
