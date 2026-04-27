# AWS Resources — Prosperas Challenge

Account: 990151165442  
Region: us-east-1

## SQS

| Cola | URL |
|------|-----|
| Main queue | https://sqs.us-east-1.amazonaws.com/990151165442/prosperas-jobs |
| Dead Letter Queue | https://sqs.us-east-1.amazonaws.com/990151165442/prosperas-jobs-dlq |

DLQ ARN: `arn:aws:sqs:us-east-1:990151165442:prosperas-jobs-dlq`  
maxReceiveCount: 3

## S3

| Bucket | Uso |
|--------|-----|
| prosperas-reports | Resultados de reportes (result_url) |

## ECR

| Repositorio | URI |
|-------------|-----|
| Backend | 990151165442.dkr.ecr.us-east-1.amazonaws.com/prosperas-backend |
| Worker | 990151165442.dkr.ecr.us-east-1.amazonaws.com/prosperas-worker |

## RDS PostgreSQL

| Parámetro | Valor |
|-----------|-------|
| Identifier | prosperas-db |
| Engine | postgres 15 |
| Class | db.t3.micro |
| Database | prosperas |
| Username | prosperas |
| Subnet group | prosperas-subnet-group |
| Security group | sg-0139ea84df95e23fb (prosperas-rds-sg) |
| VPC | vpc-08121baec071d5934 (default) |
| Publicly accessible | Yes |
| Status | creating... |

Endpoint: `prosperas-db.cyvguywqgrjc.us-east-1.rds.amazonaws.com`  
Port: 5432  
DATABASE_URL: `postgresql://prosperas:Prosperas2024Secure@prosperas-db.cyvguywqgrjc.us-east-1.rds.amazonaws.com:5432/prosperas`

## Networking

| Recurso | ID |
|---------|----|
| VPC | vpc-08121baec071d5934 |
| Security group RDS | sg-0139ea84df95e23fb |
