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
        response = requests.get(BASE_URL+ \
                f"?page={page}&per_page=1000", headers=headers)
        
        # Catch error
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data from API. Status code: {response.status_code}")
        
        # Parse the response as JSON
        data = response.json()
        
        # Get the result payload
        raw_zone_ids = data["result"]
        
        # Add all zone_ids into list
        raw_zone_id_list.extend(raw_zone_ids)
        
        if not data["result"]:
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

def loop_firewall_rules_pages(BASE_URL, headers):
    
    # Set array of list of firewall rules
    raw_firewall_rules_data = []
    zone_ids = iterate_zone_ids_into_list(BASE_URL, headers)
    
    for zone_id in zone_ids:
        
        page = 1
        while True:

            # Make a request to the firewall rules endpoint with the current ID to get the list of firewall rules
            firewall_rules_api = BASE_URL + \
                f"/{zone_id}/firewall/rules?page={page}&per_page=1000"
            response = requests.get(firewall_rules_api, headers=headers)
            
            # Catch error
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve data from API. Status code: {response.status_code}")

            data = response.json()
            
            firewall_rules = data["result"]
            raw_firewall_rules_data.extend(firewall_rules)
            
            if not firewall_rules:
                break
            else:
                page += 1
                
    return raw_firewall_rules_data

def prepare_firewall_rules_for_migration(BASE_URL, headers):
    
    firewall_rules_list = []
    raw_firewall_rules_data = loop_firewall_rules_pages(BASE_URL, headers)
    
    # Extract top-level prop from the firewall rule payload
    firewall_rules = {}
    firewall_rules["description"] = raw_firewall_rules_data["description"]
    firewall_rules["action"] = raw_firewall_rules_data["action"]
    
    # Fix those bypass and allow rules into skip, since bypass doesn't exist in custom rules
    if firewall_rules["action"] == "bypass":
        firewall_rules["action"] = "skip"
        firewall_rules["action_parameters"] = {}
        firewall_rules["action_parameters"]["products"] = raw_firewall_rules_data["products"]
    if firewall_rules["action"] == "allow":
        firewall_rules["action"] = "skip"
        firewall_rules["action_parameters"] = {}
        firewall_rules["action_parameters"]["ruleset"] = "current"

    # Extract nested objects from the firewall rule payload
    firewall_rules["expression"] = raw_firewall_rules_data["expression"]["filters"]
    firewall_rules["enabled"] = not raw_firewall_rules_data["paused"]
    firewall_rules_list.append(firewall_rules)
    
    return firewall_rules_list

print(prepare_firewall_rules_for_migration(BASE_URL, headers))