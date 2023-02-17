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
        second_api_url = BASE_URL + \
            f"/{zone_id}/firewall/rules?page={page}&per_page=10"
        response = requests.get(second_api_url, headers=headers)
        data = response.json()
        # Iterate over the data from the current page of the second API
        for firewall_rule_ids in data["result"]:
         #   print(firewall_rule_ids)
            # Check if the item's description matches the desired value
            if firewall_rule_ids["description"] == "duplicate form values":
                # Get the ID from the current item
                firewall_rule_id = firewall_rule_ids["id"]
            #    print(firewall_rule_id)
                # Make a request to the third API endpoint for the current IDs
                third_api_url = BASE_URL + \
                    f"/{zone_id}/firewall/rules/{firewall_rule_id}"
                response = requests.delete(third_api_url, headers=headers)
            #    print(data)
        # Check if there are more pages of results
        if not data["result"]:
            break

        # Move to the next page of results
        page += 1
