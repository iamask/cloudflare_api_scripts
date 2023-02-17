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

    # Make a request to the second API endpoint for the current ID
    page = 1
    while True:
        # Get filters
        filters_api = BASE_URL + \
            f"/{zone_id}/filters?page={page}&per_page=1000"
        response = requests.get(filters_api, headers=headers)
        data = response.json()
        
        # Iterate over the data from the current page of the filters API
        for filters in data["result"]:

            # Check if the filter matches the expression 
            if "ip.src in $crowdsec_managed_challenge" in filters["expression"]:
                
                # Get the ID from the current item
                filters_id = filters["id"]
                
                # Make a request to the filters API endpoint for the current IDs
                filters_id_api = BASE_URL + \
                    f"/{zone_id}/filters/{filters_id}"
                response = requests.delete(filters_id_api, headers=headers)
                print(response.text)

        # Check if there are more pages of results
        if not data["result"]:
            break
        # Move to the next page of results
        page += 1
