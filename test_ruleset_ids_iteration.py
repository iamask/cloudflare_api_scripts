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

def loop_zone_id_pages(BASE_URL, headers):
    
# Set array of list of zone ids
    raw_zone_id_list = []
    page = 1
    while True:
        # Make a request to the zones API endpoint to get the zone ids
        response = requests.get(BASE_URL+ f"?page={page}&per_page=1000", headers=headers)
        
        # Catch error
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data from the Zone IDs API. Status code: {response.status_code}")
        
        # Parse the response as JSON
        data = response.json()
        
        # Get the result payload
        raw_zone_ids = data["result"]
        
        # Add all zone_ids into list
        raw_zone_id_list.extend(raw_zone_ids)
        
        if not raw_zone_ids:
            break
        page += 1

    return raw_zone_id_list

def iterate_zone_ids_into_list(BASE_URL, headers):
    
    # Set array for only zone IDs
    zone_id_list = []
    
    # Call looped zone ids pages function
    raw_zone_ids = loop_zone_id_pages(BASE_URL, headers)
    
    # Iterate raw list for zone_ids
    for zone_ids in raw_zone_ids:
        
        # Get each zone ID from list
        zone_id = zone_ids["id"]
        
        zone_id_list.append(zone_id)

    return zone_id_list

def get_custom_ruleset_ids(BASE_URL, headers):
    
    zone_ids = iterate_zone_ids_into_list(BASE_URL, headers)
    
    # Set array for only ruleset IDs
    ruleset_id_list = []
    
    for zone_id in zone_ids:
        
        # Get list of rulesets from zone
        rulesets_api = BASE_URL + f"/{zone_id}/rulesets"
        response = requests.get(rulesets_api, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data from List Rulesets API. Status code: {response.status_code}")

        data = response.json()
        
        for ruleset_ids in data["result"]:
            if ruleset_ids["phase"] == "http_request_firewall_custom":
                ruleset_id = ruleset_ids["id"]
                ruleset_id_list.append(ruleset_id)
                
    return ruleset_id_list

def get_current_custom_ruleset_data(BASE_URL, headers):
    zone_ids = iterate_zone_ids_into_list(BASE_URL, headers)
    ruleset_ids = get_custom_ruleset_ids(BASE_URL, headers)
    
    custom_ruleset = []
    for zone_id in zone_ids:
        for ruleset_id in ruleset_ids:
            # Get the current rules from the custom ruleset
            rulesets_id_api = BASE_URL + f"/{zone_id}/rulesets/{ruleset_id}"
            response = requests.get(rulesets_id_api, headers=headers)

            if response.status_code == 404:
                continue
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve data from List Rulesets API with specific ruleset id. Status code: {response.status_code}") 
        
            data = response.json()
            
            if not data["result"]:
                
            # Transform data
                for rule in data["result"]["rules"]:
                    current_custom_ruleset = {}
                    current_custom_ruleset["action"] = rule["action"]
                    current_custom_ruleset["expression"] = rule["expression"]
                    current_custom_ruleset["description"] = rule["description"]
                    current_custom_ruleset["enabled"] = rule["enabled"]
                    custom_ruleset.append(current_custom_ruleset)
                    
    return custom_ruleset
print(get_current_custom_ruleset_data(BASE_URL, headers))