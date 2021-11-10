# Input variables for Terraform_DEPLOY_AHA.tf (AHA Solution deploy using terraform)
#
# Customize Alerts/Notifications
aha_primary_region="us-east-1"
aha_secondary_region=""
AWSOrganizationsEnabled="No"
AWSHealthEventType="issue | accountNotification | scheduledChange"

# Communication Channels - Slack/Microsoft Teams/Amazon Chime And/or EventBridge
SlackWebhookURL=""
MicrosoftTeamsWebhookURL=""
AmazonChimeWebhookURL=""
EventBusName=""

# Email Setup - For Alerting via Email
FromEmail="none@domain.com"
ToEmail="none@domain.com"
Subject="AWS Health Alert"

# More Configurations - Optional
# By default, AHA reports events affecting all AWS regions.
# If you want to report on certain regions you can enter up to 10 in a comma separated format.
EventSearchBack="1"
Regions="all regions"
ManagementAccountRoleArn=""
ExcludeAccountIDs=""

# Tags applied to all resources - using module provider. Update them per your requirement.
default_tags = {
  Application     = "AHA-Solution"
  Environment     = "PROD"
  auto-delete     = "no"
}

# commands to apply changes
# terraform init
# terraform plan
# terraform apply
