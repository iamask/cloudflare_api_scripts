import os
import requests

# Base endpoint for Cloudflare's API for zones
BASE_URL = "https://api.cloudflare.com/client/v4/zones"

# Define Auth headers
auth_email = os.environ.get('CLOUDFLARE_EMAIL')
auth_key = os.environ.get('CLOUDFLARE_API_KEY')

# Set headers
headers = {
    "X-Auth-Key": auth_key,
    "X-Auth-Email": auth_email
}

zone_id = input("Enter zone_id: ")
ruleset_id = input("Enter custom_ruleset_id: ")

def get_previous_version_id(BASE_URL, headers, zone_id, ruleset_id):
    # Get versions objects
    rulesets_versions_api = BASE_URL + f"/{zone_id}/rulesets/{ruleset_id}/versions"
    response = requests.get(rulesets_versions_api, headers=headers)
    data = response.json()

    # Iterate over the version ids and skipping the latest one, which is usually in the first object, since you can't delete the latest version as it is the same as the pinned version at this point         
    for rulesets_versions_id in data["result"][1:]:
        for version_id in rulesets_versions_id["version"]:
            version_id = rulesets_versions_id["version"]
    
    return version_id
        
def get_previous_version_id_data(BASE_URL, headers, zone_id, ruleset_id):
    
    # Get previous version ID
    version_id = get_previous_version_id(BASE_URL, headers, zone_id, ruleset_id)
    
    # Instantiate new list
    custom_ruleset = []

    # Get the current rules from the custom ruleset
    rulesets_id_api = BASE_URL + f"/{zone_id}/rulesets/{ruleset_id}/versions/{version_id}"
    response = requests.get(rulesets_id_api, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve data from List Rulesets API with specific ruleset id. Status code: {response.status_code}")

    data = response.json()
    
    if "rules" in data["result"]:
        rules = data["result"]["rules"]
        # Transform data
        for rule in rules:
            current_custom_ruleset = {}
            current_custom_ruleset["action"] = rule["action"]
            current_custom_ruleset["expression"] = rule["expression"]
            current_custom_ruleset["description"] = rule["description"]
            current_custom_ruleset["enabled"] = rule["enabled"]
            
            # Add data to new list
            custom_ruleset.append(current_custom_ruleset)
                    
    return custom_ruleset

def revert(BASE_URL, headers, zone_id, ruleset_id):

    current_custom_rules = get_previous_version_id_data(BASE_URL, headers, zone_id, ruleset_id)
    
    # Instantiate object
    payload = {}
    
    # Set up payload
    payload["rules"] = current_custom_rules
    
    # Get the current rules from the custom ruleset
    rulesets_id_api = BASE_URL + f"/{zone_id}/rulesets/{ruleset_id}"
    response = requests.put(rulesets_id_api, headers=headers, json=payload)
    print(response)
    
    if response.status_code != 200:
        raise Exception(f"Failed to add data to Rulesets API with specific ruleset id. Status code: {response.status_code}")
    
    return response