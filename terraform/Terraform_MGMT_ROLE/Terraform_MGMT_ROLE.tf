# Deploy Cross-Account Role for PHD access

# Parameters
provider "aws" {
    region  = var.aha_primary_region
    default_tags {
      tags = "${var.default_tags}"
    }
}

variable "aha_primary_region" {
    description = "Primary region where AHA solution will be deployed"
    type        = string
    default     = "us-east-1"
}

variable "default_tags" {
    description = "Tags used for the AWS resources created by this template"
    type        = map
    default     = {
      Application      = "AHA-Solution"
    }
}

variable "OrgMemberAccountId" {
  type = string 
  description = "AWS Account ID of the AWS Organizations Member Account that will run AWS Health Aware"

  validation {
    condition     = length(var.OrgMemberAccountId) == 12
    error_message = "The OrgMemberAccountId must be a valid AWS Account ID."
  }
}

# Random id generator
resource "random_string" "resource_code" {
  length  = 8
  special = false
  upper   = false
}

# aws_iam_role.AWSHealthAwareRoleForPHDEvents:
resource "aws_iam_role" "AWSHealthAwareRoleForPHDEvents" {
    assume_role_policy    = jsonencode(
        {
            Statement = [
                {
                    Action    = "sts:AssumeRole"
                    Effect    = "Allow"
                    Principal = {
                        AWS = "arn:aws:iam::${var.OrgMemberAccountId}:root"
                    }
                },
            ]
            Version   = "2012-10-17"
        }
    )
    name                  = "AWSHealthAwareRoleForPHDEvents-${random_string.resource_code.result}"
    description           = "Grants access to PHD event"
    path                  = "/"

    inline_policy {
        name   = "AllowHealthCalls"
        policy = jsonencode(
            {
                Statement = [
                    {
                        Action   = [
                            "health:DescribeAffectedAccountsForOrganization",
                            "health:DescribeAffectedEntitiesForOrganization",
                            "health:DescribeEventDetailsForOrganization",
                            "health:DescribeEventsForOrganization",
                            "health:DescribeEventDetails",
                            "health:DescribeEvents",
                            "health:DescribeEventTypes",
                            "health:DescribeAffectedEntities",
                        ]
                        Effect   = "Allow"
                        Resource = "*"
                    },
                ]
            }
        )
    }
    inline_policy {
        name   = "AllowsDescribeOrg"
        policy = jsonencode(
            {
                Statement = [
                    {
                        Action   = [
                            "organizations:ListAccounts",
                            "organizations:ListAWSServiceAccessForOrganization",
                            "organizations:DescribeAccount",
                        ]
                        Effect   = "Allow"
                        Resource = "*"
                    },
                ]
            }
        )
    }
}


output "AWSHealthAwareRoleForPHDEventsArn" {
  value       = aws_iam_role.AWSHealthAwareRoleForPHDEvents.arn
}

