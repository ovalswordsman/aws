## Question 1
Create S3 bucket from AWS CLI <br>
<b>a.</b> Create an IAM role with S3 full access

```
aws iam create-role --role-name disprz --assume-role-policy-document file://trust-policy.json
```

Here the trust policy json contains the following information 
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

<img width="1065" alt="Screenshot 2023-05-04 at 12 03 32 PM" src="https://user-images.githubusercontent.com/54627996/236127791-879116b3-92e2-4818-a9e1-cc605e1b4840.png">

Providing the role with S3 full access
```
aws iam attach-role-policy --role-name disprz --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```


<b>b.</b>Create an EC2 instance with above role
Creating an instance profile
```
aws iam create-instance-profile --instance-profile-name disprz_profile
```

Attaching the role to the instance profile

```
 aws iam add-role-to-instance-profile --instance-profile-name disprz_profile --role-name disprz
```

Running the instance
```
aws ec2 run-instances --image-id ami-0577c11149d377ab7 --instance-type t3.micro --key-name firstkeypair --iam-instance-profile Name="disprz_profile" 
```

<b>c.</b>
Creating the bucket 
```
aws s3api create-bucket --bucket disprzassgn --region eu-north-1 --create-bucket-configuration LocationConstraint=eu-north-1 
``` 
<img width="1046" alt="Screenshot 2023-05-04 at 12 21 47 PM" src="https://user-images.githubusercontent.com/54627996/236131408-53897369-53a1-4425-b303-e64833b6db84.png">



##Question 2
Put files in S3 bucket from lambda <br>

Creating clients
```
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')
```



<b>a.</b>Create custom role for AWS lambda which will only have put object access
Creating policy for put object access
```
put_object_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::disprz/*"
            ]
        }
    ]
}
```

Creating the policy
```
response = iam_client.create_policy(
    PolicyName='S3PutObjectAccessPolicy',
    PolicyDocument=json.dumps(put_object_policy_document)
)
```
Create the IAM role for the Lambda function

```
lambda_role = iam_client.create_role(
    RoleName=lambda_role_name,
    AssumeRolePolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
)
```

Attach the policy to the role
```
iam_client.attach_role_policy(
    RoleName=lambda_role_name,
    PolicyArn=put_object_policy_arn
)
```


<b>b.</b>Add role to generate and access Cloudwatch logs
Creating cloudwatch policy
```
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
```
```
response = iam_client.create_policy(
    PolicyName='lambda-cloudwatch-policy',
    PolicyDocument=json.dumps(cloudwatch_policy)
)
```

Attach the policy to the role
```
iam_client.attach_role_policy(
    RoleName=lambda_role_name,
    PolicyArn=cloudwatch_policy_arn
)
```
<img width="1089" alt="Screenshot 2023-05-04 at 12 29 16 PM" src="https://user-images.githubusercontent.com/54627996/236132742-a6f2bddb-0e64-4aac-af11-5dd6738d2070.png">






<b>c.</b>In python script, generate json in given format and save .json file in bucket created



<b>d.</b>Schedule the job to run every minute. Stop execution after 3 runs



<b>e.</b>Check if cloudwatch logs are generated


