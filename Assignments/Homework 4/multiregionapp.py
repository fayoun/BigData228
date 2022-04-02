###### 0_Cloud9 ######


#Installing nvm & node

nvm install 8.9.1

nvm alias default v8.9.1

#Verifying the right node and rpm

npm -v
node -v
nvm ls

#Cloning the workshop project 
git clone https://github.com/enghwa/MultiRegion-Serverless-Workshop.git


###### 1_Build an API Layer ######

## Using CLI Method

#Creating S3 bucket in Ireland and Singapore region

aws s3 mb s3://multiregion-wildrydesdatadivas-ireland --region eu-west-1
aws s3 mb s3://multiregion-wildrydesdatadivas-singapore --region eu-west-1

## Package up the APU Code and pushing to S3

#Entering into the correct directory
cd /home/ec2-user/environment/MultiRegion-Serverless-Workshop/1_API

#Ireland

aws cloudformation package \
--region eu-west-1 \
--template-file wild-rydes-api.yaml \
--output-template-file wild-rydes-api-output.yaml \
--s3-bucket multiregion-wildrydesdatadivas-ireland 

#Singapore

aws cloudformation package \
--region eu-west-1 \
--template-file wild-rydes-api.yaml \
--output-template-file wild-rydes-api-output.yaml \
--s3-bucket multiregion-wildrydesdatadivas-singapore

#Deploying a stack of resources

#Ireland
aws cloudformation deploy \
--region eu-west-1 \
--template-file wild-rydes-api-output.yaml \
--stack-name wild-rydes-api \
--capabilities CAPABILITY_IAM

#Singapore
aws cloudformation deploy \
--region ap-southeast-1 \
--template-file wild-rydes-api-output-ap-southeast-1.yaml \
--stack-name wild-rydes-api \
--capabilities CAPABILITY_IAM

#Enabling DynamoDB Global Table
aws dynamodb create-global-table \
--global-table-name SXRTickets \
--replication-group RegionName=eu-west-1 RegionName=ap-southeast-1 \
--region eu-west-1

###### 2_ Building a UI Layer #######

#AWS CloudFormation Deploy in eu-west-1 (Ireland)

cd /home/ec2-user/environment/MultiRegion-Serverless-Workshop/2_UI/cfn

aws cloudformation deploy \
--region eu-west-1 \
--template-file web-ui-stack.yaml \
--stack-name ticket-service-ui \
--capabilities CAPABILITY_IAM

#Cloudfront distribution for S3 Bucket

aws cloudformation deploy \
--region eu-west-1 \
--template-file webs3bucket_with_cloudfront.yaml \
--stack-name ticket-service-ui-cloudfront \
--parameter-overrides S3BucketName=ticket-service-ui-websitebucket-1v6h833bd5d1y

#Building Angular JS Project

cd /home/ec2-user/environment/MultiRegion-Serverless-Workshop/2_UI
npm install
npm run build

# Uploading the App

aws s3 sync --delete dist/ s3://ticket-service-ui-websitebucket-1v6h833bd5d1y



###### 3_ Route53 #######

#Update your UI with new API Gateway Endpoint

npm run build
aws s3 sync --delete dist/ s3://ticket-service-ui-websitebucket-1v6h833bd5d1y



###### S3 Replication and CloudFront with Multi-Region S3 Origins#######

## 1.Enable versioning on your source bucket in Ireland region

aws s3api put-bucket-versioning \
--bucket ticket-service-ui-websitebucket-1v6h833bd5d1y 
--versioning-configuration Status=Enabled

## 2.Create a destination bucket and enable versioning on it

aws s3api create-bucket \
--bucket ticket-service-ui-websitebucket-singapore-1v6h833bd5d1y \
--region ap-southeast-1 \
--create-bucket-configuration LocationConstraint=ap-southeast-1


##Enabling Version

aws s3api put-bucket-versioning \
--bucket ticket-service-ui-websitebucket-singapore-1v6h833bd5d1y \
--versioning-configuration Status=Enabled

## Running the following command to add the replication configuration to your source bucket. 
aws s3api put-bucket-replication \
--replication-configuration file://replication.json \
--bucket ticket-service-ui-websitebucket-1v6h833bd5d1y 

##Building the App

aws s3 sync --delete dist/ s3://ticket-service-ui-websitebucket-1v6h833bd5d1y 

aws cloudfront create-invalidation --distribution-id E2CCGF1I42D5MJ --paths "/images/app-screenshot.png" "/images/app-screenshot2.png"
