import os
import requests

# First API endpoint to get the IDs
BASE_URL = "https://api.cloudflare.com/client/v4/zones"

# Define Auth headers
auth_email = os.environ.get('CLOUDFLARE_EMAIL')
auth_key = os.environ.get('CLOUDFLARE_API_KEY')


# Set headers
headers = {
    "X-Auth-Key": auth_key,
    "X-Auth-Email": auth_email
}

# Make a request to the first API endpoint
response = requests.get(BASE_URL, headers=headers)

# Parse the response as JSON
data = response.json()
#print(data)
# Iterate over the data from the first API
for zone_ids in data["result"]:
   # print(zone_ids)
    # Get the ID from the current item
    zone_id = zone_ids["id"]
  #  print(zone_id)
    # Make a request to the second API endpoint for the current ID
    page = 1
    while True:
        rulesets_api = BASE_URL + \
            f"/{zone_id}/rulesets"
        response = requests.get(rulesets_api, headers=headers)
        rulesets_raw_data = response.json()
        
        # Iterate over the data from the current page of the rulesets API
        for rulesets_ids in rulesets_raw_data["result"]:
            if rulesets_ids["phase"] == "http_request_firewall_custom":
                ruleset_id = rulesets_ids["id"]
                print(ruleset_id)
                
                rulesets_versions_api = BASE_URL + \
                    f"/{zone_id}/rulesets{ruleset_id}/versions"
                response = requests.get(rulesets_versions_api, headers=headers)
                rulesets_version_raw_data = response.json()
                
                for rulesets_versions_id in rulesets_version_raw_data["result"][1:]:
                    version_id = rulesets_versions_id["version"]
                    print(version_id)
                    
                    rulesets_specific_versions_api = BASE_URL + \
                        f"/{zone_id}/rulesets{ruleset_id}/versions/{version_id}"
                    response = requests.delete(rulesets_specific_versions_api, headers=headers)
                    print(response.text)

        # Check if there are more pages of results
        if not data["result"]:
            break

        # Move to the next page of results
        page += 1
