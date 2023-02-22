# Firewall Rules to Custom Rules

# Remember to install requirements

```python3 -m pip intall -r requirements.txt```

## Run the script:
```python3 migrate_firewall_rules_to_custom_rules.py```

## If no Custom Rules have been made before, run:
```python3 initiate_custom_rulesets_for_zones.py``` 

## Once tested and ready to move off Firewall Rules entirely, run:
```python3 delete_all_firewall_rules.py```