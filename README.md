
![](https://github.com/aws-samples/aws-health-aware/blob/main/readme-images/aha_banner.png?raw=1)


**Table of Contents**

- [Introduction](#introduction)
- [Architecture](#architecture)
- [Configuring an Endpoint](#configuring-an-endpoint)
  * [Creating a Amazon Chime Webhook URL](#creating-a-amazon-chime-webhook-url)
  * [Creating a Slack Webhook URL](#creating-a-slack-webhook-url)
  * [Creating a Microsoft Teams Webhook URL](#creating-a-microsoft-teams-webhook-url)
  * [Configuring an Email](#configuring-an-email)
  * [Creating a Amazon EventBridge Ingestion ARN](#creating-a-amazon-eventbridge-ingestion-arn)
- [Deployment Options](#deployment-options) 
  - [CloudFormation](#cloudformation) 
    * [AHA for users WITHOUT AWS Organizations](#aha-without-aws-organizations-using-cloudformation)
    * [AHA for users WITH AWS Organizations (Management Account)](#aha-with-aws-organizations-on-management-account-using-cloudformation)
    * [AHA for users WITH AWS Organizations (Member Account)](#aha-with-aws-organizations-on-member-account-using-cloudformation)
  - [Terraform](#terraform)
    * [AHA for users WITHOUT AWS Organizations ](#aha-without-aws-organizations-using-terraform)
    * [AHA for users WITH AWS Organizations (Management Account)](#aha-with-aws-organizations-on-management-account-using-terraform)    
    * [AHA for users WITH AWS Organizations (Member Account)](#aha-with-aws-organizations-on-member-account-using-terraform)
- [Updating using CloudFormation](#updating-using-cloudformation)
- [Updating using Terraform](#updating-using-terraform)
- [New Features](#new-features)
- [Troubleshooting](#troubleshooting)

# Introduction
AWS Health Aware (AHA) is an automated notification tool for sending well-formatted AWS Health Alerts to Amazon Chime, Slack, Microsoft Teams, E-mail or an AWS Eventbridge compatible endpoint as long as you have Business or Enterprise Support.

# Architecture

## Single Region
![](https://github.com/aws-samples/aws-health-aware/blob/main/readme-images/aha-arch-single-region.png?raw=1)

## Multi Region
![](https://github.com/aws-samples/aws-health-aware/blob/main/readme-images/aha-arch-multi-region.png?raw=1)

## Created AWS Resources

| Resource | Description                    |
| ------------- | ------------------------------ |
| `DynamoDBTable`      | DynamoDB Table used to store Event ARNs, updates and TTL       |
| `ChimeChannelSecret`   | Webhook URL for Amazon Chime stored in AWS Secrets Manager      |
| `EventBusNameSecret`   | EventBus ARN for Amazon EventBridge stored in AWS Secrets Manager     |
| `LambdaExecutionRole`      | IAM role used for LambdaFunction       |
| `LambdaFunction`   | Main Lambda function that reads from AWS Health API, sends to endpoints and writes to DynamoDB     |
| `LambdaSchedule`      | Amazon EventBridge rule that runs every min to invoke LambdaFunction       |
| `LambdaSchedulePermission`   | IAM Role used for LambdaSchedule     |
| `MicrosoftChannelSecret`      | Webhook URL for Microsoft Teams stored in AWS Secrets Manager       |
| `SlackChannelSecret`   | Webhook URL for Slack stored in AWS Secrets Manager     |

# Configuring an Endpoint
AHA can send to multiple endpoints (webhook URLs, Email or EventBridge). To use any of these you'll need to set it up before-hand as some of these are done on 3rd party websites. We'll go over some of the common ones here.

## Creating a Amazon Chime Webhook URL
**You will need to have access to create a Amazon Chime room and manage webhooks.**

1. Create a new [chat room](https://docs.aws.amazon.com/chime/latest/ug/chime-chat-room.html) for events (i.e. aws_events).   
2. In the chat room created in step 1, **click** on the gear icon and **click** *manage webhooks and bots*.   
3. **Click** *Add webhook*.   
4. **Type** a name for the bot (e.g. AWS Health Bot) and **click** *Create*.   
5. **Click** *Copy URL*, we will need it for the deployment.

## Creating a Slack Webhook URL
**You will need to have access to add a new channel and app to your Slack Workspace**.

*Webhook*
1. Create a new [channel](https://slack.com/help/articles/201402297-Create-a-channel) for events (i.e. aws_events)
2. In your browser go to: workspace-name.slack.com/apps where workspace-name is the name of your Slack Workspace.
3. In the search bar, search for: *Incoming Webhooks* and **click** on it.
4. **Click** on *Add to Slack*.
5. From the dropdown **click** on the channel your created in step 1 and **click** *Add Incoming Webhooks integration*.
6. From this page you can change the name of the webhook (i.e. AWS Bot), the icon/emoji to use, etc.
7. For the deployment we will need the *Webhook URL*.

*Workflow*

1. Create a new [channel](https://slack.com/help/articles/201402297-Create-a-channel) for events (i.e. aws_events)
2. Within Slack **click** on your workspace name drop down arrow in the upper left. **click on Tools > Workflow Builder**  
3. **Click** Create in the upper right hand corner of the Workflow Builder and give your workflow a name **click** next.
4. **Click** on *select* next to **Webhook** and then **click** *add variable* add the following variables one at a time in the *Key* section. All *data type* will be *text*:  
-text  
-accounts  
-resources  
-service  
-region  
-status  
-start_time  
-event_arn  
-updates  
5. When done you should have 9 variables, double check them as they are case sensitive and will be referenced. When checked **click** on *done* and *next*.
6. **Click** on *add step* and then on the add a workflow step **click** *add* next to *send a message*.
7. Under *send this message to:* select the channel you created in Step 1 in *message text* you can should recreate this following:  
![](https://github.com/aws-samples/aws-health-aware/blob/main/readme-images/workflow.png?raw=1)
8. **Click** *save* and the **click** *publish*
9. For the deployment we will need the *Webhook URL*.

## Creating a Microsoft Teams Webhook URL
**You will need to have access to add a new channel and app to your Microsoft Teams channel**.

1. Create a new [channel](https://docs.microsoft.com/en-us/microsoftteams/get-started-with-teams-create-your-first-teams-and-channels) for events (i.e. aws_events)
2. Within your Microsoft Team go to *Apps*
3. In the search bar, search for: *Incoming Webhook* and **click** on it.   
4. **Click** on *Add to team*.   
5. **Type** in the name of your on the channel your created in step 1 and **click** *Set up a connector*.   
6. From this page you can change the name of the webhook (i.e. AWS Bot), the icon/emoji to use, etc. **Click** *Create* when done.  
7. For the deployment we will need the webhook *URL* that is presented.

## Configuring an Email

1. You'll be able to send email alerts to one or many addresses. However, you must first [verify](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses-procedure.html) the email(s) in the Simple Email Service (SES) console.
2. AHA utilizes Amazon SES so all you need is to enter in a To: address and a From: address.
3. You *may* have to allow a rule in your environment so that the emails don't get labeled as SPAM. This will be something you have to congfigure on your own.

## Creating a Amazon EventBridge Ingestion ARN

1.	In the AWS Console, search for **Amazon EventBridge**.
2.	On the left hand side, **click** *Event buses*.
3.	Under *Custom event* bus **click** *Create event bus*
4.	Give your Event bus a name and **click** *Create*.
5.  For the deployment we will need the *Name* of the Event bus **(not the ARN)**.

# Deployment Options

## CloudFormation
There are 3 available ways to deploy AHA, all are done via the same CloudFormation template to make deployment as easy as possible.

The 3 deployment methods for AHA are:

1. [**AHA for users WITHOUT AWS Organizations**](#aha-without-aws-organizations-using-cloudformation): Users NOT using AWS Organizations.
2. [**AHA for users WITH AWS Organizations (Management Account)**](#aha-with-aws-organizations-on-management-account-using-cloudformation): Users who ARE using AWS Organizations and deploying in the top-level management account.
3. [**AHA for users WITH AWS Organizations (Member Account)**](#aha-with-aws-organizations-on-member-account-using-cloudformation): Users who ARE using AWS Organizations and deploying in a member account in the organization to assume a role in the top-level management account.

## AHA Without AWS Organizations using CloudFormation

### Prerequisites

1. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)
2. Have access to deploy Cloudformation Templates with the following resources: AWS IAM policies, Amazon DynamoDB Tables, AWS Lambda, Amazon EventBridge and AWS Secrets Manager.
3. If using Multi-Region, you must deploy the following 2 CloudFormation templates to allow the Stackset deployment to deploy resources **even if you have full administrator privileges, you still need to follow these steps**.
 - In CloudFormation Console create a stack with new resources from the following S3 URL: https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetAdministrationRole.yml - this will allows CFT Stacksets to launch AHA in another region
 - Launch the stack.
 - In CloudFormation Console create a stack with new resources from the following S3 URL: https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetExecutionRole.yml) - In *AdministratorAccountId* type in the 12 digit account number you're running the solution in (e.g. 000123456789)
 - Launch the stack.

### Deployment

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
2. In the root of this package you'll have two files; `handler.py` and `messagegenerator.py`. Use your tool of choice to zip them both up and name them with a unique name (e.g. aha-v1.8.zip). **Note: Putting the version number in the name will make upgrading AHA seamless.**
3. Upload the .zip you created in Step 1 to an S3 in the same region you plan to deploy this in.   
4. In your AWS console go to *CloudFormation*.   
5. In the *CloudFormation* console **click** *Create stack > With new resources (standard)*.   
6. Under *Template Source* **click** *Upload a template file* and **click** *Choose file*  and select `CFN_DEPLOY_AHA.yml` **Click** *Next*.   
 - In *Stack name* type a stack name (i.e. AHA-Deployment).   
 - In *AWSOrganizationsEnabled* leave it set to default which is `No`. If you do have AWS Organizations enabled and you want to aggregate across all your accounts, you should be following the step for [AHA for users who ARE using AWS Organizations](#aha-with-aws-organizations-using-terraform)  
 - In *AWSOrganizationsEnabled* leave it set to default which is `No`. If you do have AWS Organizations enabled and you want to aggregate across all your accounts, you should be following the steps for [AHA for users who ARE using AWS Organizations (Management Account)](#aha-with-aws-organizations-on-management-account-using-cloudformation) or [AHA for users WITH AWS Organizations (Member Account)](#aha-with-aws-organizations-on-member-account-using-cloudformation)
 - In *AWSHealthEventType* select whether you want to receive *all* event types or *only* issues.   
 - In *S3Bucket* type ***just*** the bucket name of the S3 bucket used in step 3  (e.g. my-aha-bucket).    
 - In *S3Key* type ***just*** the name of the .zip file you created in Step 2 (e.g. aha-v1.8.zip).     
 - In the *Communications Channels* section enter the URLs, Emails and/or ARN of the endpoints you configured previously.  
 - In the *Email Setup* section enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
 - In *EventSearchBack* enter in the amount of hours you want to search back for events. Default is 1 hour.  
 - In *Regions* enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated (e.g. us-east-1, us-east-2).
 - In *ARN of the AWS Organizations Management Account assume role* leave it set to default None as this is only for customers using AWS Organizations.
 - In *Deploy in secondary region?* select another region to deploy AHA in. Otherwise leave to default No.
7. Scroll to the bottom and **click** *Next*. 
8. Scroll to the bottom and **click** *Next* again.
9. Scroll to the bottom and **click** the *checkbox* and **click** *Create stack*.   
10. Wait until *Status* changes to *CREATE_COMPLETE* (roughly 2-4 minutes or if deploying in a secondary region, it can take up to 30 minutes).   

## AHA With AWS Organizations on Management Account using CloudFormation

### Prerequisites

1. [Enable Health Organizational View](https://docs.aws.amazon.com/health/latest/ug/enable-organizational-view-in-health-console.html) from the console, so that you can aggregate all Personal Health Dashboard (PHD) events for all accounts in your AWS Organization. 
2. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)
3. Have access to deploy Cloudformation Templates with the following resources: AWS IAM policies, Amazon DynamoDB Tables, AWS Lambda, Amazon EventBridge and AWS Secrets Manager in the **AWS Organizations Master Account**.
4. If using Multi-Region, you must deploy the following 2 CloudFormation templates to allow the Stackset deployment to deploy resources **even if you have full administrator privileges, you still need to follow these steps**.
 - In CloudFormation Console create a stack with new resources from the following S3 URL: https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetAdministrationRole.yml - this will allows CFT Stacksets to launch AHA in another region
 - Launch the stack.
 - In CloudFormation Console create a stack with new resources from the following S3 URL: https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetExecutionRole.yml) - In *AdministratorAccountId* type in the 12 digit account number you're running the solution in (e.g. 000123456789)
 - Launch the stack.

### Deployment

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
2. In the root of this package you'll have two files; `handler.py` and `messagegenerator.py`. Use your tool of choice to zip them both up and name them with a unique name (e.g. aha-v1.8.zip). **Note: Putting the version number in the name will make upgrading AHA seamless.**
3. Upload the .zip you created in Step 1 to an S3 in the same region you plan to deploy this in.   
4. In your AWS console go to *CloudFormation*.   
5. In the *CloudFormation* console **click** *Create stack > With new resources (standard)*.   
6. Under *Template Source* **click** *Upload a template file* and **click** *Choose file*  and select `CFN_DEPLOY_AHA.yml` **Click** *Next*.   
 - In *Stack name* type a stack name (i.e. AHA-Deployment).
 - In *AWSOrganizationsEnabled* change the dropdown to `Yes`. If you do NOT have AWS Organizations enabled you should be following the steps for [AHA for users who are NOT using AWS Organizations](#aha-without-aws-organizations-using-cloudformation)  
 - In *AWSHealthEventType* select whether you want to receive *all* event types or *only* issues.   
 - In *S3Bucket* type ***just*** the bucket name of the S3 bucket used in step 3  (e.g. my-aha-bucket).    
 - In *S3Key* type ***just*** the name of the .zip file you created in Step 2 (e.g. aha-v1.8.zip).     
 - In the *Communications Channels* section enter the URLs, Emails and/or ARN of the endpoints you configured previously.  
 - In the *Email Setup* section enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
 - In *EventSearchBack* enter in the amount of hours you want to search back for events. Default is 1 hour.  
 - In *Regions* enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated with (e.g. us-east-1, us-east-2).
 - In *ARN of the AWS Organizations Management Account assume role* leave it set to default None.
 - In *Deploy in secondary region?* select another region to deploy AHA in. Otherwise leave to default No.
7. Scroll to the bottom and **click** *Next*. 
8. Scroll to the bottom and **click** *Next* again.   
9. Scroll to the bottom and **click** the *checkbox* and **click** *Create stack*.   
10. Wait until *Status* changes to *CREATE_COMPLETE* (roughly 2-4 minutes or if deploying in a secondary region, it can take up to 30 minutes). 

## AHA With AWS Organizations on Member Account using CloudFormation

### Prerequisites

1. [Enable Health Organizational View](https://docs.aws.amazon.com/health/latest/ug/enable-organizational-view-in-health-console.html) from the console, so that you can aggregate all Personal Health Dashboard (PHD) events for all accounts in your AWS Organization. 
2. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)
3. Have access to deploy Cloudformation Templates with the following resources: AWS IAM policies, Amazon DynamoDB Tables, AWS Lambda, Amazon EventBridge and AWS Secrets Manager in the **AWS Organizations Master Account**.
4. If using Multi-Region, you must deploy the following 2 CloudFormation templates to allow the Stackset deployment to deploy resources **even if you have full administrator privileges, you still need to follow these steps**.
 - In CloudFormation Console create a stack with new resources from the following S3 URL: https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetAdministrationRole.yml - this will allows CFT Stacksets to launch AHA in another region
 - Launch the stack.
 - In CloudFormation Console create a stack with new resources from the following S3 URL: https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetExecutionRole.yml) - In *AdministratorAccountId* type in the 12 digit account number you're running the solution in (e.g. 000123456789)
 - Launch the stack.

### Deployment

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
2. In your top-level management account AWS console go to *CloudFormation*
3. In the *CloudFormation* console **click** *Create stack > With new resources (standard)*.
4. Under *Template Source* **click** *Upload a template file* and **click** *Choose file*  and select `CFN_MGMT_ROLE.yml` **Click** *Next*.
 - In *Stack name* type a stack name (i.e. aha-assume-role).
 - In *OrgMemberAccountId* put in the account id of the member account you plan to run AHA in (e.g. 000123456789).
5. Scroll to the bottom and **click** *Next*.
6. Scroll to the bottom and **click** *Next* again.
7. Scroll to the bottom and **click** the *checkbox* and **click** *Create stack*.
8. Wait until *Status* changes to *CREATE_COMPLETE* (roughly 1-2 minutes). This will create an IAM role with the necessary AWS Organizations and AWS Health API permissions for the member account to assume.
9. In the *Outputs* tab, there will be a value for *AWSHealthAwareRoleForPHDEventsArn* (e.g. arn:aws:iam::000123456789:role/aha-org-role-AWSHealthAwareRoleForPHDEvents-ABCSDE12201), copy that down as you will need it for step 16.
10. Back In the root of the package you downloaded/cloned you'll have two files; `handler.py` and `messagegenerator.py`. Use your tool of choice to zip them both up and name them with a unique name (e.g. aha-v1.8.zip). **Note: Putting the version number in the name will make upgrading AHA seamless.**
11. Upload the .zip you created in Step 11 to an S3 in the same region you plan to deploy this in.
12. Login to the member account you plan to deploy this in and in your AWS console go to *CloudFormation*.
13. In the *CloudFormation* console **click** *Create stack > With new resources (standard)*.
14. Under *Template Source* **click** *Upload a template file* and **click** *Choose file*  and select `CFN_DEPLOY_AHA.yml` **Click** *Next*.
 - In *Stack name* type a stack name (i.e. AHA-Deployment).
 - In *AWSOrganizationsEnabled* change the dropdown to `Yes`. If you do NOT have AWS Organizations enabled you should be following the steps for [AHA for users who are NOT using AWS Organizations](#aha-without-aws-organizations-using-cloudformation)
 - In *AWSHealthEventType* select whether you want to receive *all* event types or *only* issues.
 - In *S3Bucket* type ***just*** the bucket name of the S3 bucket used in step 12  (e.g. my-aha-bucket).
 - In *S3Key* type ***just*** the name of the .zip file you created in Step 11 (e.g. aha-v1.8.zip).
 - In the *Communications Channels* section enter the URLs, Emails and/or ARN of the endpoints you configured previously.
 - In the *Email Setup* section enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
 - In *EventSearchBack* enter in the amount of hours you want to search back for events. Default is 1 hour.
 - In *Regions* enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated with (e.g. us-east-1, us-east-2).
 - In *ManagementAccountRoleArn* enter in the full IAM arn from step 10 (e.g. arn:aws:iam::000123456789:role/aha-org-role-AWSHealthAwareRoleForPHDEvents-ABCSDE12201)
 - In *Deploy in secondary region?* select another region to deploy AHA in. Otherwise leave to default No.
15. Scroll to the bottom and **click** *Next*.
16. Scroll to the bottom and **click** *Next* again.
17. Scroll to the bottom and **click** the *checkbox* and **click** *Create stack*.
18. Wait until *Status* changes to *CREATE_COMPLETE* (roughly 2-4 minutes or if deploying in a secondary region, it can take up to 30 minutes).

## Terraform

There are 3 available ways to deploy AHA, all are done via the same Terraform template to make deployment as easy as possible.

**NOTE: ** AHA code is tested with Terraform version v1.0.9, please make sure to have minimum terraform verson of v1.0.9 installed.

The 3 deployment methods for AHA are:

1. [**AHA for users NOT using AWS Organizations using Terraform**](#aha-without-aws-organizations-using-terraform): Users NOT using AWS Organizations.
2. [**AHA for users WITH AWS Organizations using Terraform (Management Account)**](#aha-with-aws-organizations-on-management-account-using-terraform): Users who ARE using AWS Organizations and deploying in the top-level management account.
3. [**AHA for users WITH AWS Organizations using Terraform (Member Account)**](#aha-with-aws-organizations-on-member-account-using-terraform): Users who ARE using AWS Organizations and deploying in a member account in the organization to assume a role in the top-level management account.

## AHA Without AWS Organizations using Terraform

### Prerequisites

1. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)
2. Have access to deploy Terraform Templates with the following resources: AWS IAM policies, Amazon DynamoDB Tables, AWS Lambda, Amazon EventBridge and AWS Secrets Manager.

**NOTE: ** For Multi region deployment, DynamoDB table will be created with PAY_PER_REQUEST billing mode insted of PROVISIONED due to limitation with terraform.

### Deployment - Terraform

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
```
$ git clone https://github.com/aws-samples/aws-health-aware.git
$ cd aws-health-aware/terraform/Terraform_DEPLOY_AHA
```
2. Update parameters file **terraform.tfvars** as below
 - *aha_primary_region* - change to region where you want to deploy AHA solution
 - *aha_secondary_region* - Required if needed to deploy in AHA solution in multiple regions, change to another region (Secondary) where you want to deploy AHA solution, Otherwise leave to default empty value.
 - *AWSOrganizationsEnabled* - Leave it to default which is `No`. If you do have AWS Organizations enabled and you want to aggregate across all your accounts, you should be following the steps for [AHA for users who ARE using AWS Organizations (Management Account)](#aha-with-aws-organizations-on-management-account-using-terraform)] or [AHA for users WITH AWS Organizations (Member Account)](#aha-with-aws-organizations-on-member-account-using-terraform)
 - *AWSHealthEventType* - select whether you want to receive *all* event types or *only* issues.
 - *Communications Channels* section - enter the URLs, Emails and/or ARN of the endpoints you configured previously.
 - *Email Setup* section - enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
 - *EventSearchBack* - enter in the amount of hours you want to search back for events. Default is 1 hour.
 - *Regions* - enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated (e.g. us-east-1, us-east-2).
 - *ManagementAccountRoleArn* - Leave it default empty value
 - *ExcludeAccountIDs* - type ***just*** the name of the .csv file you want to upload if needed to exclude accounts from monitoring, else leave it to empty.
 - *ManagementAccountRoleArn*  - In ARN of the AWS Organizations Management Account assume role leave it set to default None as this is only for customers using AWS Organizations.
3. Deploy the solution using terraform commands below.
```
$ terraform init
$ terraform plan
$ terraform apply
```

## AHA WITH AWS Organizations on Management Account using Terraform

1. [Enable Health Organizational View](https://docs.aws.amazon.com/health/latest/ug/enable-organizational-view-in-health-console.html) from the console, so that you can aggregate all Personal Health Dashboard (PHD) events for all accounts in your AWS Organization. 
2. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)

**NOTE: ** For Multi region deployment, DynamoDB table will be created with PAY_PER_REQUEST billing mode insted of PROVISIONED due to limitation with terraform.

### Deployment - Terraform

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
```
$ git clone https://github.com/aws-samples/aws-health-aware.git
$ cd aws-health-aware/terraform/Terraform_DEPLOY_AHA
```
5. Update parameters file **terraform.tfvars** as below
 - *aha_primary_region* - change to region where you want to deploy AHA solution
 - *aha_secondary_region* - Required if needed to deploy in AHA solution in multiple regions, change to another region (Secondary) where you want to deploy AHA solution, Otherwise leave to default empty value.
 - *AWSOrganizationsEnabled* - change the value to `Yes`. If you do NOT have AWS Organizations enabled you should be following the steps for [AHA for users who are NOT using AWS Organizations](#aha-without-aws-organizations-using-terraform)
 - *AWSHealthEventType* - select whether you want to receive *all* event types or *only* issues.
 - *Communications Channels* section - enter the URLs, Emails and/or ARN of the endpoints you configured previously.
 - *Email Setup* section - enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
 - *EventSearchBack* - enter in the amount of hours you want to search back for events. Default is 1 hour.
 - *Regions* enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated (e.g. us-east-1, us-east-2).
 - *ManagementAccountRoleArn* - Leave it default empty value
 - *S3Bucket* - type ***just*** the name of the S3 bucket where exclude file .csv you upload. leave it empty if exclude Account feature is not used. 
 - *ExcludeAccountIDs* - type ***just*** the name of the .csv file you want to upload if needed to exclude accounts from monitoring, else leave it to empty.
 - *ManagementAccountRoleArn* - In ARN of the AWS Organizations Management Account assume role leave it set to default None, unless you are using a member account instead of the management account. Instructions for this configuration are in the next section.
3. Deploy the solution using terraform commands below.
```
$ terraform init
$ terraform plan
$ terraform apply
```

## AHA WITH AWS Organizations on Member Account using Terraform

1. [Enable Health Organizational View](https://docs.aws.amazon.com/health/latest/ug/enable-organizational-view-in-health-console.html) from the console, so that you can aggregate all Personal Health Dashboard (PHD) events for all accounts in your AWS Organization.
2. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)

**NOTE: ** For Multi region deployment, DynamoDB table will be created with PAY_PER_REQUEST billing mode insted of PROVISIONED due to limitation with terraform.

### Deployment - Terraform

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
```
$ git clone https://github.com/aws-samples/aws-health-aware.git
```
2. In your top-level management account deploy terraform module Terraform_MGMT_ROLE.tf to create Cross-Account Role for PHD access
```
$ cd aws-health-aware/terraform/Terraform_MGMT_ROLE
$ terraform init
$ terraform plan
$ terraform apply
 Input *OrgMemberAccountId*  Enter the account id of the member account you plan to run AHA in (e.g. 000123456789).
```
3. Wait for deployment to complete. This will create an IAM role with the necessary AWS Organizations and AWS Health API permissions for the member account to assume. and note the **AWSHealthAwareRoleForPHDEventsArn** role name, this will be used during deploying solution in member account
4. In the *Outputs* section, there will be a value for *AWSHealthAwareRoleForPHDEventsArn* (e.g. arn:aws:iam::000123456789:role/aha-org-role-AWSHealthAwareRoleForPHDEvents-ABCSDE12201), copy that down as you will need to update params file (variable ManagementAccountRoleArn).
4. Change directory to **terraform/Terraform_DEPLOY_AHA** to deploy the solution
5. Update parameters file **terraform.tfvars** as below
 - *aha_primary_region* - change to region where you want to deploy AHA solution
 - *aha_secondary_region* - Required if needed to deploy in AHA solution in multiple regions, change to another region (Secondary) where you want to deploy AHA solution, Otherwise leave to default empty value.
 - *AWSOrganizationsEnabled* - change the value to `Yes`. If you do NOT have AWS Organizations enabled you should be following the steps for [AHA for users who are NOT using AWS Organizations](#aha-without-aws-organizations-using-terraform)
 - *AWSHealthEventType* - select whether you want to receive *all* event types or *only* issues.
 - *Communications Channels* section - enter the URLs, Emails and/or ARN of the endpoints you configured previously.
 - *Email Setup* section - enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
 - *EventSearchBack* - enter in the amount of hours you want to search back for events. Default is 1 hour.
 - *Regions* enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated (e.g. us-east-1, us-east-2).
 - *ManagementAccountRoleArn* -  Enter in the full IAM arn from step 10 (e.g. arn:aws:iam::000123456789:role/aha-org-role-AWSHealthAwareRoleForPHDEvents-ABCSDE12201)
 - *S3Bucket* - type ***just*** the name of the S3 bucket where exclude file .csv you upload. leave it empty if exclude Account feature is not used. 
 - *ExcludeAccountIDs* - type ***just*** the name of the .csv file you want to upload if needed to exclude accounts from monitoring, else leave it to empty.
4. Deploy the solution using terraform commands below.
```
$ terraform init
$ terraform plan
$ terraform apply
```

# Updating using CloudFormation
**Until this project is migrated to the AWS Serverless Application Model (SAM), updates will have to be done as described below:**
1. Download the updated CloudFormation Template .yml file and 2 `.py` files.   
2. Zip up the 2 `.py` files and name the .zip with a different version number than before (e.g. if the .zip you originally uploaded is aha-v1.8.zip the new one should be aha-v1.9.zip)   
3. In the AWS CloudFormation console **click** on the name of your stack, then **click** *Update*.   
4. In the *Prepare template* section **click** *Replace current template*, **click** *Upload a template file*, **click** *Choose file*, select the newer `CFN_DEPLOY_AHA.yml` file you downloaded and finally **click** *Next*.   
5. In the *S3Key* text box change the version number in the name of the .zip to match name of the .zip you uploaded in Step 2 (The name of the .zip has to be different for CloudFormation to recognize a change). **Click** *Next*.   
6. At the next screen **click** *Next* and finally **click** *Update stack*. This will now upgrade your environment to the latest version you downloaded.

**If for some reason, you still have issues after updating, you can easily just delete the stack and redeploy. The infrastructure can be destroyed and rebuilt within minutes through CloudFormation.**

# Updating using Terraform
**Until this project is migrated to the AWS Serverless Application Model (SAM), updates will have to be done as described below:**
1. Pull the latest code from git repository for AHA.
2. Update the parameters file terraform.tfvars per your requirement
3. Copy the terraform template files to directory where your previous state exists
4. Deploy the templates as below
```
$ cd aws-health-aware
$ git pull https://github.com/aws-samples/aws-health-aware.git
$ cd terraform/Terraform_DEPLOY_AHA
$ terraform init
$ terraform plan - This command should show any difference existing config and latest code.
$ terraform apply
```

**If for some reason, you still have issues after updating, you can easily just delete the stack and redeploy. The infrastructure can be destroyed and rebuilt within minutes through Terraform.**

# New Features
We are happy to announce the launch of new enhancements to AHA. Please try them out and keep sendings us your feedback!
1. Multi-region deployment option
2. Updated file names for improved clarity
2. Ability to filter accounts (Refer to AccountIDs CFN parameter for more info on how to exclude accounts from AHA notifications)
3. Ability to view Account Names for a given Account ID in the PHD alerts
4. If you are running AHA with the Non-Org mode, AHA will send the Account #' and resource(s) impacts if applicable for a given alert
5. Ability to deploy AHA with the Org mode on a member account
6. Support for a new Health Event Type - "Investigation"
7. Terraform support to deploy the solution

# Troubleshooting
* If for whatever reason you need to update the Webhook URL; just update the CloudFormation or terraform Template with the new Webhook URL.
* If you are expecting an event and it did not show up it may be an oddly formed event. Take a look at *CloudWatch > Log groups* and search for the name of your Lambda function.  See what the error is and reach out to us [email](mailto:aha-builders@amazon.com) for help.
* If for any errors related to duplicate secrets during deployment, try deleting manually and redeploy the solution. Example command to delete SlackChannelID secret in us-east-1 region.
```
$ aws secretsmanager delete-secret --secret-id SlackChannelID --force-delete-without-recovery --region us-east-1
```
