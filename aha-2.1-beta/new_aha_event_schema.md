# Readme for new AHA Event schema

## New AHA Event Schema

With release X.Y.Z, AHA includes an updated format for events published to EventBridge. Building on the [existing event format](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html#health-event-types) published by AWS Health, AHA enriches it with additional data from the Health API and AWS Organizations to enable new options for filtering in EventBridge. 


>Note: If you used the previous { "title": "Title", "value": "Value" } schema in your rules, you must update your rules to reflect the new schema when deploying the new version of AHA

### Schema:

```
{
    "version": "0",
    "id": "7bf73129-1428-4cd3-a780-95db273d1602",
    "detail-type": "AHA Event",
    "source": "aha",
    "account": "123456789012",
    "time": "2022-07-14T03:56:10Z",
    "region": "region of the eventbus",
    "resources": [
        "i-1234567890abcdef0"
    ],
    "detail": {
        "eventArn": "arn:aws:health:region::event/id",
        "service": "service",
        "eventTypeCode": "typecode",
        "eventTypeCategory": "category",
        "region": "region of the Health event",
        "startTime": "2022-07-02 12:33:26.951000+00:00",
        "endTime": "2022-07-02 12:33:26.951000+00:00",
        "lastUpdatedTime": "2022-07-02 12:36:18.576000+00:00",
        "statusCode": "status",
        "eventScopeCode": "scopecode",
        "eventDescription": {
            "latestDescription": "description"
        },
        "affectedEntities": [{
            "entityValue": "i-1234567890abcdef0",
            "awsAccountId": "account number",
            "awsAccountName": "account name"
        }]
    }
}
```

### AHA added properties 

**eventScopeCode:** Specifies if the Health event is a public AWS service event or an account-specific event. 
Values: *string -* `PUBLIC | ACCOUNT_SPECIFIC`

**statusCode:** Reflects whether the event is ongoing, resolved or in the case of scheduled maintenance, upcoming. 
Values: *string -* `open | closed | upcoming`

**affectedEntities:** For ACCOUNT_SPECIFIC events, AHA includes expanded detail on resources. **affectedEntities** includes the listed **resources**, each as an **entitityValue** with the resource ID (as it appears in events for single accounts). AHA adds the related **awsAccountId** and In AWS Organizations, **awsAccountName** of the resource. 
Values: *entity object(s). May be empty if no resources are listed*


## EventBridge pattern examples 

As a primer we recommended you review the [EventBridge EventPatterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html) documentation and examples on [Content filtering in Amazon EventBridge event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns-content-based-filtering.html)

Use the following sample event published by AWS Health Aware to test matching in the provided examples: 

```
{
    "version": "0",
    "id": "e47c4390-b295-ce6f-7e94-f13083d7bb90",
    "detail-type": "AHA Event",
    "source": "aha",
    "account": "`234567890123`",
    "time": "2022-07-20T18:26:17Z",
    "region": "us-east-1",
    "resources": [
        "vpn-0d0e3eeefe6aabb0d"
    ],
    "detail": {
        "arn": "arn:aws:health:us-east-1::event/VPN/AWS_VPN_REDUNDANCY_LOSS/AWS_VPN_REDUNDANCY_LOSS-1656151378267-7672191-IAD",
        "service": "VPN",
        "eventTypeCode": "AWS_VPN_REDUNDANCY_LOSS",
        "eventTypeCategory": "accountNotification",
        "region": "us-east-1",
        "startTime": "2022-06-25 10:00:48.868000+00:00",
        "lastUpdatedTime": "2022-06-25 10:02:58.371000+00:00",
        "statusCode": "open",
        "eventScopeCode": "ACCOUNT_SPECIFIC",
        "eventDescription": {
            "latestDescription": "Your VPN Connection associated with this event in the us-east-1 Region had a momentary lapse of redundancy as one of two tunnel endpoints was replaced. Connectivity on the second tunnel was not affected during this time. Both tunnels are now operating normally.\n\nReplacements can occur for several reasons, including health, software upgrades, customer-initiated modifications, and when underlying hardware is retired. If you have configured your VPN Customer Gateway to use both tunnels, then your VPN Connection will have utilized the alternate tunnel during the replacement process. For more on tunnel endpoint replacements, please see our documentation [1].\n\nIf you have not configured your VPN Customer Gateway to use both tunnels, then your VPN Connection may have been interrupted during the replacement. We encourage you to configure your router to use both tunnels. You can obtain the VPN Connection configuration recommendations for several types of VPN devices from the AWS Management Console [2]. On the \"Amazon VPC\" tab, select \"VPN Connections\". Then highlight the VPN Connection and choose \"Download Configuration\".\n\n[1] https://docs.aws.amazon.com/vpn/latest/s2svpn/monitoring-vpn-health-events.html\n[2] https://console.aws.amazon.com"
        },
        "affectedEntities": [{
            "entityValue": "vpn-0d0e3eeefe6aabb0d",
            "awsAccountId": "987654321987",
            "awsAccountName": "Prod-Apps"
        }]
    }
}
```


To write a rule that matches resources found in the event, reference the **resources** key of the JSON event, and provide an event pattern to the EventBridge rule.  Example 1 matches on an exact resource - “*vpn-0d0e3eeefe6aabb0d*”.  Example 2 matches any resource starting with "*vpn-*"  
**Example 1:**

```
{
  "resources": [
    "vpn-0d0e3eeefe6aabb0d"
  ]
}
```


**Example 2:** 

```
{
  "resources": [
    {"prefix": "vpn-"}
  ]
}
```


To match based on a specific service, note that **service** is nested within the **detail** key in the JSON structure, so we reference both **detail** and **service**.   Example 3 matches the VPN service, and Example 4 matches EC2 OR S3 (will not match the sample event).   To get a list of all service names used by AWS Health you can use the cli command - `aws health describe-event-types` 

**Example 3:** 

```
{
  "detail": {
    "service": ["VPN"]
  }
}
```


**Example 4:** 

```
{
  "detail": {
    "service": ["EC2", "S3"]
  }
}
```


To match events based on an AWS account name or number, use the following patterns.  Take note of the additional levels of nesting based on the sample event.   Example 5 matches a specific account number as **awsAccountId**.  Example 6 matches a specific account name, and Example 7 adds an additional field of **eventTypeCategory** along with the “prefix” filter pattern which will match any value in the **awsAccountName** field that starts with “*Prod*”  similar to a wildcard match of “*Prod**”

**Example 5:**

```
{ 
  "detail": {
    "affectedEntities": {
      "awsAccountId": ["987654321987"]
    }
  }
}
```


**Example 6:**

```
{ 
  "detail": {
    "affectedEntities": {
      "awsAccountName": ["Prod-Apps"]
    }
  }
}
```


**Example 7:**

```
{ 
  "detail": {
    "eventTypeCategory": ["accountNotification"],
    "affectedEntities": {
      "awsAccountName": [{"prefix": "Prod"}]
    }
  }
}
```


Combine any of the patterns listed to create more specific rules. Note that all patterns in the rule must match for the EventBridge rule to trigger.  Example 8 will only match when all 3 conditions exist in an AHA event -  **service** = *VPN*, **region** = *us-east-1* and **awsAccountId** = *987654321098*

**Example 8:**

```
{
  "detail": {
    "service": ["VPN"],
    "region": ["us-east-1"],
    "affectedEntities": {
      "awsAccountId": ["987654321987"]
    }
  }
}
```


As a best practice, also include `"source": ["aha"]` in your pattern if the event bus contains events generated by other sources.

**Example 9:**

```
{
  "source": ["aha"],
  "detail": {
    "service": ["VPN"],
    "region": ["us-east-1"],
    "affectedEntities": {
      "awsAccountId": ["987654321987"]
    }
  }
}
```
