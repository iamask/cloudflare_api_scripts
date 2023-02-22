# Firewall Rules to Custom Rules

# Remember to install requirements
```python3 -m pip intall -r requirements.txt```

## API Keys/Tokens
The zone IDs used will depend on the scope of your API key, if you're a member of many orgs, then it'll run for any zones that are compatible. 

If you want to run scoped tokens instead, feel free to create a branch and change out the header variables to account for scoped tokens.

These should be the necessary ones:
`Account - Firewall Access - Edit`
`Account - Account Settings - Edit`
`Zone - Zone Settings - Read`
`Zone - Firewall Service - Edit`
`Zone - Zone WAF - Edit`

## Run the script:
```python3 migrate_firewall_rules_to_custom_rules.py```

## If no Custom Rules have been made before, run:
```python3 initiate_custom_rulesets_for_zones.py``` 

## Once tested and ready to move off Firewall Rules entirely, run:
```python3 delete_all_firewall_rules.py```