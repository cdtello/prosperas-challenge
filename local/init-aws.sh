#!/bin/sh
set -e

ENDPOINT="http://localstack:4566"
REGION="us-east-1"
AWS="aws --endpoint-url=$ENDPOINT --region=$REGION"

echo "==> Creando Dead Letter Queue..."
$AWS sqs create-queue --queue-name prosperas-jobs-dlq

DLQ_ARN=$($AWS sqs get-queue-attributes \
  --queue-url "$ENDPOINT/000000000000/prosperas-jobs-dlq" \
  --attribute-names QueueArn \
  --query 'Attributes.QueueArn' \
  --output text)

echo "==> DLQ ARN: $DLQ_ARN"

echo "==> Creando cola principal con DLQ y política de reintentos..."
$AWS sqs create-queue \
  --queue-name prosperas-jobs \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_ARN\\\",\\\"maxReceiveCount\\\":\\\"3\\\"}\"}"

echo "==> Creando bucket S3..."
$AWS s3 mb s3://prosperas-reports

echo "==> Recursos AWS listos:"
echo "    SQS queue:  $ENDPOINT/000000000000/prosperas-jobs"
echo "    SQS DLQ:    $ENDPOINT/000000000000/prosperas-jobs-dlq"
echo "    S3 bucket:  s3://prosperas-reports"
