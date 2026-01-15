#!/bin/bash
set -e

# CoomerDL AWS Deployment Script
# This script deploys CoomerDL to AWS ECS Fargate using CloudFormation

echo "🚀 CoomerDL AWS Deployment Script"
echo "===================================="
echo ""

# Configuration
PROJECT_NAME="${PROJECT_NAME:-coomerdl}"
ENVIRONMENT="${ENVIRONMENT:-production}"
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it: https://aws.amazon.com/cli/"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install it: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Prerequisites met"
echo ""

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}"

echo "📦 Deployment Configuration:"
echo "  Project: ${PROJECT_NAME}"
echo "  Environment: ${ENVIRONMENT}"
echo "  AWS Region: ${AWS_REGION}"
echo "  AWS Account: ${AWS_ACCOUNT_ID}"
echo "  Stack Name: ${STACK_NAME}"
echo ""

# Create ECR repository if it doesn't exist
echo "🏗️  Setting up ECR repository..."
if ! aws ecr describe-repositories --repository-names ${PROJECT_NAME} --region ${AWS_REGION} &> /dev/null; then
    echo "Creating ECR repository: ${PROJECT_NAME}"
    aws ecr create-repository \
        --repository-name ${PROJECT_NAME} \
        --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    echo "✅ ECR repository created"
else
    echo "✅ ECR repository already exists"
fi
echo ""

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t ${PROJECT_NAME}:latest -f Dockerfile.webapp .
echo "✅ Docker image built"
echo ""

# Tag and push to ECR
echo "📤 Pushing image to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY}
docker tag ${PROJECT_NAME}:latest ${ECR_REPOSITORY}:latest
docker tag ${PROJECT_NAME}:latest ${ECR_REPOSITORY}:${ENVIRONMENT}
docker push ${ECR_REPOSITORY}:latest
docker push ${ECR_REPOSITORY}:${ENVIRONMENT}
echo "✅ Image pushed to ECR"
echo ""

# Deploy CloudFormation stack
echo "☁️  Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file aws/cloudformation.yaml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        ProjectName=${PROJECT_NAME} \
        EnvironmentName=${ENVIRONMENT} \
        ContainerImage=${ECR_REPOSITORY}:${ENVIRONMENT} \
        TaskCpu=2048 \
        TaskMemory=4096 \
        DesiredCount=1 \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ${AWS_REGION}

echo "✅ CloudFormation stack deployed"
echo ""

# Get outputs
echo "📊 Deployment Information:"
APPLICATION_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
    --output text)

BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`DownloadBucketName`].OutputValue' \
    --output text)

echo "  Application URL: ${APPLICATION_URL}"
echo "  Download Bucket: ${BUCKET_NAME}"
echo "  ECR Repository: ${ECR_REPOSITORY}"
echo ""

# Wait for service to be stable
echo "⏳ Waiting for service to stabilize..."
CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' \
    --output text)

SERVICE_NAME=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${AWS_REGION} \
    --query 'Stacks[0].Outputs[?OutputKey==`ServiceName`].OutputValue' \
    --output text)

aws ecs wait services-stable \
    --cluster ${CLUSTER_NAME} \
    --services ${SERVICE_NAME} \
    --region ${AWS_REGION}

echo "✅ Service is stable and running"
echo ""

echo "🎉 Deployment Complete!"
echo ""
echo "📝 Next Steps:"
echo "  1. Visit your application: ${APPLICATION_URL}"
echo "  2. Configure DNS (optional): Point your domain to ${APPLICATION_URL}"
echo "  3. Set up SSL/TLS (optional): Use AWS Certificate Manager + ALB listener"
echo "  4. Monitor logs: aws logs tail /ecs/${PROJECT_NAME}-${ENVIRONMENT} --follow"
echo "  5. View metrics: AWS Console → ECS → ${CLUSTER_NAME} → ${SERVICE_NAME}"
echo ""
echo "🗑️  To delete this deployment:"
echo "  aws cloudformation delete-stack --stack-name ${STACK_NAME} --region ${AWS_REGION}"
echo "  aws ecr delete-repository --repository-name ${PROJECT_NAME} --region ${AWS_REGION} --force"
echo ""
