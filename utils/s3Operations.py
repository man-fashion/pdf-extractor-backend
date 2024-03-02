#  using boto3 setup s3 client and operations and on upload get public urls

import boto3
import botocore
import os
from dotenv import load_dotenv

load_dotenv()


def upload_file_to_s3(file, bucket_name, acl="public-read"):
    s3 = boto3.client(
       "s3",
       aws_access_key_id=os.environ.get("Access_key_ID"),
       aws_secret_access_key=os.environ.get("Secret_access_key")
    )

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e

    return "{}{}".format(os.environ.get("Bucket_Name"), file.filename)

def delete_file_from_s3(bucket_name, s3_file_name):
    s3 = boto3.client(
       "s3",
       aws_access_key_id=os.environ.get("Access_key_ID"),
       aws_secret_access_key=os.environ.get("Secret_access_key")
    )

    try:
        s3.delete_object(Bucket=bucket_name, Key=s3_file_name)
    except botocore.exceptions.ClientError as e:
        print("An error occurred: ", e)
        return e

    return "File Deleted"

def get_bucket_contents(bucket_name):
    s3 = boto3.client(
       "s3",
       aws_access_key_id=os.environ.get("Access_key_ID"),
       aws_secret_access_key=os.environ.get("Secret_access_key")
    )

    try:
        contents = s3.list_objects(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        print("An error occurred: ", e)
        return None

    return contents

