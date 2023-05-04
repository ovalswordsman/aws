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
