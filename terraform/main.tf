# Validate only in CI; not applied.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "github_org" {
  type    = string
  default = "dardan-hoxhaj"
}

variable "github_repo" {
  type    = string
  default = "reliability-lab"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "billing_alarm_threshold_usd" {
  type    = number
  default = 10
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

resource "aws_ecr_repository" "reliability" {
  name                 = "reliability-lab"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = { project = "reliability-lab" }
}

data "aws_iam_policy_document" "github_oidc_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "github_oidc" {
  name               = "reliability-lab-github-oidc"
  assume_role_policy = data.aws_iam_policy_document.github_oidc_assume.json
}

data "aws_iam_policy_document" "ecr_push" {
  statement {
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
  statement {
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    resources = [aws_ecr_repository.reliability.arn]
  }
}

resource "aws_iam_role_policy" "ecr_push" {
  name   = "ecr-push"
  role   = aws_iam_role.github_oidc.id
  policy = data.aws_iam_policy_document.ecr_push.json
}

resource "aws_cloudwatch_metric_alarm" "billing" {
  alarm_name          = "reliability-lab-billing"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600
  statistic           = "Maximum"
  threshold           = var.billing_alarm_threshold_usd
  alarm_description   = "Billing alarm for the reliability-lab account. Create this before any apply."
  dimensions = {
    Currency = "USD"
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.reliability.repository_url
}

output "github_oidc_role_arn" {
  value = aws_iam_role.github_oidc.arn
}
