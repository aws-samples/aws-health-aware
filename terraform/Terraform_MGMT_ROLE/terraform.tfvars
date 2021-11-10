# Region for IAM role creation - it's global service, so we will be just using one region.
aha_primary_region="us-east-1"

# Tags applied to all resources - using module provider. Update them per your requirement.
default_tags = {
  Application     = "AHA-Solution"
  Environment     = "DEV"
  auto-delete     = "no"
}

