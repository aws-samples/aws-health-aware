
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
- [Setup](#setup) 
  * [AHA for users WITHOUT AWS Organizations](#aha-without-aws-organizations)
  * [AHA for users WITH AWS Organizations](#aha-with-aws-organizations)    
- [Updating](#updating)
- [Troubleshooting](#troubleshooting)

# Introduction
AWS Health Aware (AHA) is an automated notification tool for sending well-formatted AWS Health Alerts to Amazon Chime, Slack, Microsoft Teams, E-mail or an AWS Eventbridge compatible endpoint as long as you have Business or Enterprise Support.

![](https://github.com/aws-samples/aws-health-aware/blob/main/readme-images/aha-logo.png?raw=1)

# Architecture
![](https://github.com/aws-samples/aws-health-aware/blob/main/readme-images/architecture.png?raw=1)

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

# Configuring an Endpoint - 
AHA can send to multiple endpoints (webhook URLs, Email or EventBridge). To use any of these you'll need to set it up before-hand as some of these are done on 3rd party websites. We'll go over some of the common ones here.

## Creating a Amazon Chime Webhook URL - 
**You will need to have access to create a Amazon Chime room and manage webhooks.**

1. Create a new [chat room](https://docs.aws.amazon.com/chime/latest/ug/chime-chat-room.html) for events (i.e. aws_events).   
2. In the chat room created in step 1, **click** on the gear icon and **click** *manage webhooks and bots*.   
3. **Click** *Add webhook*.   
4. **Type** a name for the bot (e.g. AWS Health Bot) and **click** *Create*.   
5. **Click** *Copy URL*, we will need it for the deployment.

## Creating a Slack Webhook URL - 
**You will need to have access to add a new channel and app to your Slack Workspace**.

1. Create a new [channel](https://slack.com/help/articles/201402297-Create-a-channel) for events (i.e. aws_events)
2. In your browser go to: workspace-name.slack.com/apps where workspace-name is the name of your Slack Workspace.   
3. In the search bar, search for: *Incoming Webhooks* and **click** on it.   
4. **Click** on *Add to Slack*.   
5. From the dropdown **click** on the channel your created in step 1 and **click** *Add Incoming Webhooks integration*.   
6. From this page you can change the name of the webhook (i.e. AWS Bot), the icon/emoji to use, etc.   
7. For the deployment we will need the *Webhook URL*.

## Creating a Microsoft Teams Webhook URL - 
**You will need to have access to add a new channel and app to your Microsoft Teams channel**.

1. Create a new [channel](https://docs.microsoft.com/en-us/microsoftteams/get-started-with-teams-create-your-first-teams-and-channels) for events (i.e. aws_events)
2. Within your Microsoft Team go to *Apps*
3. In the search bar, search for: *Incoming Webhook* and **click** on it.   
4. **Click** on *Add to team*.   
5. **Type** in the name of your on the channel your created in step 1 and **click** *Set up a connector*.   
6. From this page you can change the name of the webhook (i.e. AWS Bot), the icon/emoji to use, etc. **Click** *Create* when done.  
7. For the deployment we will need the webhook *URL* that is presented.

## Configuring an Email - 

1. You'll be able to send email alerts to one or many addresses. However, you must first [verify](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses-procedure.html) the email(s) in the Simple Email Service (SES) console.
2. AHA utilizes Amazon SES so all you need is to enter in a To: address and a From: address.
3. You *may* have to allow a rule in your environment so that the emails don't get labeled as SPAM. This will be something you have to congfigure on your own.

## Creating a Amazon EventBridge Ingestion ARN - 

1.	In the AWS Console, search for **Amazon EventBridge**.
2.	On the left hand side, **click** *Event buses*.
3.	Under *Custom event* bus **click** *Create event bus*
4.	Give your Event bus a name and **click** *Create*.
5.  For the deployment we will need the *Name* of the Event bus **(not the ARN)**.

# Setup - 
There are 2 available ways to deploy AHA, both are done via the same CloudFormation template to make deployment as easy as possible.

The 2 deployment methods for AHA are:

1. [**AHA for users NOT using AWS Organizations**](#aha-without-aws-organizations): Users NOT using AWS Organizations will be able to get Service Health Dashboard (SHD) events ONLY.
2. [**AHA for users who ARE using AWS Organizations**](#aha-with-aws-organizations): Users who ARE using AWS Organizations will be able to get Service Health Dashboard (SHD) events as well as aggregated Personal Health Dashboard (PHD) events for all accounts in their AWS Organization.

## AHA Without AWS Organizations

### Prerequisites

1. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)
2. Have access to deploy Cloudformation Templates with the following resources: AWS IAM policies, Amazon DynamoDB Tables, AWS Lambda, Amazon EventBridge and AWS Secrets Manager.

### Deployment

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
2. In the root of this package you'll have two files; `handler.py` and `messagegenerator.py`. Use your tool of choice to zip them both up and name them with a unique name (e.g. aha-v1.8.zip). **Note: Putting the version number in the name will make upgrading AHA seamless.**
3. Upload the .zip you created in Step 1 to an S3 in the same region you plan to deploy this in.   
4. In your AWS console go to *CloudFormation*.   
5. In the *CloudFormation* console **click** *Create stack > With new resources (standard)*.   
6. Under *Template Source* **click** *Upload a template file* and **click** *Choose file*  and select `CFN_AHA.yml` **Click** *Next*.   
7. -In *Stack name* type a stack name (i.e. AHA-Deployment).   
-In *AWSOrganizationsEnabled* leave it set to default which is `No`. If you do have AWS Organizations enabled and you want to aggregate across all your accounts, you should be following the step for [AHA for users who ARE using AWS Organizations](#aha-with-aws-organizations)  
-In *AWSHealthEventType* select whether you want to receive *all* event types or *only* issues.   
-In *S3Bucket* type ***just*** the bucket name of the S3 bucket used in step 3  (e.g. my-aha-bucket).    
-In *S3Key* type ***just*** the name of the .zip file you created in Step 2 (e.g. aha-v1.8.zip).     
-In the *Communications Channels* section enter the URLs, Emails and/or ARN of the endpoints you configured previously.  
-In the *Email Setup* section enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
-In *EventSearchBack* enter in the amount of hours you want to search back for events. Default is 1 hour.  
-In *Regions* enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated (e.g. us-east-1, us-east-2).
8. Scroll to the bottom and **click** *Next*. 
9. Scroll to the bottom and **click** *Next* again.   
10. Scroll to the bottom and **click** the *checkbox* and **click** *Create stack*.   
11. Wait until *Status* changes to *CREATE_COMPLETE* (roughly 2-4 minutes).   

## AHA With AWS Organizations


### Prerequisites

1. [Enable Health Organizational View](https://docs.aws.amazon.com/health/latest/ug/enable-organizational-view-in-health-console.html) from the console, so that you can aggregate all Personal Health Dashboard (PHD) events for all accounts in your AWS Organization. 
2. Have at least 1 [endpoint](#configuring-an-endpoint) configured (you can have multiple)
3. Have access to deploy Cloudformation Templates with the following resources: AWS IAM policies, Amazon DynamoDB Tables, AWS Lambda, Amazon EventBridge and AWS Secrets Manager in the **AWS Organizations Master Account**.

### Deployment

1. Clone the AHA package that from this repository. If you're not familiar with the process, [here](https://git-scm.com/docs/git-clone) is some documentation. The URL to clone is in the upper right-hand corner labeled `Clone uri`
2. In the root of this package you'll have two files; `handler.py` and `messagegenerator.py`. Use your tool of choice to zip them both up and name them with a unique name (e.g. aha-v1.8.zip). **Note: Putting the version number in the name will make upgrading AHA seamless.**
3. Upload the .zip you created in Step 1 to an S3 in the same region you plan to deploy this in.   
4. In your AWS console go to *CloudFormation*.   
5. In the *CloudFormation* console **click** *Create stack > With new resources (standard)*.   
6. Under *Template Source* **click** *Upload a template file* and **click** *Choose file*  and select `CFN_AHA.yml` **Click** *Next*.   
7. -In *Stack name* type a stack name (i.e. AHA-Deployment).
-In *AWSOrganizationsEnabled* change the dropdown to `Yes`. If you do NOT have AWS Organizations enabled you should be following the steps for [AHA for users who are NOT using AWS Organizations](#aha-without-aws-organizations)  
-In *AWSHealthEventType* select whether you want to receive *all* event types or *only* issues.   
-In *S3Bucket* type ***just*** the bucket name of the S3 bucket used in step 3  (e.g. my-aha-bucket).    
-In *S3Key* type ***just*** the name of the .zip file you created in Step 2 (e.g. aha-v1.8.zip).     
-In the *Communications Channels* section enter the URLs, Emails and/or ARN of the endpoints you configured previously.  
-In the *Email Setup* section enter the From and To Email addresses as well as the Email subject. If you aren't configuring email, just leave it as is.
-In *EventSearchBack* enter in the amount of hours you want to search back for events. Default is 1 hour.  
-In *Regions* enter in the regions you want to search for events in. Default is all regions. You can filter for up to 10, comma separated with (e.g. us-east-1, us-east-2).
8. Scroll to the bottom and **click** *Next*. 
9. Scroll to the bottom and **click** *Next* again.   
10. Scroll to the bottom and **click** the *checkbox* and **click** *Create stack*.   
11. Wait until *Status* changes to *CREATE_COMPLETE* (roughly 2-4 minutes). 

# Updating
**Until this project is migrated to the AWS Serverless Application Model (SAM), updates will have to be done as described below:**
1. Download the updated CloudFormation Template .yml file and 2 `.py` files.   
2. Zip up the 2 `.py` files and name the .zip with a different version number than before (e.g. if the .zip you originally uploaded is aha-v1.8.zip the new one should be aha-v1.9.zip)   
3. In the AWS CloudFormation console **click** on the name of your stack, then **click** *Update*.   
4. In the *Prepare template* section **click** *Replace current template*, **click** *Upload a template file*, **click** *Choose file*, select the newer `CFN_AHA.yml` file you downloaded and finally **click** *Next*.   
5. In the *S3Key* text box change the version number in the name of the .zip to match name of the .zip you uploaded in Step 2 (The name of the .zip has to be different for CloudFormation to recognize a change). **Click** *Next*.   
6. At the next screen **click** *Next* and finally **click** *Update stack*. This will now upgrade your environment to the latest version you downloaded.

**If for some reason, you still have issues after updating, you can easily just delete the stack and redeploy. The infrastructure can be destroyed and rebuilt within minutes through CloudFormation.**

# Troubleshooting
* If for whatever reason you need to update the Webhook URL; just update the CloudFormation Template with the new Webhook URL.
* If you are expecting an event and it did not show up it may be an oddly formed event. Take a look at *CloudWatch > Log groups* and search for the name of your Cloudformation stack and Lambda function.  See what the error is and reach out to us [email](mailto:aha-builders@amazon.com) for help.
