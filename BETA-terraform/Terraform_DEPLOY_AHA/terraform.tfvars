# Input variables for 02_Terraform_deploy.AHA.tf (AHA Solution deploy using terraform)
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
# Skip sending alerts containing the following CSV list of strings e.g. AWS_VPN_SINGLE_TUNNEL_NOTIFICATION,AWS_VPN_REDUNDANCY_LOSS 
SkipList=""

# commands to apply changes
# terraform init
# terraform plan
# terraform apply
