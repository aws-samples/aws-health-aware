# Terraform script to deploy AHA Solution
# 1.0 - Initial version 

# Variables defined below, you can overwrite them using tfvars or imput variables

data "aws_caller_identity" "current" {}

provider "aws" {
    region  = var.aha_primary_region
    default_tags {
      tags = "${var.default_tags}"
    }
}

# Secondary region - provider config
locals {
    secondary_region = "${var.aha_secondary_region == "" ? var.aha_primary_region : var.aha_secondary_region}"
}

provider "aws" {
    alias   = "secondary_region"
    region  = local.secondary_region
    default_tags {
      tags = "${var.default_tags}"
    }
}

# Comment below - if needed to use s3_bucket, s3_key for consistency with cf 
locals {
    source_files = ["../../handler.py", "../../messagegenerator.py"]
}
data "template_file" "t_file" {
    count = "${length(local.source_files)}"
    template = "${file(element(local.source_files, count.index))}"
}
data "archive_file" "lambda_zip" {
    type          = "zip"
    output_path   = "lambda_function.zip"
    source {
      filename = "${basename(local.source_files[0])}"
      content  = "${data.template_file.t_file.0.rendered}"
    }
    source {
      filename = "${basename(local.source_files[1])}"
      content  = "${data.template_file.t_file.1.rendered}"
  }
}

variable "aha_primary_region" {
    description = "Primary region where AHA solution will be deployed"
    type        = string
    default     = "us-east-1"
}

variable "aha_secondary_region" {
    description = "Secondary region where AHA solution will be deployed"
    type        = string
    default     = ""
}

variable "default_tags" {
    description = "Tags used for the AWS resources created by this template"
    type        = map
    default     = {
      Application      = "AHA-Solution"
    }
}

variable "dynamodbtable" {
    type    = string
    default = "AHA-DynamoDBTable"
}

variable "AWSOrganizationsEnabled" {
    type = string
    default = "No"
    description = "You can receive both PHD and SHD alerts if you're using AWS Organizations. \n If you are, make sure to enable Organizational Health View: \n (https://docs.aws.amazon.com/health/latest/ug/aggregate-events.html) to \n aggregate all PHD events in your AWS Organization. If not, you can still \n get SHD alerts."
    validation {
      condition = (
        var.AWSOrganizationsEnabled == "Yes" || var.AWSOrganizationsEnabled == "No"
      )
      error_message = "AWSOrganizationsEnabled variable can only accept Yes or No as values."
    }
}

variable "ManagementAccountRoleArn" {
    type    = string
    default = ""
    description = "Arn of the IAM role in the top-level management account for collecting PHD Events. 'None' if deploying into the top-level management account."
}

variable "AWSHealthEventType" {
    type = string
    default = "issue | accountNotification | scheduledChange"
    description = "Select the event type that you want AHA to report on. Refer to \n https://docs.aws.amazon.com/health/latest/APIReference/API_EventType.html for more information on EventType."
    validation {
      condition = (
        var.AWSHealthEventType == "issue | accountNotification | scheduledChange" || var.AWSHealthEventType == "issue"
      )
      error_message = "AWSHealthEventType variable can only accept issue | accountNotification | scheduledChange or issue as values."
    }
}

#variable "S3Bucket" {
#    type = string
#    description = "Name of your S3 Bucket where the AHA Package .zip resides. Just the name of the bucket (e.g. my-s3-bucket)"
#    validation {
#      condition     = length(var.S3Bucket) > 0
#      error_message = "The S3Bucket cannot be empty."
#    }
#}
#
#variable "S3Key" {
#    type = string
#    description = "Name of the .zip in your S3 Bucket. Just the name of the file (e.g. aha-v1.0.zip)"
#    validation {
#      condition     = length(var.S3Key) > 0
#      error_message = "The S3Key cannot be empty."
#    }
#}

variable "EventBusName" {
    type    = string
    default = ""
    description = "This is to ingest alerts into AWS EventBridge. Enter the event bus name if you wish to send the alerts to the AWS EventBridge. Note: By ingesting you wish to send the alerts to the AWS EventBridge. Note: By ingesting these alerts to AWS EventBridge, you can integrate with 35 SaaS vendors such as DataDog/NewRelic/PagerDuty. If you don't prefer to use EventBridge, leave the default (None)."
}

variable "SlackWebhookURL" {
    type    = string
    default = ""
    description = "Enter the Slack Webhook URL. If you don't prefer to use Slack, leave the default (empty)."
}

variable "MicrosoftTeamsWebhookURL" {
    type    = string
    default = ""
    description = "Enter Microsoft Teams Webhook URL. If you don't prefer to use MS Teams, leave the default (empty)."
}

variable "AmazonChimeWebhookURL" {
    type    = string
    default = ""
    description = "Enter the Chime Webhook URL, If you don't prefer to use Amazon Chime, leave the default (empty)."
}

variable "Regions" {
    type = string
    default = "all regions"
    description = "By default, AHA reports events affecting all AWS regions. \n If you want to report on certain regions you can enter up to 10 in a comma separated format. \n Available Regions: us-east-1,us-east-2,us-west-1,us-west-2,af-south-1,ap-east-1,ap-south-1,ap-northeast-3, \n ap-northeast-2,ap-southeast-1,ap-southeast-2,ap-northeast-1,ca-central-1,eu-central-1,eu-west-1,eu-west-2, \n eu-south-1,eu-south-3,eu-north-1,me-south-1,sa-east-1,global"
}

variable "EventSearchBack" {
    type = number
    default = "1"
    description = "How far back to search for events in hours. Default is 1 hour"
}

variable "FromEmail" {
    type = string
    default = "none@domain.com"
    description = "Enter FROM Email Address"
}

variable "ToEmail" {
    type = string
    default = "none@domain.com"
    description = "Enter email addresses separated by commas (for ex: abc@amazon.com, bcd@amazon.com)"
}

variable "Subject" {
    type = string
    default = "AWS Health Alert"
    description = "Enter the subject of the email address"
}

#variable "S3Bucket" {
#    type = string
#    description = "Name of your S3 Bucket where the AHA Package .zip resides. Just the name of the bucket (e.g. my-s3-bucket)"
#    default = ""
#}

variable "ExcludeAccountIDs" {
    type = string
    default = ""
    description = "If you would like to EXCLUDE any accounts from alerting, enter a .csv filename created with comma-seperated account numbers. Sample AccountIDs file name: aha_account_ids.csv. If not, leave the default empty."
}

##### Resources for AHA Solution created below.

# Random id generator
resource "random_string" "resource_code" {
  length  = 8
  special = false
  upper   = false
}

# S3 buckets creation
resource "aws_s3_bucket" "AHA-S3Bucket-PrimaryRegion" {
    count      = "${var.ExcludeAccountIDs != "" ? 1 : 0}"
    bucket     = "aha-bucket-${var.aha_primary_region}-${random_string.resource_code.result}"
    tags = {
      Name        = "aha-bucket"
    }
}

resource "aws_s3_bucket_acl" "AHA-S3Bucket-PrimaryRegion" {
    bucket = aws_s3_bucket.AHA-S3Bucket-PrimaryRegion[0].id
    acl    = "private"
}

resource "aws_s3_bucket" "AHA-S3Bucket-SecondaryRegion" {
    count      = "${var.aha_secondary_region != "" && var.ExcludeAccountIDs != "" ? 1 : 0}"
    provider   = aws.secondary_region
    bucket     = "aha-bucket-${var.aha_secondary_region}-${random_string.resource_code.result}"
    tags = {
      Name        = "aha-bucket"
    }
}

resource "aws_s3_bucket_acl" "AHA-S3Bucket-SecondaryRegion" {
    count  = "${var.aha_secondary_region != "" && var.ExcludeAccountIDs != "" ? 1 : 0}"
    provider   = aws.secondary_region
    bucket = aws_s3_bucket.AHA-S3Bucket-SecondaryRegion[0].id
    acl    = "private"
}

resource "aws_s3_object" "AHA-S3Object-PrimaryRegion" {
    count      = "${var.ExcludeAccountIDs != "" ? 1 : 0}"
    key        = var.ExcludeAccountIDs
    bucket     = aws_s3_bucket.AHA-S3Bucket-PrimaryRegion[0].bucket
    source     = var.ExcludeAccountIDs
    tags = {
      Name        = "${var.ExcludeAccountIDs}"
    }
}

resource "aws_s3_object" "AHA-S3Object-SecondaryRegion" {
    count      = "${var.aha_secondary_region != "" && var.ExcludeAccountIDs != "" ? 1 : 0}"
    provider   = aws.secondary_region
    key        = var.ExcludeAccountIDs
    bucket     = aws_s3_bucket.AHA-S3Bucket-SecondaryRegion[0].bucket
    source     = var.ExcludeAccountIDs
    tags = {
      Name        = "${var.ExcludeAccountIDs}"
    }
}

# DynamoDB table - Create if secondary region not set
resource "aws_dynamodb_table" "AHA-DynamoDBTable" {
    count = "${var.aha_secondary_region == "" ? 1 : 0}"
    billing_mode   = "PROVISIONED"
    hash_key       = "arn"
    name           = "${var.dynamodbtable}-${random_string.resource_code.result}"
    read_capacity  = 5
    write_capacity = 5
    stream_enabled = false
    tags           = {
       Name   = "${var.dynamodbtable}"
    }

    attribute {
        name = "arn"
        type = "S"
    }

    point_in_time_recovery {
        enabled = false
    }

    timeouts {}

    ttl {
        attribute_name = "ttl"
        enabled        = true
    }
}

# DynamoDB table - Multi region Global Table - Create if secondary region is set
resource "aws_dynamodb_table" "AHA-GlobalDynamoDBTable" {
    count = "${var.aha_secondary_region == "" ? 0 : 1}"
    billing_mode     = "PAY_PER_REQUEST"
    hash_key         = "arn"
    name             = "${var.dynamodbtable}-${random_string.resource_code.result}"
    stream_enabled   = true
    stream_view_type = "NEW_AND_OLD_IMAGES"
    tags           = {
       Name   = "${var.dynamodbtable}"
    }

    attribute {
        name = "arn"
        type = "S"
    }

    point_in_time_recovery {
        enabled = false
    }

    replica {
        region_name = var.aha_secondary_region
    }

    timeouts {}

    ttl {
        attribute_name = "ttl"
        enabled        = true
    }
}
# Tags for DynamoDB - secondary region
resource "aws_dynamodb_tag" "AHA-GlobalDynamoDBTable" {
    count = "${var.aha_secondary_region == "" ? 0 : 1}"
    provider   = aws.secondary_region
    resource_arn = replace(aws_dynamodb_table.AHA-GlobalDynamoDBTable[count.index].arn, var.aha_primary_region, var.aha_secondary_region)
    key          = "Name"
    value        = "${var.dynamodbtable}"
}
# Tags for DynamoDB - secondary region - default_tags
resource "aws_dynamodb_tag" "AHA-GlobalDynamoDBTable-Additional-tags" {
    for_each = { for key, value in var.default_tags : key => value if var.aha_secondary_region != "" }
    provider   = aws.secondary_region
    resource_arn = replace(aws_dynamodb_table.AHA-GlobalDynamoDBTable[0].arn, var.aha_primary_region, var.aha_secondary_region)
    key          = each.key
    value        = each.value
}

# Secrets - SlackChannelSecret
resource "aws_secretsmanager_secret" "SlackChannelID" {
    count = "${var.SlackWebhookURL == "" ? 0 : 1}"
    name             = "SlackChannelID"
    description      = "Slack Channel ID Secret"
    recovery_window_in_days      = 0
    tags             = {
        "HealthCheckSlack" = "ChannelID"
    }
    dynamic "replica" {
      for_each = var.aha_secondary_region == "" ? [] : [1]
      content {
        region = var.aha_secondary_region
      }
    }
}
resource "aws_secretsmanager_secret_version" "SlackChannelID" {
    count = "${var.SlackWebhookURL == "" ? 0 : 1}"
    secret_id     = "${aws_secretsmanager_secret.SlackChannelID.*.id[count.index]}"
    secret_string = "${var.SlackWebhookURL}"
}

# Secrets - MicrosoftChannelSecret
resource "aws_secretsmanager_secret" "MicrosoftChannelID" {
    count = "${var.MicrosoftTeamsWebhookURL == "" ? 0 : 1}"
    name             = "MicrosoftChannelID"
    description      = "Microsoft Channel ID Secret"
    recovery_window_in_days      = 0
    tags             = {
        "HealthCheckMicrosoft" = "ChannelID"
        "Name"                 = "AHA-MicrosoftChannelID"
    }
    dynamic "replica" {
      for_each = var.aha_secondary_region == "" ? [] : [1]
      content {
        region = var.aha_secondary_region
      }
    }
}
resource "aws_secretsmanager_secret_version" "MicrosoftChannelID" {
    count = "${var.MicrosoftTeamsWebhookURL == "" ? 0 : 1}"
    secret_id     = "${aws_secretsmanager_secret.MicrosoftChannelID.*.id[count.index]}"
    secret_string = "${var.MicrosoftTeamsWebhookURL}"
}

# Secrets - EventBusNameSecret
resource "aws_secretsmanager_secret" "EventBusName" {
    count = "${var.EventBusName == "" ? 0 : 1}"
    name             = "EventBusName"
    description      = "EventBus Name Secret"
    recovery_window_in_days      = 0
    tags             = {
        "EventBusName" = "ChannelID"
        "Name"         = "AHA-EventBusName"
    }
    dynamic "replica" {
      for_each = var.aha_secondary_region == "" ? [] : [1]
      content {
        region = var.aha_secondary_region
      }
    }
}

resource "aws_secretsmanager_secret_version" "EventBusName" {
    count = "${var.EventBusName == "" ? 0 : 1}"
    secret_id     = "${aws_secretsmanager_secret.EventBusName.*.id[count.index]}"
    secret_string = "${var.EventBusName}"
}

# Secrets - ChimeChannelSecret
resource "aws_secretsmanager_secret" "ChimeChannelID" {
    count = "${var.AmazonChimeWebhookURL == "" ? 0 : 1}"
    name             = "ChimeChannelID"
    description      = "Chime Channel ID Secret"
    recovery_window_in_days      = 0
    tags             = {
        "HealthCheckChime" = "ChannelID"
        "Name"             = "AHA-ChimeChannelID-${random_string.resource_code.result}"
    }
    dynamic "replica" {
      for_each = var.aha_secondary_region == "" ? [] : [1]
      content {
        region = var.aha_secondary_region
      }
    }
}
resource "aws_secretsmanager_secret_version" "ChimeChannelID" {
    count = "${var.AmazonChimeWebhookURL == "" ? 0 : 1}"
    secret_id     = "${aws_secretsmanager_secret.ChimeChannelID.*.id[count.index]}"
    secret_string = "${var.AmazonChimeWebhookURL}"
}

# Secrets - AssumeRoleSecret
resource "aws_secretsmanager_secret" "AssumeRoleArn" {
    count = "${var.ManagementAccountRoleArn == "" ? 0 : 1}"
    name             = "AssumeRoleArn"
    description      = "Management account role for AHA to assume"
    recovery_window_in_days      = 0
    tags             = {
        "AssumeRoleArn" = ""
        "Name"          = "AHA-AssumeRoleArn"
    }
    dynamic "replica" {
      for_each = var.aha_secondary_region == "" ? [0] : [1]
      content {
        region = var.aha_secondary_region
      }
    }
}
resource "aws_secretsmanager_secret_version" "AssumeRoleArn" {
    count = "${var.ManagementAccountRoleArn == "" ? 0 : 1}"
    secret_id     = "${aws_secretsmanager_secret.AssumeRoleArn.*.id[count.index]}"
    secret_string = "${var.ManagementAccountRoleArn}"
}

# IAM Role for Lambda function execution
resource "aws_iam_role" "AHA-LambdaExecutionRole" {
    name                  = "AHA-LambdaExecutionRole-${random_string.resource_code.result}"
    path                  = "/"
    assume_role_policy    = jsonencode(
        {
            Version   = "2012-10-17"
            Statement = [
                {
                    Action    = "sts:AssumeRole"
                    Effect    = "Allow"
                    Principal = {
                        Service = "lambda.amazonaws.com"
                    }
                },
            ]
        }
    )
    inline_policy {
        name   = "AHA-LambdaPolicy"
        policy = data.aws_iam_policy_document.AHA-LambdaPolicy-Document.json
    }
    tags             = {
        "Name"             = "AHA-LambdaExecutionRole"
    }
}

data "aws_iam_policy_document" "AHA-LambdaPolicy-Document" {
  version   = "2012-10-17"
  statement {
    effect = "Allow"
    actions = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
    ]
    resources = [
          "arn:aws:logs:${var.aha_primary_region}:${data.aws_caller_identity.current.account_id}:*",
          "arn:aws:logs:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:*"
    ]
  }
  statement {
    effect   = "Allow"
    actions   = [
          "health:DescribeAffectedAccountsForOrganization",
          "health:DescribeAffectedEntitiesForOrganization",
          "health:DescribeEventDetailsForOrganization",
          "health:DescribeEventsForOrganization",
          "health:DescribeEventDetails",
          "health:DescribeEvents",
          "health:DescribeEventTypes",
          "health:DescribeAffectedEntities",
          "organizations:ListAccounts",
          "organizations:DescribeAccount",
    ]
    resources = [ "*" ]
  }
  statement {
    effect   = "Allow"
    actions   = [
          "dynamodb:ListTables",
    ]
    resources = [
          "arn:aws:dynamodb:${var.aha_primary_region}:${data.aws_caller_identity.current.account_id}:*",
          "arn:aws:dynamodb:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:*",
    ]
  }
  statement {
    effect   = "Allow"
    actions   = [
          "ses:SendEmail",
    ]
    resources = [
          "arn:aws:ses:${var.aha_primary_region}:${data.aws_caller_identity.current.account_id}:*",
          "arn:aws:ses:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:*",
    ]
  }
  statement {
    effect   = "Allow"
    actions   = [
          "dynamodb:UpdateTimeToLive",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:UpdateTable",
          "dynamodb:GetRecords",
    ]
    resources = [
          #aws_dynamodb_table.AHA-DynamoDBTable.arn
          "arn:aws:dynamodb:${var.aha_primary_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodbtable}-${random_string.resource_code.result}",
          "arn:aws:dynamodb:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodbtable}-${random_string.resource_code.result}",
    ]
  }
  dynamic "statement" {
    for_each = var.SlackWebhookURL == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:GetSecretValue",
      ]
      resources = [
          aws_secretsmanager_secret.SlackChannelID[0].arn,
          "arn:aws:secretsmanager:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:secret:${element(split(":", aws_secretsmanager_secret.SlackChannelID[0].arn),6)}"
#          var.aha_secondary_region != "" ? "arn:aws:secretsmanager:${var.aha_secondary_region}:${data.aws_caller_identity.current.account_id}:secret:${element(split(":", aws_secretsmanager_secret.SlackChannelID[0].arn),6)}" : null
      ]
    }
  }
  dynamic "statement" {
    for_each = var.MicrosoftTeamsWebhookURL == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:GetSecretValue",
      ]
      resources = [
          aws_secretsmanager_secret.MicrosoftChannelID[0].arn,
          "arn:aws:secretsmanager:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:secret:${element(split(":", aws_secretsmanager_secret.MicrosoftChannelID[0].arn),6)}"
      ]
    }
  }
  dynamic "statement" {
    for_each = var.AmazonChimeWebhookURL == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:GetSecretValue",
      ]
      resources = [
          aws_secretsmanager_secret.ChimeChannelID[0].arn,
          "arn:aws:secretsmanager:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:secret:${element(split(":", aws_secretsmanager_secret.ChimeChannelID[0].arn),6)}"
      ]
    }
  }
  dynamic "statement" {
    for_each = var.EventBusName == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:GetSecretValue",
      ]
      resources = [
          aws_secretsmanager_secret.EventBusName[0].arn,
          "arn:aws:secretsmanager:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:secret:${element(split(":", aws_secretsmanager_secret.EventBusName[0].arn),6)}"
      ]
    }
  }
  dynamic "statement" {
    for_each = var.ManagementAccountRoleArn == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:GetSecretValue",
      ]
      resources = [
          aws_secretsmanager_secret.AssumeRoleArn[0].arn,
          "arn:aws:secretsmanager:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:secret:${element(split(":", aws_secretsmanager_secret.AssumeRoleArn[0].arn),6)}"
      ]
    }
  }
  dynamic "statement" {
    for_each = var.EventBusName == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "events:PutEvents",
      ]
      resources = [
          "arn:aws:events:${var.aha_primary_region}:${data.aws_caller_identity.current.account_id}:event-bus/${var.EventBusName}",
          "arn:aws:events:${local.secondary_region}:${data.aws_caller_identity.current.account_id}:event-bus/${var.EventBusName}"
      ]
    }
  }
  dynamic "statement" {
    for_each = var.ManagementAccountRoleArn == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "sts:AssumeRole",
      ]
      resources = [
          "${var.ManagementAccountRoleArn}",
      ]
    }
  }
  dynamic "statement" {
    for_each = var.ExcludeAccountIDs == "" ? [] : [1]
    content {
      effect = "Allow"
      actions = [
          "s3:GetObject",
      ]
      resources = [
          "arn:aws:s3:::aha-bucket-${var.aha_primary_region}-${random_string.resource_code.result}/${var.ExcludeAccountIDs}",
          "arn:aws:s3:::aha-bucket-${local.secondary_region}-${random_string.resource_code.result}/${var.ExcludeAccountIDs}",
      ]
    }
  }
}
# aws_lambda_function - AHA-LambdaFunction - Primary region
resource "aws_lambda_function" "AHA-LambdaFunction-PrimaryRegion" {
    description                    = "Lambda function that runs AHA"
    function_name                  = "AHA-LambdaFunction-${random_string.resource_code.result}"
    handler                        = "handler.main"
    memory_size                    = 128
    timeout                        = 600
    filename                       = data.archive_file.lambda_zip.output_path
    source_code_hash               = filebase64sha256(data.archive_file.lambda_zip.output_path)
#    s3_bucket                      = var.S3Bucket
#    s3_key                         = var.S3Key
    reserved_concurrent_executions = -1
    role                           = aws_iam_role.AHA-LambdaExecutionRole.arn
    runtime                        = "python3.8"

    environment {
        variables = {
            "DYNAMODB_TABLE"      = "${var.dynamodbtable}-${random_string.resource_code.result}"
            "EMAIL_SUBJECT"       = var.Subject
            "EVENT_SEARCH_BACK"   = var.EventSearchBack
            "FROM_EMAIL"          = var.FromEmail
            "HEALTH_EVENT_TYPE"   = var.AWSHealthEventType
            "ORG_STATUS"          = var.AWSOrganizationsEnabled
            "REGIONS"             = var.Regions
            "TO_EMAIL"            = var.ToEmail
            "MANAGEMENT_ROLE_ARN" = var.ManagementAccountRoleArn
            "ACCOUNT_IDS"         = var.ExcludeAccountIDs
            "S3_BUCKET"           = join("",aws_s3_bucket.AHA-S3Bucket-PrimaryRegion[*].bucket)
        }
    }

    timeouts {}

    tracing_config {
        mode = "PassThrough"
    }
    tags             = {   
        "Name"             = "AHA-LambdaFunction"
    }
    depends_on = [
      aws_dynamodb_table.AHA-DynamoDBTable,
      aws_dynamodb_table.AHA-GlobalDynamoDBTable,
    ]
}

# aws_lambda_function - AHA-LambdaFunction - Secondary region
resource "aws_lambda_function" "AHA-LambdaFunction-SecondaryRegion" {
    count                          = "${var.aha_secondary_region == "" ? 0 : 1}"
    provider                       = aws.secondary_region
    description                    = "Lambda function that runs AHA"
    function_name                  = "AHA-LambdaFunction-${random_string.resource_code.result}"
    handler                        = "handler.main"
    memory_size                    = 128
    timeout                        = 600
    filename                       = data.archive_file.lambda_zip.output_path
    source_code_hash               = filebase64sha256(data.archive_file.lambda_zip.output_path)
#    s3_bucket                      = var.S3Bucket
#    s3_key                         = var.S3Key
    reserved_concurrent_executions = -1
    role                           = aws_iam_role.AHA-LambdaExecutionRole.arn
    runtime                        = "python3.8"

    environment {
        variables = {
            "DYNAMODB_TABLE"      = "${var.dynamodbtable}-${random_string.resource_code.result}"
            "EMAIL_SUBJECT"       = var.Subject
            "EVENT_SEARCH_BACK"   = var.EventSearchBack
            "FROM_EMAIL"          = var.FromEmail
            "HEALTH_EVENT_TYPE"   = var.AWSHealthEventType
            "ORG_STATUS"          = var.AWSOrganizationsEnabled
            "REGIONS"             = var.Regions
            "TO_EMAIL"            = var.ToEmail
            "MANAGEMENT_ROLE_ARN" = var.ManagementAccountRoleArn
            "ACCOUNT_IDS"         = var.ExcludeAccountIDs
            "S3_BUCKET"           = join("",aws_s3_bucket.AHA-S3Bucket-SecondaryRegion[*].bucket)
        }
    }

    timeouts {}

    tracing_config {
        mode = "PassThrough"
    }
    tags             = {
        "Name"             = "AHA-LambdaFunction"
    }
    depends_on = [
      aws_dynamodb_table.AHA-DynamoDBTable,
      aws_dynamodb_table.AHA-GlobalDynamoDBTable,
    ]
}

# EventBridge - Schedule to run lambda
resource "aws_cloudwatch_event_rule" "AHA-LambdaSchedule-PrimaryRegion" {
    description         = "Lambda trigger Event"
    event_bus_name      = "default"
    is_enabled          = true
    name                = "AHA-LambdaSchedule-${random_string.resource_code.result}"
    schedule_expression = "rate(1 minute)"
    tags             = {
        "Name"             = "AHA-LambdaSchedule"
    }
}
resource "aws_cloudwatch_event_rule" "AHA-LambdaSchedule-SecondaryRegion" {
    count               = "${var.aha_secondary_region == "" ? 0 : 1}"
    provider            = aws.secondary_region    
    description         = "Lambda trigger Event"
    event_bus_name      = "default"
    is_enabled          = true
    name                = "AHA-LambdaSchedule-${random_string.resource_code.result}"
    schedule_expression = "rate(1 minute)"
    tags             = {
        "Name"             = "AHA-LambdaSchedule"
    }
}

resource "aws_cloudwatch_event_target" "AHA-LambdaFunction-PrimaryRegion" {
    arn            = aws_lambda_function.AHA-LambdaFunction-PrimaryRegion.arn
    rule           = aws_cloudwatch_event_rule.AHA-LambdaSchedule-PrimaryRegion.name
}
resource "aws_cloudwatch_event_target" "AHA-LambdaFunction-SecondaryRegion" {
    count          = "${var.aha_secondary_region == "" ? 0 : 1}"
    provider       = aws.secondary_region    
    arn            = aws_lambda_function.AHA-LambdaFunction-SecondaryRegion[0].arn
    rule           = aws_cloudwatch_event_rule.AHA-LambdaSchedule-SecondaryRegion[0].name
}

resource "aws_lambda_permission" "AHA-LambdaSchedulePermission-PrimaryRegion" {
    action        = "lambda:InvokeFunction"
    principal     = "events.amazonaws.com"
    function_name = aws_lambda_function.AHA-LambdaFunction-PrimaryRegion.arn
    source_arn    = aws_cloudwatch_event_rule.AHA-LambdaSchedule-PrimaryRegion.arn
}
resource "aws_lambda_permission" "AHA-LambdaSchedulePermission-SecondaryRegion" {
    count         = "${var.aha_secondary_region == "" ? 0 : 1}"
    provider      = aws.secondary_region    
    action        = "lambda:InvokeFunction"
    principal     = "events.amazonaws.com"
    function_name = aws_lambda_function.AHA-LambdaFunction-SecondaryRegion[0].arn
    source_arn    = aws_cloudwatch_event_rule.AHA-LambdaSchedule-SecondaryRegion[0].arn
}

