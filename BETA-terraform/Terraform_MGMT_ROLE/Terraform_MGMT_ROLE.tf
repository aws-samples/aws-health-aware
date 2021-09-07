# Deploy Cross-Account Role for PHD access

# Parameters
provider "aws" {
}

variable "OrgMemberAccountId" {
  type = string 
  description = "AWS Account ID of the AWS Organizations Member Account that will run AWS Health Aware"

  validation {
    condition     = length(var.OrgMemberAccountId) == 12
    error_message = "The OrgMemberAccountId must be a valid AWS Account ID."
  }
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
    name                  = "AWSHealthAwareRoleForPHDEvents"
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

