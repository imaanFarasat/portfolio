"""
Shopify Collection Creator via REST API (Legacy but simpler)
Creates collections based on shopify_collections_suggestions.json
"""

import json
import requests
import os
from typing import Dict, List

# Configuration
SHOP_DOMAIN = os.getenv('SHOPIFY_SHOP_DOMAIN', 'your-store.myshopify.com')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN', 'your-access-token-here')
API_VERSION = '2025-04'

# REST API endpoints
SMART_COLLECTIONS_URL = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/smart_collections.json"
CUSTOM_COLLECTIONS_URL = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/custom_collections.json"

# Headers
HEADERS = {
    'X-Shopify-Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
}


def create_smart_collection(title: str, description: str, rules: List[Dict]) -> Dict:
    """
    Create an automated (smart) collection using REST API
    
    Args:
        title: Collection title
        description: Collection description (HTML)
        rules: List of rule dictionaries
    
    Returns:
        API response dictionary
    """
    
    payload = {
        'smart_collection': {
            'title': title,
            'body_html': description,
            'rules': rules,
            'disjunctive': True  # OR logic (False = AND logic)
        }
    }
    
    response = requests.post(SMART_COLLECTIONS_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    
    return response.json()


def create_custom_collection(title: str, description: str) -> Dict:
    """
    Create a manual (custom) collection using REST API
    
    Args:
        title: Collection title
        description: Collection description (HTML)
    
    Returns:
        API response dictionary
    """
    
    payload = {
        'custom_collection': {
            'title': title,
            'body_html': description
        }
    }
    
    response = requests.post(CUSTOM_COLLECTIONS_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    
    return response.json()


def parse_condition_to_rule(condition: str) -> Dict:
    """
    Parse condition string to REST API rule format
    
    Args:
        condition: Condition string like "Product title contains: 'yak chews'"
    
    Returns:
        Rule dictionary
    """
    
    # Handle "Product title contains: 'yak chews'" format
    if 'contains' in condition.lower():
        # Extract search term
        if "'" in condition:
            search_term = condition.split("'")[1]
        elif '"' in condition:
            search_term = condition.split('"')[1]
        else:
            search_term = condition.split(':')[-1].strip()
        
        return {
            'column': 'title',
            'relation': 'contains',
            'condition': search_term.strip()
        }
    
    return None


def create_collections_from_json(json_file: str = 'shopify_collections_suggestions.json'):
    """
    Create collections from JSON configuration file
    """
    
    with open(json_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    collections = config.get('collections', [])
    
    print(f"Creating {len(collections)} collections using REST API...\n")
    
    created_collections = []
    
    for collection in collections:
        title = collection['collection_name']
        description = collection.get('description', '')
        collection_type = collection.get('collection_type', 'automatic')
        
        print(f"Creating collection: {title}")
        
        # Convert description to HTML
        if not description.startswith('<'):
            description_html = f"<p>{description}</p>"
        else:
            description_html = description
        
        try:
            if collection_type == 'automatic' and 'conditions' in collection:
                # Create smart collection
                condition_str = collection['conditions']
                
                # Parse OR conditions
                if ' OR ' in condition_str.upper():
                    or_conditions = condition_str.split(' OR ')
                    rules = []
                    for cond in or_conditions:
                        rule = parse_condition_to_rule(cond.strip())
                        if rule:
                            rules.append(rule)
                else:
                    rule = parse_condition_to_rule(condition_str)
                    rules = [rule] if rule else []
                
                response = create_smart_collection(title, description_html, rules)
                collection_data = response.get('smart_collection', {})
                
            else:
                # Create custom collection
                response = create_custom_collection(title, description_html)
                collection_data = response.get('custom_collection', {})
            
            collection_id = collection_data.get('id')
            print(f"  ✅ Created: {title} (ID: {collection_id})")
            
            created_collections.append({
                'title': title,
                'id': collection_id,
                'handle': collection_data.get('handle')
            })
        
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json() if e.response else str(e)
            print(f"  ❌ Error: {error_msg}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()
    
    print(f"\n✅ Successfully created {len(created_collections)} collections!")
    return created_collections


def main():
    """Main function"""
    
    if ACCESS_TOKEN == 'your-access-token-here' or SHOP_DOMAIN == 'your-store.myshopify.com':
        print("⚠️  Please set your Shopify credentials!")
        print("\nOption 1: Set environment variables:")
        print("  export SHOPIFY_SHOP_DOMAIN='your-store.myshopify.com'")
        print("  export SHOPIFY_ACCESS_TOKEN='your-token-here'")
        print("\nOption 2: Edit the script and update SHOP_DOMAIN and ACCESS_TOKEN")
        return
    
    try:
        created = create_collections_from_json()
        
        with open('created_collections.json', 'w') as f:
            json.dump(created, f, indent=2)
        
        print("\n📝 Collection IDs saved to: created_collections.json")
        
    except FileNotFoundError:
        print("❌ Error: shopify_collections_suggestions.json not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == '__main__':
    main()

