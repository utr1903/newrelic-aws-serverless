import newrelic
import os
import json
import boto3
import urllib3

LAMBDA_NAME = "forwarder"
CUSTOM_NEWRELIC_EVENT = "MyCustomServerlessEvent"

s3Client = boto3.client("s3")
http = urllib3.PoolManager()

def log(message):
  print("{}: {}".format(LAMBDA_NAME, message))

def createCustomNewRelicEvent(attributes):
  if attributes == None:
    attributes = {}

  application = newrelic.agent.application()
  newrelic.agent.record_custom_event(CUSTOM_NEWRELIC_EVENT,
    attributes, application)

def lambda_handler(event, context):

  log("Lambda is triggered.")

  # Get validator lambda URL
  validatorLambdaUrl = os.getenv("LAMBDA_VALIDATOR_URL")
  if validatorLambdaUrl == None:
    createCustomNewRelicEvent({
      "message": "No bucket name is provided."
    })
    return

  # Get file from S3
  try:
    records = event.get("Records")
    log("Records are parsed successfully.")
  except Exception as e:
    log(e)
    createCustomNewRelicEvent({
      "message": "Parsing records is failed."
    })

  # Send files to validation
  for record in records:
    try:
      log("Reading file from bucket...")
      bucketName = record.get("s3").get("bucket").get("name")
      fileKey = record.get("s3").get("object").get("key")

      object = s3Client.get_object(
        Bucket = bucketName,
        Key = fileKey,
      )

      file = json.loads(object["Body"].read())
      log("File [{}] is read successfully from the bucket [{}]."
        .format(fileKey, bucketName))

    except Exception as e:
      log(e)
      createCustomNewRelicEvent({
        "message": "Retrieving file [{}] from bucket [{}] failed."
          .format(fileKey, bucketName)
      })
      return

    try:
      log("Sending file to validator...")
      http.request(
        'POST',
        validatorLambdaUrl,
        body = json.dumps(file),
        headers = {'Content-Type': 'application/json'},
        retries = False
      )
    except Exception as e:
      log(e)
      createCustomNewRelicEvent({
        "message": "Sending file [{}] from bucket [{}] to validator [{}] failed."
          .format(fileKey, bucketName, validatorLambdaUrl)
      })
      return
