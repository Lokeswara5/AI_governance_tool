terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr        = var.vpc_cidr
  project_name    = var.project_name
  environment     = var.environment
  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
}

# ECS Cluster
module "ecs" {
  source = "./modules/ecs"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  public_subnets  = module.vpc.public_subnet_ids
}

# RDS Database
module "rds" {
  source = "./modules/rds"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  db_name         = var.db_name
  db_username     = var.db_username
  db_password     = var.db_password
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
}

# Frontend (S3 + CloudFront)
module "frontend" {
  source = "./modules/frontend"

  project_name = var.project_name
  environment  = var.environment
  domain_name = var.domain_name
}

# Backend (ECS Service)
module "backend" {
  source = "./modules/backend"

  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  private_subnets  = module.vpc.private_subnet_ids
  public_subnets   = module.vpc.public_subnet_ids
  ecs_cluster_id   = module.ecs.cluster_id
  ecs_cluster_name = module.ecs.cluster_name
  db_host          = module.rds.db_endpoint
  redis_host       = module.redis.redis_endpoint
  domain_name      = var.domain_name
}