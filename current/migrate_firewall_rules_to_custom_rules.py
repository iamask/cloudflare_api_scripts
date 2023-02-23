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

# Initiate list for "for loop"
zone_ids = iterate_zone_ids_into_list(BASE_URL, headers)

def loop_firewall_rules_pages(BASE_URL, headers, zone_id):
    
    # Set array of list of firewall rules
    raw_firewall_rules_data = []
    
    # Set page to loop
    page = 1
    while True:

        # Make a request to the firewall rules endpoint with the current ID to get the list of firewall rules
        firewall_rules_api = BASE_URL + f"/{zone_id}/firewall/rules?page={page}&per_page=1000"
        response = requests.get(firewall_rules_api, headers=headers)
        
        # Catch error
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data from Firewall Rules IDs API. Status code: {response.status_code}")

        data = response.json()
        
        firewall_rules = data["result"]
        
        # Add lists to new list
        raw_firewall_rules_data.extend(firewall_rules)
        
        if not firewall_rules:
            break
        else:
            page += 1
                
    return raw_firewall_rules_data

def prepare_firewall_rules_for_migration(BASE_URL, headers, zone_id):
    
    # Instantiate new list
    new_custom_rules_list = []
    
    # Call raw firewall rules data
    raw_firewall_rules_data = loop_firewall_rules_pages(BASE_URL, headers, zone_id)
    
    for firewall_rule in raw_firewall_rules_data:
        
        # Extract top-level prop from the firewall rule payload
        new_custom_rule = {}
        new_custom_rule["description"] = firewall_rule["description"]
        new_custom_rule["description"] + "(Firewall Rule)"
        new_custom_rule["action"] = firewall_rule["action"]
        
        # Fix those bypass rules into skip rules, since bypass doesn't exist in custom rules
        if new_custom_rule["action"] == "bypass":
            new_custom_rule["action"] = "skip"
            new_custom_rule["action_parameters"] = {}
            new_custom_rule["action_parameters"]["products"] = firewall_rule["products"]
            
        # Fix those allow rules into skip rules, since bypass doesn't exist in custom rules
        if new_custom_rule["action"] == "allow":
            new_custom_rule["action"] = "skip"
            new_custom_rule["action_parameters"] = {}
            new_custom_rule["action_parameters"]["ruleset"] = "current"

        # Extract nested objects from the firewall rule payload
        new_custom_rule["expression"] = firewall_rule["filter"]["expression"]
        new_custom_rule["enabled"] = not firewall_rule["paused"]
        
        new_custom_rules_list.append(new_custom_rule)
    
    return new_custom_rules_list

def get_custom_ruleset_id(BASE_URL, headers, zone_id):

    # Get list of rulesets from zone
    rulesets_api = BASE_URL + f"/{zone_id}/rulesets"
    response = requests.get(rulesets_api, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve data from List Rulesets API. Status code: {response.status_code}")

    data = response.json()
    
    for ruleset_ids in data["result"]:
        if ruleset_ids["phase"] == "http_request_firewall_custom":
            ruleset_id = ruleset_ids["id"]
    
    return ruleset_id

def get_current_custom_ruleset_data(BASE_URL, headers, zone_id):
    
    # Getting the ruleset ID per zone that's looped in
    ruleset_id = get_custom_ruleset_id(BASE_URL, headers, zone_id)
    
    # Instantiate new list
    custom_ruleset = []

    # Get the current rules from the custom ruleset
    rulesets_id_api = BASE_URL + f"/{zone_id}/rulesets/{ruleset_id}"
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

def combine_and_migrate(BASE_URL, headers, zone_id):
    ruleset_id = get_custom_ruleset_id(BASE_URL, headers, zone_id)
    current_custom_rules = get_current_custom_ruleset_data(BASE_URL, headers, zone_id)
    firewall_rules = prepare_firewall_rules_for_migration(BASE_URL, headers, zone_id)
    
    # Combine old and new
    migrate = firewall_rules + current_custom_rules
    
    # Instantiate object
    payload = {}
    
    # Set up payload
    payload["rules"] = migrate
    
    # Get the current rules from the custom ruleset
    rulesets_id_api = BASE_URL + f"/{zone_id}/rulesets/{ruleset_id}"
    response = requests.put(rulesets_id_api, headers=headers, json=payload)
    print(response)
    if response.status_code != 200:
        raise Exception(f"Failed to add data to Rulesets API with specific ruleset id. Status code: {response.status_code}")
    
    return response

# Run the loop
for zone_id in zone_ids:
    loop_firewall_rules_pages(BASE_URL, headers, zone_id)
    prepare_firewall_rules_for_migration(BASE_URL, headers, zone_id)
    get_custom_ruleset_id(BASE_URL, headers, zone_id)
    get_current_custom_ruleset_data(BASE_URL, headers, zone_id)
    combine_and_migrate(BASE_URL, headers, zone_id)