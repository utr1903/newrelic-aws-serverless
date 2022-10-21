import newrelic
import os
import json
import time
import boto3

LAMBDA_NAME = "storer"

s3Client = boto3.client("s3")

def log(message):
  print("{}: {}".format(LAMBDA_NAME, message))

def acceptDistributedTracingHeaders(event):
  dtHeaders = event.get("dtHeaders")
  transaction = newrelic.agent.current_transaction()
  transaction.accept_distributed_trace_headers(dtHeaders, transport_type='HTTP')
  # newrelic.agent.accept_distributed_trace_headers(dtHeaders, transport_type='HTTP')

def prepareResponse(success, message):
  response = {
    "statusCode": 200,
    "body": {
      "success": success,
      "message": message,
    }
  }

  log(response)
  return response

def lambda_handler(event, context):

  log("Lambda is triggered.")

  acceptDistributedTracingHeaders(event)

  # Get bucket name
  bucketName = os.getenv('S3_BUCKET_NAME')
  if bucketName == None:
    return prepareResponse(False, "No bucket name is provided.")

  # Parse request body
  try:
    file = event.get("file")
    encodedString = json.dumps(file).encode("utf-8")
  except:
    return prepareResponse(False, "Failed to parse request body.")

  # Store in S3
  try:
    fileName = "{}.json".format(round(time.time()*1000))
    s3Client.put_object(
      Bucket = bucketName,
      Key = fileName,
      Body = encodedString
    )
  except Exception as e:
    log(e)
    return prepareResponse(False, "File is failed to be stored in S3.")

  return prepareResponse(True, "File is stored in S3 successfully.")
