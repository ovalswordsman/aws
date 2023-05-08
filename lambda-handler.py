import boto3
import datetime, time
import json

s3 = boto3.resource('s3')

bucket_name = 'disprzassgn'
key_name = 'transaction{}.json'

cw_logs = boto3.client('logs')
log_group = 'lambda_logs'
log_stream = 'lambda_stream'

def lambda_handler(event, context):
    try:
        # Generate JSON in the given format
        transaction_id = 12345
        payment_mode = "card/netbanking/upi"
        Amount = 200.0
        customer_id = 101
        Timestamp = str(datetime.datetime.now())
        transaction_data = {
            "transaction_id": transaction_id,
            "payment_mode": payment_mode,
            "Amount": Amount,
            "customer_id": customer_id,
            "Timestamp": Timestamp
        }
        
        # Save JSON file in S3 bucket
        json_data = json.dumps(transaction_data)
        file_name = key_name.format(Timestamp.replace(" ", "_"))
        s3.Bucket(bucket_name).Object(file_name).put(Body=json_data)
        
        # Log the S3 object creation event
        log_message = f"Object created in S3 bucket {bucket_name}: {file_name}"
        cw_logs.create_log_group(logGroupName=log_group)
        cw_logs.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
        cw_logs.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[{
                'timestamp': int(round(time.time() * 1000)),
                'message': log_message
            }]
        )
        
        # Stop execution after 3 runs
        if context.invoked_function_arn.endswith(':1'):
            print('First execution')
        elif context.invoked_function_arn.endswith(':2'):
            print('Second execution')
        elif context.invoked_function_arn.endswith(':3'):
            print('Third execution')
        else:
            print('Stopping execution')
            return
        
    except Exception as e:
        print(e)

