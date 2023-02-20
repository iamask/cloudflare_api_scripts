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

# Iterate over the data from the first API
for zone_ids in data["result"]:

    # Get the ID from the current item
    zone_id = zone_ids["id"]

    # Call the rulesets API
    rulesets_api = BASE_URL + \
        f"/{zone_id}/rulesets"
    response = requests.get(rulesets_api, headers=headers)
    data = response.json()
    
    # Iterate over the data from the rulesets API and filter for custom rules ruleset
    for rulesets_ids in data["result"]:
        if rulesets_ids["phase"] == "http_request_firewall_custom":
            ruleset_id = rulesets_ids["id"]
            
            empty_payload = {}
            empty_payload["rules"] = []
            
            # Put empty payload into ruleset to nuke it
            rulesets_specific_api = BASE_URL + \
                f"/{zone_id}/rulesets/{ruleset_id}"
            response = requests.put(rulesets_specific_api, headers=headers, json=empty_payload)
            data = response.json()
            print(data)
            # # Iterate over the rule ids
            # for rulesets_rules_id in data["result"]["rules"]:
            #     for rule_id in rulesets_rules_id["id"]:
            #         rule_id = rulesets_rules_id["id"]
                
            #     # Nuke the rules in the ruleset (I suppose you could also just PUT an empty payload)
            #     rulesets_specific_versions_api = BASE_URL + \
            #         f"/{zone_id}/rulesets/{ruleset_id}/rules/{rule_id}"
            #     response = requests.delete(rulesets_specific_versions_api, headers=headers)
            #     print(response.text)