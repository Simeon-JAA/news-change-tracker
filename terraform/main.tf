provider "aws" {
  region = var.REGION
}

resource "aws_security_group" "c8-news-change-tracker-rds-sg" {
  name = "c8-news-change-tracker-rds-sg"
  description = "Security group that allows communcation all ports to RDS inbound and outbound"
  vpc_id = "vpc-0e0f897ec7ddc230d"
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "c8-news-change-tracker-rds-db" {
    allocated_storage    = 20
    db_name = "news"
    identifier = "c8-news-change-tracker-rds-db"
    engine               = "postgres"
    engine_version = "15.3"
    instance_class       = "db.t3.micro"
    username             = var.RDS_USERNAME
    password             = var.RDS_PASSWORD
    publicly_accessible = true
    performance_insights_enabled = false
    port = var.RDS_PORT
    db_subnet_group_name = "public_subnet_group"
    vpc_security_group_ids = [aws_security_group.c8-news-change-tracker-rds-sg.id]
    skip_final_snapshot = true
}

resource "aws_s3_bucket" "c8-news-change-tracker-bucket" {
  bucket = "c8-news-change-tracker-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "c8-news-change-tracker-bucket-versioning" {
  bucket = aws_s3_bucket.c8-news-change-tracker-bucket.id

  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_ecr_repository" "c8-news-change-tracker-etl-ecr" {
  name                 = "c8-news-change-tracker-etl-ecr"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_iam_role" "c8-news-change-tracker-ecs-role" {
  name = "c8-news-change-tracker-ecs-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_ecs_task_definition" "c8-news-change-tracker-etl-task-definition" {
  family                   = "c8-news-change-tracker-etl-task-definition"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 3072
  task_role_arn = aws_iam_role.c8-news-change-tracker-ecs-role.arn
  execution_role_arn = aws_iam_role.c8-news-change-tracker-ecs-role.arn
  
  container_definitions    = jsonencode(
  [ 
    {
    "name": "c8-news-change-tracker-etl-container",
    "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c8-news-change-tracker-etl-ecr:latest"
    "cpu": 1024,
    "memory": 3072,
    "essential": true,
    "portMappings": [
      {
        "containerPort": 80,
        "hostPort": 80,
      }, {
        "containerPort": 5432,
        "hostPort": 5432,
      }
    ]
    "environment": [
      {"name": "DB_NAME", "value": var.CONTAINER_DB_NAME},
      {"name": "DB_USER", "value": var.CONTAINER_DB_USER},
      {"name": "DB_PASSWORD", "value": var.CONTAINER_DB_PASSWORD},
      {"name": "DB_PORT", "value": var.CONTAINER_DB_PORT},
      {"name": "DB_HOST", "value": var.CONTAINER_DB_HOST }
    ]
    }
  ])
}

