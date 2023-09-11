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

resource "aws_ecs_cluster" "c8-news-change-tracker-cluster" {
  name = "c8-news-change-tracker-cluster"
}

resource "aws_security_group" "c8-news-change-tracker-scheduler-sg" {
  name = "c8-news-change-tracker-scheduler-sg"
  description = "Security group that listens on all ports inbound and outbound"
  vpc_id = "vpc-0e0f897ec7ddc230d"
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_scheduler_schedule" "c8-news-change-tracker-etl-pipeline-schedule" {
  name       = "c8-news-change-tracker-etl-pipeline-schedule"
  description = "Schedule for the etl pipeline of the news change tracker. When run the db will be updated with new news stories"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(*/30 * * * ? *)"
  

  target {
    arn      = aws_ecs_cluster.c8-news-change-tracker-cluster.arn
    role_arn = "arn:aws:iam::129033205317:role/service-role/Amazon_EventBridge_Scheduler_ECS_8655dce22e"

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.c8-news-change-tracker-etl-task-definition.arn + ""
      launch_type = "FARGATE"
      task_count = 1

     network_configuration {
      subnets = ["subnet-0667517a2a13e2a6b", "subnet-0cec5bdb9586ed3c4", "subnet-03b1a3e1075174995"]
      assign_public_ip = true
      security_groups = [ aws_security_group.c8-news-change-tracker-scheduler-sg.id ]
     }
     
    }
    retry_policy {
      maximum_retry_attempts = 5
      maximum_event_age_in_seconds = 3600
    }
  }
}

resource "aws_ecr_repository" "c8-news-change-tracker-comparison-pipeline-ecr" {
  name                 = "c8-news-change-tracker-comparison-pipeline-ecr"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecs_task_definition" "c8-news-change-tracker-comparison-pipeline-task-definition" {
  family                   = "c8-news-change-tracker-comparison-pipeline-task-definition"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 3072
  task_role_arn = aws_iam_role.c8-news-change-tracker-ecs-role.arn
  execution_role_arn = aws_iam_role.c8-news-change-tracker-ecs-role.arn
  
  container_definitions    = jsonencode(
  [ 
    {
    "name": "c8-news-change-tracker-comparison-pipeline-container",
    "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c8-news-change-tracker-comparison-pipeline-ecr:latest"
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

resource "aws_scheduler_schedule" "c8-news-change-tracker-comparison-pipeline-schedule" {
  name       = "c8-news-change-tracker-comparison-pipeline-schedule"
  description = "Schedule for the comparison pipeline of the news change tracker. When run, the data in the db will be compared against the current state of the data on the web."
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(* 1 * * ? *)"
  
  target {
    arn      = aws_ecs_cluster.c8-news-change-tracker-cluster.arn
    role_arn = "arn:aws:iam::129033205317:role/service-role/Amazon_EventBridge_Scheduler_ECS_8655dce22e"

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.c8-news-change-tracker-comparison-pipeline-task-definition.arn
      launch_type = "FARGATE"
      task_count = 1

     network_configuration {
      subnets = ["subnet-0667517a2a13e2a6b", "subnet-0cec5bdb9586ed3c4", "subnet-03b1a3e1075174995"]
      assign_public_ip = true
      security_groups = [ aws_security_group.c8-news-change-tracker-scheduler-sg.id ]
     }
     
    }
    retry_policy {
      maximum_retry_attempts = 5
      maximum_event_age_in_seconds = 3600
    }
  }
}

resource "aws_ecr_repository" "c8-news-change-tracker-dashboard-ecr" {
  name                 = "c8-news-change-tracker-dashboard-ecr"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecs_task_definition" "c8-news-change-tracker-dashboard-task-definition" {
  family                   = "c8-news-change-tracker-dashboard-task-definition"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 3072
  task_role_arn = aws_iam_role.c8-news-change-tracker-ecs-role.arn
  execution_role_arn = aws_iam_role.c8-news-change-tracker-ecs-role.arn
  
  container_definitions    = jsonencode(
  [ 
    {
    "name": "c8-news-change-tracker-dashboard-container",
    "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c8-news-change-tracker-dashboard-ecr:latest"
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

resource "aws_ecs_service" "c8-news-change-tracker-dashboard-service" {
  name            = "c8-news-change-tracker-dashboard-service"
  cluster         = aws_ecs_cluster.c8-news-change-tracker-cluster.id
  task_definition = aws_ecs_task_definition.c8-news-change-tracker-dashboard-task-definition.arn
  desired_count   = 3
  iam_role        = aws_iam_role.c8-news-change-tracker-ecs-role.arn

  network_configuration {
    subnets = ["subnet-0667517a2a13e2a6b", "subnet-0cec5bdb9586ed3c4", "subnet-03b1a3e1075174995"]
    assign_public_ip = true
    security_groups = [ aws_security_group.c8-news-change-tracker-scheduler-sg.id ]
  }

  ordered_placement_strategy {
    type  = "binpack"
    field = "cpu"
  }

  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.availability-zone in [us-west-2a, us-west-2b]"
  }
}