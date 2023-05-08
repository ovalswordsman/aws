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

<b>c.</b>In python script, generate json in given format and save .json file in bucket created<br>
<b>i. </b>Created a lambda_handler function to save the file in json in format and upload it to the bucket<br>


<b>d.</b>Schedule the job to run every minute. Stop execution after 3 runs
<b>i. </b>Using amazon lambda, created a function and uploaded the zip file created above

<img width="871" alt="Screenshot 2023-05-04 at 4 16 04 PM" src="https://user-images.githubusercontent.com/54627996/236182673-ef121259-abca-425e-bb8d-95c85fef40ae.png">

<b>ii. </b>Now using cloudwatch rule, created a rule for my lambda function to run it every minute.
<img width="1176" alt="Screenshot 2023-05-04 at 4 19 17 PM" src="https://user-images.githubusercontent.com/54627996/236183390-02a31341-f4ea-4d8e-9bf5-fd8075cb4792.png">


<b>e.</b>Check if cloudwatch logs are generated
<img width="1075" alt="Screenshot 2023-05-04 at 4 21 07 PM" src="https://user-images.githubusercontent.com/54627996/236183766-e8faccf5-f88c-497c-84cd-df12f0d0549f.png">

Also the file was added to the bucket
<img width="1315" alt="Screenshot 2023-05-04 at 4 21 32 PM" src="https://user-images.githubusercontent.com/54627996/236183846-bcdd7d56-25dd-4c64-bd40-135d31ae795f.png">


## Question 3
<b>a.</b> Modify lambda function to accept parameters and return file name
Modified lambda function is : 
```
import boto3
import datetime
import json

s3 = boto3.resource('s3')
bucket_name = 'disprzassgn'
key_name = 'transaction{}.json'

def lambda_handler(event, context):
    try:
        # Parse input data
        transaction_id = event['transaction_id']
        payment_mode = event['payment_mode']
        amount = event['amount']
        customer_id = event['customer_id']

        # Generate JSON in the given format
        timestamp = str(datetime.datetime.now())
        transaction_data = {
            "transaction_id": transaction_id,
            "payment_mode": payment_mode,
            "amount": amount,
            "customer_id": customer_id,
            "timestamp": timestamp
        }

        # Save JSON file in S3 bucket
        json_data = json.dumps(transaction_data)
        file_name = key_name.format(timestamp.replace(" ", "_"))
        s3.Object(bucket_name, file_name).put(Body=json_data)

        # Log the S3 object creation event
        print(f"Object created in S3 bucket {bucket_name}: {file_name}")

        return {
            "file_name": file_name,
            "status": "success"
        }

    except Exception as e:
        print(e)
        return {
            "status": "error"
        }
```

<b>b.</b> Create a POST API from API gateway, pass parameters as request body to Lambda job. Return filename and status as response<br>
Created a post API with name <b>transactions</b>
<img width="759" alt="Screenshot 2023-05-08 at 12 49 19 PM" src="https://user-images.githubusercontent.com/54627996/236760369-910dee7b-acd1-4935-bab4-484a47cac4e4.png">

Tested the API by sending a POST request with the given JSON payload :
<img width="1167" alt="Screenshot 2023-05-08 at 12 52 57 PM" src="https://user-images.githubusercontent.com/54627996/236761167-fe0dbdf9-baa9-4026-a5df-ba0d067bb433.png">

Checking the cloudwatch logs : 
<img width="1143" alt="Screenshot 2023-05-08 at 12 54 10 PM" src="https://user-images.githubusercontent.com/54627996/236761411-cb7b1c90-6e30-421d-967c-c2ffb1e2889d.png">

c. Consume API from local machine and pass unique data to lambda.
Used postman to send the request
<img width="916" alt="Screenshot 2023-05-08 at 1 43 29 PM" src="https://user-images.githubusercontent.com/54627996/236772049-2ac98b78-aace-43f4-ad42-9b97049d0d1e.png">

d. Check if cloud watch logs are generated
<img width="1146" alt="Screenshot 2023-05-08 at 1 43 45 PM" src="https://user-images.githubusercontent.com/54627996/236772098-c57b50fc-f5c4-4119-bc2f-7a3e55ef6b67.png">
File also get uploaded to the bucket

<img width="1094" alt="Screenshot 2023-05-08 at 1 44 04 PM" src="https://user-images.githubusercontent.com/54627996/236772172-47e6e987-5bcf-4f9d-96bf-10c2f5f403b9.png">
