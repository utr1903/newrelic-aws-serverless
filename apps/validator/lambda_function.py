import newrelic
import json
import boto3

LAMBDA_NAME = "validator"
CUSTOM_NEWRELIC_EVENT = "MyCustomServerlessEvent"

s3Client = boto3.client("s3")

def log(message):
  print("{}: {}".format(LAMBDA_NAME, message))

def createCustomNewRelicEvent(attributes):
  if attributes == None:
    attributes = {}

  application = newrelic.agent.application()
  newrelic.agent.record_custom_event(CUSTOM_NEWRELIC_EVENT,
    attributes, application)

def prepareResponse(statusCode):
  response = {
    "statusCode": statusCode,
  }
  return response

def lambda_handler(event, context):

  log("Lambda is triggered.")

  # Parse request body
  requestBody = json.loads(event["body"])
  log(requestBody)

  if requestBody.get("name") == None:
    createCustomNewRelicEvent({
      "message": "Name is not provided."
    })
    return prepareResponse(400)
  elif requestBody.get("description") == None:
    createCustomNewRelicEvent({
      "message": "Description is not provided."
    })
    return prepareResponse(400)
  else:
    return prepareResponse(200)
