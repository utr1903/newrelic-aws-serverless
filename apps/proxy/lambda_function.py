import newrelic
import os
import json
import boto3

LAMBDA_NAME = "proxy"

lambdaClient = boto3.client("lambda")

def log(message):
  print("{}: {}".format(LAMBDA_NAME, message))

def insertDistributedTracingHeaders(requestBody):
  dtHeaders = []
  newrelic.agent.insert_distributed_trace_headers(headers=dtHeaders)
  requestBody["dtHeaders"] = dtHeaders

def prepareResponse(statusCode, message):
  response = {
    "statusCode": statusCode,
    "body": json.dumps(
      {
        "message": message
      }
    ),
  }

  log(response)
  return response

def lambda_handler(event, context):

  log("Lambda is triggered.")

  # Parse request body
  requestBody = json.loads(event["body"])
  insertDistributedTracingHeaders(requestBody)

  try:
    # Send payload to storer lambda
    log("Performing request to storer lambda...")
    storerResponse = lambdaClient.invoke(
      FunctionName = os.getenv('LAMBDA_STORER_NAME'),
      InvocationType = "RequestResponse",
      Payload = json.dumps(requestBody)
    )
    log("Request is performed to storer lambda successfully.")
  except Exception as e:
    log(e)
    return prepareResponse(500, "Request to storer lambda is failed.")

  try:
    payload = json.loads(storerResponse["Payload"].read())
  except Exception as e:
    log(e)
    return prepareResponse(500, "Storer response is failed to be parsed.")

  if payload.get("body").get("success"):
    statusCode = 200
  else:
    statusCode = 400

  return prepareResponse(
    statusCode,
    payload.get("body").get("message")
  )
