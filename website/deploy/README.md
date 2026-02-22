# AI Governance Tool - Cloud Deployment

## AWS Deployment Guide

### Prerequisites

1. AWS Account with required permissions
2. Terraform installed locally
3. AWS CLI configured
4. GitHub repository access
5. Domain name (for HTTPS and custom URL)

### Required AWS Services

- ECS (Elastic Container Service)
- RDS (Relational Database Service)
- ElastiCache (Redis)
- S3 (Static website hosting)
- CloudFront (CDN)
- Route53 (DNS)
- ACM (SSL Certificates)
- ECR (Container Registry)

### Deployment Steps

1. **Set up AWS credentials**:
```bash
aws configure
```

2. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Initialize Terraform**:
```bash
cd deploy/aws/terraform
terraform init
```

4. **Create AWS infrastructure**:
```bash
terraform plan -out=tfplan
terraform apply tfplan
```

5. **Configure GitHub Secrets**:

Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET`
- `CLOUDFRONT_DISTRIBUTION_ID`
- `API_URL`
- `SLACK_WEBHOOK_URL` (optional)

6. **Initial deployment**:
Push to main branch or manually trigger GitHub Actions workflow.

### Infrastructure Overview

```
                                     ┌──────────────┐
                                     │  CloudFront  │
                                     └──────┬───────┘
                                            │
                       ┌────────────────────┴───────────────────┐
                       │                                        │
                  ┌────▼─────┐                            ┌─────▼────┐
                  │    S3    │                            │   ALB    │
                  └────┬─────┘                            └─────┬────┘
                       │                                        │
                ┌──────▼──────┐                          ┌─────▼─────┐
                │   Frontend  │                          │    ECS    │
                └─────────────┘                          └─────┬─────┘
                                                              │
                                              ┌───────────────┴──────────────┐
                                              │                              │
                                         ┌────▼─────┐                   ┌────▼─────┐
                                         │   RDS    │                   │  Redis   │
                                         └──────────┘                   └──────────┘
```

### Monitoring and Logging

1. **CloudWatch Metrics**:
- ECS Service metrics
- RDS metrics
- ElastiCache metrics
- ALB metrics

2. **CloudWatch Logs**:
- ECS task logs
- Application logs
- ALB access logs

3. **X-Ray Tracing**:
- API latency
- Service dependencies
- Error tracking

### Scaling Configuration

1. **ECS Auto Scaling**:
- CPU utilization target: 70%
- Memory utilization target: 80%
- Min instances: 2
- Max instances: 10

2. **RDS**:
- Instance class: db.t3.medium
- Storage: Auto scaling enabled
- Multi-AZ: Enabled

3. **ElastiCache**:
- Node type: cache.t3.medium
- Replicas: 2

### Cost Optimization

1. **Reserved Instances**:
- RDS: 1-year commitment
- ElastiCache: 1-year commitment

2. **S3 Lifecycle Rules**:
- Move infrequent access files to IA
- Expire old files

3. **CloudFront**:
- Caching enabled
- Compression enabled

### Security Measures

1. **Network**:
- VPC with private subnets
- Security groups
- NACLs

2. **Data**:
- RDS encryption
- S3 encryption
- Redis encryption

3. **Access**:
- IAM roles
- Secrets Manager
- SSL/TLS

### Backup Strategy

1. **Database**:
- Daily automated backups
- 30-day retention
- Point-in-time recovery

2. **Application State**:
- S3 versioning
- Cross-region replication

3. **Configuration**:
- Terraform state backup
- Infrastructure as Code

### Rollback Procedure

1. **Application**:
```bash
# Roll back ECS deployment
aws ecs update-service --cluster ai-governance-cluster \
  --service ai-governance-backend \
  --task-definition ai-governance:PREVIOUS_VERSION
```

2. **Infrastructure**:
```bash
# Roll back Terraform changes
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
```

### Troubleshooting

1. **Check service health**:
```bash
aws ecs describe-services \
  --cluster ai-governance-cluster \
  --services ai-governance-backend
```

2. **View logs**:
```bash
aws logs get-log-events \
  --log-group-name /ecs/ai-governance \
  --log-stream-name backend/TASK_ID
```

3. **Check database**:
```bash
aws rds describe-db-instances \
  --db-instance-identifier ai-governance
```