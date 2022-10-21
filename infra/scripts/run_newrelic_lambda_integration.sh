#!/bin/bash

### Set up New Relic Lambda integration
newrelic-lambda integrations install \
  --nr-account-id $NEWRELIC_ACCOUNT_ID \
  --nr-api-key $NEWRELIC_API_KEY \
  --nr-region "eu" \
  --enable-license-key-secret \
  --enable-cw-ingest \
  --enable-logs \
  --aws-region "eu-west-1"
