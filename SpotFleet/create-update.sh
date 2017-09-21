#!/bin/bash
# This script uses the AWS CLI tools to initiate and monitor an OpsWorks application deployment
# The AWS CLI tools expect ENV vars set for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# Expected arguments:
## 1 - file of the CloudFormation.json
## 2 - profile name
## 3 - aws region, ex: us-east-1
## 4 -  to be stack name ex: ecs-cluster
## ./create-update.sh myECSCloudFormation.json t-bo us-east-1  ecs-cluster

## Should add at the end something to show all the events
## aws --profile nike --region us-east-1 cloudformation describe-stack-events --stack-name arn:aws:cloudformation:us-east-1::stack/ecs-vpc/7d8bc632-0f1d-11e7-8794-300c219a3c36

RETRY_LIMIT=60
WAIT_TIME=20s
RETRY_COUNT=0
SUCCESS=0
LAST_STATUS=""
status_re="\{.*\"StackStatus\": \"(.*)\",.*\}"  ## "StackStatus": "ROLLBACK_COMPLETE",
deployid_re="\{.*StackId\": \"(arn.*[A-Za-z0-9])\".*\}" ## "StackId": "arn:aws:cloudformation:us-east-1::stack/ecs-cluster/4ff57472-0e87-11e7-86cf-50d5cd795cfd"
stackName_re="\{.*\"StackName\": \"("${4}")\",.*\}" ## "StackName": "ecs-cluster",
cloudformation_action="create-stack"

# Check if the initiated stack is already there or not
echo "Looking to see if the stack is already there or not"
echo "       aws --profile "${2}" --region "${3}" cloudformation describe-stacks"
CURRENTSTACK=`aws --profile "${2}" --region "${3}" cloudformation describe-stacks`
if [[ $CURRENTSTACK =~ $stackName_re ]]
then
  STACK_NAME=${BASH_REMATCH[1]}
  echo "The ${STACK_NAME} already exist, we will try to update it"
  cloudformation_action="update-stack"
fi

# Initiate deployment using aws cli
echo "Trying to create/update the stack"
echo "       aws --profile "${2}" --region "${3}" cloudformation "$cloudformation_action" --stack-name "${4}" --template-body \$CFTEMPLATE"
DEPLOY=`CFTEMPLATE=$(cat  "${1}");aws --profile "${2}" --region "${3}" cloudformation "$cloudformation_action" --stack-name "${4}" --template-body "$CFTEMPLATE" --capabilities CAPABILITY_NAMED_IAM`
# check response for deployment-id
if [[ $DEPLOY =~ $deployid_re ]]
then
  STACK_ID=${BASH_REMATCH[1]}
  echo "Stack initiated, ID: ${STACK_ID}"
else
  echo "Deployment unsuccessful, response from AWS CLI: ${DEPLOY}"
  exit 1
fi

while [ $SUCCESS -ne 1 ] && [ $RETRY_COUNT -lt $RETRY_LIMIT  ]
do
  echo "Attempt #${RETRY_COUNT} of ${RETRY_LIMIT}...";
  RESULTS=`/usr/local/bin/aws --profile "${2}" --region "${3}" cloudformation describe-stacks --stack-name ${STACK_ID}`

  if [[ $RESULTS =~ $status_re ]]
  then
    LAST_STATUS=${BASH_REMATCH[1]}
    echo "Current Status: " $LAST_STATUS;
    if [ $LAST_STATUS == "CREATE_COMPLETE" ]
    then
      SUCCESS=1
      break
    elif [ $LAST_STATUS == "UPDATE_COMPLETE" ]
    then
      SUCCESS=1
      break
    elif [ $LAST_STATUS == "ROLLBACK_COMPLETE" ]
    then
      break
    elif [ $LAST_STATUS == "UPDATE_ROLLBACK_COMPLETE" ]
    then
      break
    fi
  fi

  sleep $WAIT_TIME;
  ((RETRY_COUNT++))
done

if [ $SUCCESS -eq 1 ]
then
  echo "Deployment completed successfully!"
  exit 0
else
  echo "Deployment did not complete successfully, status: ${LAST_STATUS}"
  exit 2
fi
