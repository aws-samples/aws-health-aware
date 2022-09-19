import json
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import os
import time


def get_message_for_feishu(event_details, event_type, affected_accounts, affected_entities):
    message = ""
    summary = ""

        
    if len(affected_entities) >= 1:
        affected_entities = "\n".join(affected_entities)
        if affected_entities == "UNKNOWN":
            affected_entities = "All resources\nin region"
    else:
        affected_entities = "All resources\nin region"
    if len(affected_accounts) >= 1:
        affected_accounts = "\n".join(affected_accounts)
    else:
        affected_accounts = "All accounts\nin region"      
    if event_type == "create":
        summary += (
            f"[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
            f"the {event_details['successfulSet'][0]['event']['region'].upper()} region."
        )
        # message1 = {
        #     "zh_cn": {
        #         "title": summary,
        #         "content": [
        #             [{"tag":"text","text": "Account(s): {}".format(affected_accounts)}],
        #             [{"tag":"text","text": "Resource(s): {}".format(affected_entities)}],
        #             [{"tag":"text","text": "Service: {}".format(event_details['successfulSet'][0]['event']['service'])}],
        #             [{"tag":"text","text": "Region: {}".format(event_details['successfulSet'][0]['event']['region'])}],
        #             [{"tag":"text","text": "Start Time (UTC): {}".format(cleanup_time(event_details['successfulSet'][0]['event']['startTime']))}],
        #             [{"tag":"text","text": "Status: {}".format(event_details['successfulSet'][0]['event']['statusCode'])}],
        #             [{"tag":"text","text": "Event ARN: {}".format(event_details['successfulSet'][0]['event']['arn'])}],
        #             [{"tag":"text","text": "Updates: {}".format(get_last_aws_update(event_details))}],
        #         ]
        #     }
        # }
        message = f"""
        {{
            "config": {{
                "wide_screen_mode": true
            }},
            "header": {{
                "template": "red",
                "title": {{
                "content": "{summary}",
                "tag": "plain_text"
                }}
            }},
            "elements": [
                {{
                "fields": [
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Account(s): **{affected_accounts}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Region: **{event_details['successfulSet'][0]['event']['region']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Service: **{event_details['successfulSet'][0]['event']['service']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Status: **{event_details['successfulSet'][0]['event']['statusCode']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Start Time (UTC): **{cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Resource(s): **{affected_entities}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Event ARN: **{event_details['successfulSet'][0]['event']['arn']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Updates: **{get_last_aws_update(event_details)}",
                        "tag": "lark_md"
                    }}
                    }}
                ],
                "tag": "div"
                }},
                {{
                "tag": "hr"
                }}
            ]
        }}"""

    elif event_type == "resolve":
        summary += (
            f"[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
            f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved."
        )
    
        message = f"""
        {{
            "config": {{
                "wide_screen_mode": true
            }},
            "header": {{
                "template": "bule",
                "title": {{
                "content": "{summary}",
                "tag": "plain_text"
                }}
            }},
            "elements": [
                {{
                "fields": [
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Account(s): **{affected_accounts}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Region: **{event_details['successfulSet'][0]['event']['region']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Service: **{event_details['successfulSet'][0]['event']['service']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Status: **{event_details['successfulSet'][0]['event']['statusCode']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Start Time (UTC): **{cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Resource(s): **{affected_entities}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Event ARN: **{event_details['successfulSet'][0]['event']['arn']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Updates: **{get_last_aws_update(event_details)}",
                        "tag": "lark_md"
                    }}
                    }}
                ],
                "tag": "div"
                }},
                {{
                "tag": "hr"
                }}
            ]
        }}"""

    message = json.loads(message,strict=False)
    print("Message sent to feishu: ", message)
    return message


def get_org_message_for_feishu(event_details, event_type, affected_org_accounts, affected_org_entities):
    message = ""
    summary = ""
        
    if len(affected_org_entities) >= 1:
        affected_org_entities = "\n".join(affected_org_entities)
    else:
        affected_org_entities = "All resources\nin region"
    if len(affected_org_accounts) >= 1:
        affected_org_accounts = "\n".join(affected_org_accounts)
    else:
        affected_org_accounts = "All accounts\nin region"        
    if event_type == "create":
        summary += (
            f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
            f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
        )
        message = f"""
        {{
            "config": {{
                "wide_screen_mode": true
            }},
            "header": {{
                "template": "red",
                "title": {{
                "content": "{summary}",
                "tag": "plain_text"
                }}
            }},
            "elements": [
                {{
                "fields": [
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Account(s): **{affected_org_accounts}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Region: **{event_details['successfulSet'][0]['event']['region']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Service: **{event_details['successfulSet'][0]['event']['service']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Status: **{event_details['successfulSet'][0]['event']['statusCode']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Start Time (UTC): **{cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Resource(s): **{affected_org_entities}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Event ARN: **{event_details['successfulSet'][0]['event']['arn']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Updates: **{get_last_aws_update(event_details)}",
                        "tag": "lark_md"
                    }}
                    }}
                ],
                "tag": "div"
                }},
                {{
                "tag": "hr"
                }}
            ]
        }}"""

    elif event_type == "resolve":
        summary += (
            f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
            f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
        )
        message = f"""
        {{
            "config": {{
                "wide_screen_mode": true
            }},
            "header": {{
                "template": "bule",
                "title": {{
                "content": "{summary}",
                "tag": "plain_text"
                }}
            }},
            "elements": [
                {{
                "fields": [
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Account(s): **{affected_org_accounts}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Region: **{event_details['successfulSet'][0]['event']['region']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Service: **{event_details['successfulSet'][0]['event']['service']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Status: **{event_details['successfulSet'][0]['event']['statusCode']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Start Time (UTC): **{cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Resource(s): **{affected_org_entities}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Event ARN: **{event_details['successfulSet'][0]['event']['arn']}",
                        "tag": "lark_md"
                    }}
                    }},
                    {{
                    "is_short": false,
                    "text": {{
                        "content": "**Updates: **{get_last_aws_update(event_details)}",
                        "tag": "lark_md"
                    }}
                    }}
                ],
                "tag": "div"
                }},
                {{
                "tag": "hr"
                }}
            ]
        }}"""

    message = json.loads(message,strict=False)
    print("Message sent to feishu: ", message)
    return message


def get_message_for_slack(event_details, event_type, affected_accounts, affected_entities, slack_webhook):
    message = ""
    summary = ""
    if slack_webhook == "webhook":
        if len(affected_entities) >= 1:
            affected_entities = "\n".join(affected_entities)
            if affected_entities == "UNKNOWN":
                affected_entities = "All resources\nin region"
        else:
            affected_entities = "All resources\nin region"
        if len(affected_accounts) >= 1:
            affected_accounts = "\n".join(affected_accounts)
        else:
            affected_accounts = "All accounts\nin region"      
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "danger",
                            "fields": [
                                { "title": "Account(s)", "value": affected_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                          
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "00ff00",
                            "fields": [
                                { "title": "Account(s)", "value": affected_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                                
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }
    else:
        if len(affected_entities) >= 1:
            affected_entities = "\n".join(affected_entities)
            if affected_entities == "UNKNOWN":
                affected_entities = "All resources\nin region"
        else:
            affected_entities = "All resources in region"
        if len(affected_accounts) >= 1:
            affected_accounts = "\n".join(affected_accounts)
        else:
            affected_accounts = "All accounts in region"      
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
               "text": summary,
                "accounts": affected_accounts,
                "resources": affected_entities,
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "accounts": affected_accounts,
                "resources": affected_entities,                
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            }
    
    print("Message sent to Slack: ", message)
    return message

def get_message_for_eventbridge(event_details, event_type, affected_accounts, affected_entities):
    message = ""
    if len(affected_entities) >= 1:
        affected_entities = "\n".join(affected_entities)
        if affected_entities == "UNKNOWN":
            affected_entities = "All resources\nin region"
    else:
        affected_entities = "All resources\nin region"
    if len(affected_accounts) >= 1:
        affected_accounts = "\n".join(affected_accounts)
    else:
        affected_accounts = "All accounts\nin region"       
    if event_type == "create":
        message = {
            "attachments": [
                {
                        "fields": [
                            { "title": "Account(s)", "value": affected_accounts, "short": True },
                            { "title": "Resource(s)", "value": affected_entities, "short": True },
                            { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                            { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                            { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                            { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                            { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },
                            { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                        ],
                }
            ]
        }

    elif event_type == "resolve":
        message = {
            "attachments": [
                {
                        "fields": [
                            { "title": "Account(s)", "value": affected_accounts, "short": True },
                            { "title": "Resource(s)", "value": affected_entities, "short": True },
                            { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                            { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                            { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                            { "title": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime']), "short": True },
                            { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                            { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },
                            { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                        ],
                }
            ]
        }
    print("SHD Message generated for EventBridge : ", message)
    return message

def get_org_message_for_eventbridge(event_details, event_type, affected_org_accounts, affected_org_entities):
    message = ""
    if len(affected_org_entities) >= 1:
        affected_org_entities = "\n".join(affected_org_entities)
    else:
        affected_org_entities = "All resources\nin region"
    if len(affected_org_accounts) >= 1:
        affected_org_accounts = "\n".join(affected_org_accounts)
    else:
        affected_org_accounts = "All accounts\nin region"
    if event_type == "create":
        message = {
            "attachments": [
                {
                        "fields": [
                            { "title": "Account(s)", "value": affected_org_accounts, "short": True },
                            { "title": "Resource(s)", "value": affected_org_entities, "short": True },
                            { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                            { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                            { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                            { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                            { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },
                            { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                        ],
                }
            ]
        }

    elif event_type == "resolve":
        message = {
            "attachments": [
                {
                        "fields": [
                            { "title": "Account(s)", "value": affected_org_accounts, "short": True },
                            { "title": "Resource(s)", "value": affected_org_entities, "short": True },
                            { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                            { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                            { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                            { "title": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime']), "short": True },
                            { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                            { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },
                            { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                        ],
                }
            ]
        }
    json.dumps(message)
    print("PHD/SHD Message generated for Event Bridge: ", message)
    return message


def get_org_message_for_slack(event_details, event_type, affected_org_accounts, affected_org_entities, slack_webhook):
    message = ""
    summary = ""
    if slack_webhook == "webhook":
        if len(affected_org_entities) >= 1:
            affected_org_entities = "\n".join(affected_org_entities)
        else:
            affected_org_entities = "All resources\nin region"
        if len(affected_org_accounts) >= 1:
            affected_org_accounts = "\n".join(affected_org_accounts)
        else:
            affected_org_accounts = "All accounts\nin region"        
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "danger",
                            "fields": [
                                { "title": "Account(s)", "value": affected_org_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_org_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                                  
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "attachments": [
                    {
                        "color": "00ff00",
                            "fields": [
                                { "title": "Account(s)", "value": affected_org_accounts, "short": True },
                                { "title": "Resource(s)", "value": affected_org_entities, "short": True },
                                { "title": "Service", "value": event_details['successfulSet'][0]['event']['service'], "short": True },
                                { "title": "Region", "value": event_details['successfulSet'][0]['event']['region'], "short": True },
                                { "title": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime']), "short": True },
                                { "title": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime']), "short": True },
                                { "title": "Status", "value": event_details['successfulSet'][0]['event']['statusCode'], "short": True },
                                { "title": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn'], "short": False },                                
                                { "title": "Updates", "value": get_last_aws_update(event_details), "short": False }
                            ],
                    }
                ]
            }
    else:
        if len(affected_org_entities) >= 1:
            affected_org_entities = "\n".join(affected_org_entities)
        else:
            affected_org_entities = "All resources in region"
        if len(affected_org_accounts) >= 1:
            affected_org_accounts = "\n".join(affected_org_accounts)
        else:
            affected_org_accounts = "All accounts in region"        
        if event_type == "create":
            summary += (
                f":rotating_light:*[NEW] AWS Health reported an issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region.*"
            )
            message = {
               "text": summary,
                "accounts": affected_org_accounts,
                "resources": affected_org_entities,
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            }

        elif event_type == "resolve":
            summary += (
                f":heavy_check_mark:*[RESOLVED] The AWS Health issue with the {event_details['successfulSet'][0]['event']['service'].upper()} service in "
                f"the {event_details['successfulSet'][0]['event']['region'].upper()} region is now resolved.*"
            )
            message = {
                "text": summary,
                "accounts": affected_org_accounts,
                "resources": affected_org_entities,                
                "service": event_details['successfulSet'][0]['event']['service'],
                "region": event_details['successfulSet'][0]['event']['region'],
                "start_time": cleanup_time(event_details['successfulSet'][0]['event']['startTime']),
                "status": event_details['successfulSet'][0]['event']['statusCode'],
                "event_arn": event_details['successfulSet'][0]['event']['arn'],
                "updates": get_last_aws_update(event_details)
            } 
    json.dumps(message)
    print("Message sent to Slack: ", message)
    return message


def get_message_for_chime(event_details, event_type, affected_accounts, affected_entities):
    message = ""
    if len(affected_entities) >= 1:
        affected_entities = "\n".join(affected_entities)
        if affected_entities == "UNKNOWN":
            affected_entities = "All resources\nin region"
    else:
        affected_entities = "All resources\nin region"
    if len(affected_accounts) >= 1:
        affected_accounts = "\n".join(affected_accounts)
    else:
        affected_accounts = "All accounts\nin region"   
    summary = ""
    if event_type == "create":

        message = str("/md" + "\n" + "**:rotating_light:\[NEW\] AWS Health reported an issue with the " + event_details['successfulSet'][0]['event']['service'].upper() +  " service in " + event_details['successfulSet'][0]['event']['region'].upper() + " region.**" + "\n"
          "---" + "\n"
          "**Account(s)**: " + affected_accounts + "\n"
          "**Resource(s)**: " + affected_entities + "\n"
          "**Service**: " + event_details['successfulSet'][0]['event']['service'] + "\n"
          "**Region**: " + event_details['successfulSet'][0]['event']['region'] + "\n" 
          "**Start Time (UTC)**: " + cleanup_time(event_details['successfulSet'][0]['event']['startTime']) + "\n"
          "**Status**: " + event_details['successfulSet'][0]['event']['statusCode'] + "\n"
          "**Event ARN**: " + event_details['successfulSet'][0]['event']['arn'] + "\n"          
          "**Updates:**" + "\n" + get_last_aws_update(event_details)
          )

    elif event_type == "resolve":

        message = str("/md" + "\n" + "**:heavy_check_mark:\[RESOLVED\] The AWS Health issue with the " + event_details['successfulSet'][0]['event']['service'].upper() +  " service in " + event_details['successfulSet'][0]['event']['region'].upper() + " region is now resolved.**" + "\n"
          "---" + "\n"
          "**Account(s)**: " + affected_accounts + "\n"
          "**Resource(s)**: " + affected_entities + "\n"
          "**Service**: " + event_details['successfulSet'][0]['event']['service'] + "\n"
          "**Region**: " + event_details['successfulSet'][0]['event']['region'] + "\n" 
          "**Start Time (UTC)**: " + cleanup_time(event_details['successfulSet'][0]['event']['startTime']) + "\n"
          "**End Time (UTC)**: " + cleanup_time(event_details['successfulSet'][0]['event']['endTime']) + "\n"
          "**Status**: " + event_details['successfulSet'][0]['event']['statusCode'] + "\n"
          "**Event ARN**: " + event_details['successfulSet'][0]['event']['arn'] + "\n"             
          "**Updates:**" + "\n" + get_last_aws_update(event_details)
        )
    json.dumps(message)
    print("Message sent to Chime: ", message)    
    return message


def get_org_message_for_chime(event_details, event_type, affected_org_accounts, affected_org_entities):
    message = ""
    summary = ""
    if len(affected_org_entities) >= 1:
        affected_org_entities = "\n".join(affected_org_entities)
    else:
        affected_org_entities = "All resources in region"
    if len(affected_org_accounts) >= 1:
        affected_org_accounts = "\n".join(affected_org_accounts)
    else:
        affected_org_accounts = "All accounts in region"
    if event_type == "create":
        
        message = str("/md" + "\n" + "**:rotating_light:\[NEW\] AWS Health reported an issue with the " + event_details['successfulSet'][0]['event']['service'].upper()) +  " service in " + str(event_details['successfulSet'][0]['event']['region'].upper() + " region**" + "\n"
          "---" + "\n"
          "**Account(s)**: " + affected_org_accounts + "\n"
          "**Resource(s)**: " + affected_org_entities + "\n"
          "**Service**: " + event_details['successfulSet'][0]['event']['service'] + "\n"
          "**Region**: " + event_details['successfulSet'][0]['event']['region'] + "\n" 
          "**Start Time (UTC)**: " + cleanup_time(event_details['successfulSet'][0]['event']['startTime']) + "\n"
          "**Status**: " + event_details['successfulSet'][0]['event']['statusCode'] + "\n"
          "**Event ARN**: " + event_details['successfulSet'][0]['event']['arn'] + "\n"             
          "**Updates:**" + "\n" + get_last_aws_update(event_details)
        )

    elif event_type == "resolve":

        message = str("/md" + "\n" + "**:heavy_check_mark:\[RESOLVED\] The AWS Health issue with the " + event_details['successfulSet'][0]['event']['service'].upper()) +  " service in " + str(event_details['successfulSet'][0]['event']['region'].upper() + " region is now resolved.**" + "\n"
          "---" + "\n"
          "**Account(s)**: " + affected_org_accounts + "\n"
          "**Resource(s)**: " + affected_org_entities + "\n"
          "**Service**: " + event_details['successfulSet'][0]['event']['service'] + "\n"
          "**Region**: " + event_details['successfulSet'][0]['event']['region'] + "\n" 
          "**Start Time (UTC)**: " + cleanup_time(event_details['successfulSet'][0]['event']['startTime']) + "\n"
          "**End Time (UTC)**: " + cleanup_time(event_details['successfulSet'][0]['event']['endTime']) + "\n"
          "**Status**: " + event_details['successfulSet'][0]['event']['statusCode'] + "\n"
          "**Event ARN**: " + event_details['successfulSet'][0]['event']['arn'] + "\n"             
          "**Updates:**" + "\n" + get_last_aws_update(event_details)
        )
    print("Message sent to Chime: ", message)
    return message  



def get_message_for_teams(event_details, event_type, affected_accounts, affected_entities):
    message = ""
    if len(affected_entities) >= 1:
        affected_entities = "\n".join(affected_entities)
        if affected_entities == "UNKNOWN":
            affected_entities = "All resources\nin region"
    else:
        affected_entities = "All resources\nin region"
    if len(affected_accounts) >= 1:
        affected_accounts = "\n".join(affected_accounts)
    else:
        affected_accounts = "All accounts\nin region"      
    summary = ""
    if event_type == "create":
        title = "&#x1F6A8; [NEW] AWS Health reported an issue with the " + event_details['successfulSet'][0]['event'][
            'service'].upper() + " service in the " + event_details['successfulSet'][0]['event'][
                    'region'].upper() + " region."
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF0000",
            "summary": "AWS Health Aware Alert",
            "sections": [
                {
                    "activityTitle": str(title),
                    "markdown": False,
                    "facts": [
                        {"name": "Account(s)", "value": affected_accounts},
                        {"name": "Resource(s)", "value": affected_entities},
                        {"name": "Service", "value": event_details['successfulSet'][0]['event']['service']},
                        {"name": "Region", "value": event_details['successfulSet'][0]['event']['region']},
                        {"name": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime'])},
                        {"name": "Status", "value": event_details['successfulSet'][0]['event']['statusCode']},
                        {"name": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn']},
                        {"name": "Updates", "value": get_last_aws_update(event_details)}
                    ],
                }
            ]
        }

    elif event_type == "resolve":
        title = "&#x2705; [RESOLVED] The AWS Health issue with the " + event_details['successfulSet'][0]['event'][
            'service'].upper() + " service in the " + event_details['successfulSet'][0]['event'][
                    'region'].upper() + " region is now resolved."
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "00ff00",
            "summary": "AWS Health Aware Alert",
            "sections": [
                {
                    "activityTitle": str(title),
                    "markdown": False,
                    "facts": [
                        {"name": "Account(s)", "value": affected_accounts},
                        {"name": "Resource(s)", "value": affected_entities},
                        {"name": "Service", "value": event_details['successfulSet'][0]['event']['service']},
                        {"name": "Region", "value": event_details['successfulSet'][0]['event']['region']},
                        {"name": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime'])},
                        {"name": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime'])},
                        {"name": "Status", "value": event_details['successfulSet'][0]['event']['statusCode']},
                        {"name": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn']},
                        {"name": "Updates", "value": get_last_aws_update(event_details)}
                    ],
                }
            ]
        }
    print("Message sent to Teams: ", message)
    return message


def get_org_message_for_teams(event_details, event_type, affected_org_accounts, affected_org_entities):
    message = ""
    summary = ""
    if len(affected_org_entities) >= 1:
        affected_org_entities = "\n".join(affected_org_entities)
    else:
        affected_org_entities = "All resources in region"
    if len(affected_org_accounts) >= 1:
        affected_org_accounts = "\n".join(affected_org_accounts)
    else:
        affected_org_accounts = "All accounts in region"
    if event_type == "create":
        title = "&#x1F6A8; [NEW] AWS Health reported an issue with the " + event_details['successfulSet'][0]['event'][
            'service'].upper() + " service in the " + event_details['successfulSet'][0]['event'][
                    'region'].upper() + " region."
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF0000",
            "summary": "AWS Health Aware Alert",
            "sections": [
                {
                    "activityTitle": title,
                    "markdown": False,
                    "facts": [
                        {"name": "Account(s)", "value": affected_org_accounts},
                        {"name": "Resource(s)", "value": affected_org_entities},
                        {"name": "Service", "value": event_details['successfulSet'][0]['event']['service']},
                        {"name": "Region", "value": event_details['successfulSet'][0]['event']['region']},
                        {"name": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime'])},
                        {"name": "Status", "value": event_details['successfulSet'][0]['event']['statusCode']},
                        {"name": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn']},
                        {"name": "Updates", "value": event_details['successfulSet'][0]['eventDescription']['latestDescription']}
                    ],
                }
            ]
        }

    elif event_type == "resolve":
        title = "&#x2705; [RESOLVED] The AWS Health issue with the " + event_details['successfulSet'][0]['event'][
            'service'].upper() + " service in the " + event_details['successfulSet'][0]['event'][
                    'region'].upper() + " region is now resolved."
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "00ff00",
            "summary": "AWS Health Aware Alert",
            "sections": [
                {
                    "activityTitle": title,
                    "markdown": False,
                    "facts": [
                        {"name": "Account(s)", "value": affected_org_accounts},
                        {"name": "Resource(s)", "value": affected_org_entities},
                        {"name": "Service", "value": event_details['successfulSet'][0]['event']['service']},
                        {"name": "Region", "value": event_details['successfulSet'][0]['event']['region']},
                        {"name": "Start Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['startTime'])},
                        {"name": "End Time (UTC)", "value": cleanup_time(event_details['successfulSet'][0]['event']['endTime'])},
                        {"name": "Status", "value": event_details['successfulSet'][0]['event']['statusCode']},
                        {"name": "Event ARN", "value": event_details['successfulSet'][0]['event']['arn']},
                        {"name": "Updates", "value": event_details['successfulSet'][0]['eventDescription']['latestDescription']}
                    ],
                }
            ]
        }
    return message
    print("Message sent to Teams: ", message)


def get_message_for_email(event_details, event_type, affected_accounts, affected_entities):
    if len(affected_entities) >= 1:
        affected_entities = "\n".join(affected_entities)
        if affected_entities == "UNKNOWN":
            affected_entities = "All resources\nin region"
    else:
        affected_entities = "All resources\nin region"
    if len(affected_accounts) >= 1:
        affected_accounts = "\n".join(affected_accounts)
    else:
        affected_accounts = "All accounts\nin region"
    if event_type == "create":
        BODY_HTML = f"""
        <html>
            <body>
                <h>Greetings from AWS Health Aware,</h><br>
                <p>There is an AWS incident that is in effect which may likely impact your resources. Here are the details:<br><br>
                <b>Account(s):</b> {affected_accounts}<br>
                <b>Resource(s):</b> {affected_entities}<br>
                <b>Service:</b> {event_details['successfulSet'][0]['event']['service']}<br>
                <b>Region:</b> {event_details['successfulSet'][0]['event']['region']}<br>
                <b>Start Time (UTC):</b> {cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}<br>                
                <b>Status:</b> {event_details['successfulSet'][0]['event']['statusCode']}<br>
                <b>Event ARN:</b> {event_details['successfulSet'][0]['event']['arn']}<br> 
                <b>Updates:</b> {event_details['successfulSet'][0]['eventDescription']['latestDescription']}<br><br>
                For updates, please visit the <a href=https://status.aws.amazon.com>AWS Service Health Dashboard</a><br>
                If you are experiencing issues related to this event, please open an <a href=https://console.aws.amazon.com/support/home>AWS Support</a> case within your account.<br><br>
                Thanks, <br><br>AHA: AWS Health Aware
                </p>
            </body>
        </html>
    """
    else:
        BODY_HTML = f"""
        <html>
            <body>
                <h>Greetings again from AWS Health Aware,</h><br>
                <p>Good news! The AWS Health incident from earlier has now been marked as resolved.<br><br>
                <b>Account(s):</b> {affected_accounts}<br>
                <b>Resource(s):</b>   {affected_entities}<br>                         
                <b>Service:</b> {event_details['successfulSet'][0]['event']['service']}<br>
                <b>Region:</b> {event_details['successfulSet'][0]['event']['region']}<br>
                <b>Start Time (UTC):</b> {cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}<br>
                <b>End Time (UTC):</b> {cleanup_time(event_details['successfulSet'][0]['event']['endTime'])}<br>
                <b>Status:</b> {event_details['successfulSet'][0]['event']['statusCode']}<br>                
                <b>Event ARN:</b> {event_details['successfulSet'][0]['event']['arn']}<br>                
                <b>Updates:</b> {event_details['successfulSet'][0]['eventDescription']['latestDescription']}<br><br>  
                If you are still experiencing issues related to this event, please open an <a href=https://console.aws.amazon.com/support/home>AWS Support</a> case within your account.<br><br>                
                <br><br>
                Thanks, <br><br>AHA: AWS Health Aware
                </p>
            </body>
        </html>
    """
    print("Message sent to Email: ", BODY_HTML)
    return BODY_HTML


def get_org_message_for_email(event_details, event_type, affected_org_accounts, affected_org_entities):
    if len(affected_org_entities) >= 1:
        affected_org_entities = "\n".join(affected_org_entities)
    else:
        affected_org_entities = "All services related resources in region"
    if len(affected_org_accounts) >= 1:
        affected_org_accounts = "\n".join(affected_org_accounts)
    else:
        affected_org_accounts = "All accounts in region"
    if event_type == "create":
        BODY_HTML = f"""
        <html>
            <body>
                <h>Greetings from AWS Health Aware,</h><br>
                <p>There is an AWS incident that is in effect which may likely impact your resources. Here are the details:<br><br>
                <b>Account(s):</b> {affected_org_accounts}<br>
                <b>Resource(s):</b> {affected_org_entities}<br>
                <b>Service:</b> {event_details['successfulSet'][0]['event']['service']}<br>
                <b>Region:</b> {event_details['successfulSet'][0]['event']['region']}<br>
                <b>Start Time (UTC):</b> {cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}<br>
                <b>Status:</b> {event_details['successfulSet'][0]['event']['statusCode']}<br>                
                <b>Event ARN:</b> {event_details['successfulSet'][0]['event']['arn']}<br>                
                <b>Updates:</b> {event_details['successfulSet'][0]['eventDescription']['latestDescription']}<br><br>                 
                For updates, please visit the <a href=https://status.aws.amazon.com>AWS Service Health Dashboard</a><br>
                If you are experiencing issues related to this event, please open an <a href=https://console.aws.amazon.com/support/home>AWS Support</a> case within your account.<br><br>
                Thanks, <br><br>AHA: AWS Health Aware
                </p>
            </body>
        </html>
    """
    else:
        BODY_HTML = f"""
        <html>
            <body>
                <h>Greetings again from AWS Health Aware,</h><br>
                <p>Good news! The AWS Health incident from earlier has now been marked as resolved.<br><br>
                <b>Account(s):</b> {affected_org_accounts}<br>
                <b>Resource(s):</b> {affected_org_entities}<br>                            
                <b>Service:</b> {event_details['successfulSet'][0]['event']['service']}<br>
                <b>Region:</b> {event_details['successfulSet'][0]['event']['region']}<br>
                <b>Start Time (UTC):</b> {cleanup_time(event_details['successfulSet'][0]['event']['startTime'])}<br>
                <b>End Time (UTC):</b> {cleanup_time(event_details['successfulSet'][0]['event']['endTime'])}<br>
                <b>Status:</b> {event_details['successfulSet'][0]['event']['statusCode']}<br>                
                <b>Event ARN:</b> {event_details['successfulSet'][0]['event']['arn']}<br>
                <b>Updates:</b> {event_details['successfulSet'][0]['eventDescription']['latestDescription']}<br><br>               
                If you are still experiencing issues related to this event, please open an <a href=https://console.aws.amazon.com/support/home>AWS Support</a> case within your account.<br><br>                
                Thanks, <br><br>AHA: AWS Health Aware
                </p>
            </body>
        </html>
    """
    print("Message sent to Email: ", BODY_HTML)
    return BODY_HTML


def cleanup_time(event_time):
    """
    Takes as input a datetime string as received from The AWS Health event_detail call.  It converts this string to a
    datetime object, changes the timezone to EST and then formats it into a readable string to display in Slack.

    :param event_time: datetime string
    :type event_time: str
    :return: A formatted string that includes the month, date, year and 12-hour time.
    :rtype: str
    """
    event_time = datetime.strptime(event_time[:16], '%Y-%m-%d %H:%M')
    return event_time.strftime("%Y-%m-%d %H:%M:%S")


def get_last_aws_update(event_details):
    """
    Takes as input the event_details and returns the last update from AWS (instead of the entire timeline)

    :param event_details: Detailed information about a specific AWS health event.
    :type event_details: dict
    :return: the last update message from AWS
    :rtype: str
    """
    aws_message = event_details['successfulSet'][0]['eventDescription']['latestDescription']
    return aws_message


def format_date(event_time):
    """
    Takes as input a datetime string as received from The AWS Health event_detail call.  It converts this string to a
    datetime object, changes the timezone to EST and then formats it into a readable string to display in Slack.

    :param event_time: datetime string
    :type event_time: str
    :return: A formatted string that includes the month, date, year and 12-hour time.
    :rtype: str
    """
    event_time = datetime.strptime(event_time[:16], '%Y-%m-%d %H:%M')
    return event_time.strftime('%B %d, %Y at %I:%M %p')

