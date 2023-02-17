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

    rulesets_api = BASE_URL + \
        f"/{zone_id}/rulesets"
    response = requests.get(rulesets_api, headers=headers)
    data = response.json()
    
    # Iterate over the data from the current page of the rulesets API
    for rulesets_ids in data["result"]:
        if rulesets_ids["phase"] == "http_request_firewall_custom":
            ruleset_id = rulesets_ids["id"]
            
            # Get versions objects
            rulesets_versions_api = BASE_URL + \
                f"/{zone_id}/rulesets/{ruleset_id}/versions"
            response = requests.get(rulesets_versions_api, headers=headers)
            data = response.json()
          
            # Iterate over the version ids and skipping the latest one, which is usually in the first object, since you can't delete the latest version as it is the same as the pinned version at this point         
            for rulesets_versions_id in data["result"][1:]:
                for version_id in rulesets_versions_id["version"]:
                    version_id = rulesets_versions_id["version"]
                
                # Nuke it
                rulesets_specific_versions_api = BASE_URL + \
                    f"/{zone_id}/rulesets/{ruleset_id}/versions/{version_id}"
                response = requests.delete(rulesets_specific_versions_api, headers=headers)
                print(response.text)