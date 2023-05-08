import json
import boto3
import datetime

# Create a custom IAM role with permissions to put objects in S3
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')


# Define the policy document for the IAM role
put_object_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::disprzassgn/*"
            ]
        }
    ]
}

#Creating a policy 

response = iam_client.create_policy(
    PolicyName='S3PutObjectAccessPolicy',
    PolicyDocument=json.dumps(put_object_policy_document)
)





#ARN of the policy
put_object_policy_arn = response['Policy']['Arn']


# Define the IAM role for the Lambda function
lambda_role_name = 'lambda-s3-role'

# Create the IAM role for the Lambda function
# lambda_role = iam_client.create_role(
#     RoleName=lambda_role_name,
#     AssumeRolePolicyDocument=json.dumps({
#         "Version": "2012-10-17",
#         "Statement": [
#             {
#                 "Effect": "Allow",
#                 "Principal": {
#                     "Service": "lambda.amazonaws.com"
#                 },
#                 "Action": "sts:AssumeRole"
#             }
#         ]
#     })
# )


iam_client.attach_role_policy(
    RoleName=lambda_role_name,
    PolicyArn=put_object_policy_arn
)


cloudwatch_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}

response = iam_client.create_policy(
    PolicyName='lambda-cloudwatch-policy',
    PolicyDocument=json.dumps(cloudwatch_policy)
)

cloudwatch_policy_arn = response['Policy']['Arn']


iam_client.attach_role_policy(
    RoleName=lambda_role_name,
    PolicyArn=cloudwatch_policy_arn
)


