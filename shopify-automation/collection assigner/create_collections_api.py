"""
Shopify Collection Creator via GraphQL API
Creates collections based on shopify_collections_suggestions.json
"""

import json
import requests
import os
from typing import Dict, List, Optional

# Configuration - Set these in environment variables or update here
SHOP_DOMAIN = os.getenv('SHOPIFY_SHOP_DOMAIN', 'your-store.myshopify.com')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN', 'your-access-token-here')
API_VERSION = '2025-04'

# GraphQL endpoint
GRAPHQL_URL = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/graphql.json"

# Headers for API requests
HEADERS = {
    'X-Shopify-Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
}


def create_collection(title: str, description: str, rules: Optional[List[Dict]] = None) -> Dict:
    """
    Create a collection using GraphQL API
    
    Args:
        title: Collection title
        description: Collection description (HTML)
        rules: List of rules for automated collection (None for manual)
    
    Returns:
        API response dictionary
    """
    
    if rules:
        # Create automated collection (Smart Collection)
        rules_list = []
        for rule in rules:
            rules_list.append(f"""
                {{
                  column: {rule['column']}
                  relation: {rule['relation']}
                  condition: "{rule['condition']}"
                }}
            """)
        
        rules_str = ",\n".join(rules_list)
        disjunctive = rule.get('disjunctive', True)
        
        mutation = f"""
        mutation {{
          collectionCreate(input: {{
            title: "{title}"
            descriptionHtml: "{description}"
            ruleSet: {{
              appliedDisjunctively: {str(disjunctive).lower()}
              rules: [
                {rules_str}
              ]
            }}
          }}) {{
            collection {{
              id
              title
              handle
            }}
            userErrors {{
              field
              message
            }}
          }}
        }}
        """
    else:
        # Create manual collection (Custom Collection)
        mutation = f"""
        mutation {{
          collectionCreate(input: {{
            title: "{title}"
            descriptionHtml: "{description}"
          }}) {{
            collection {{
              id
              title
              handle
            }}
            userErrors {{
              field
              message
            }}
          }}
        }}
        """
    
    response = requests.post(GRAPHQL_URL, json={'query': mutation}, headers=HEADERS)
    response.raise_for_status()
    
    return response.json()


def publish_collection(collection_id: str, publication_id: str = None) -> Dict:
    """
    Publish a collection to make it visible
    
    Args:
        collection_id: Collection Global ID
        publication_id: Publication Global ID (defaults to online store)
    
    Returns:
        API response dictionary
    """
    
    # If no publication ID provided, you'll need to fetch it first
    # For now, this is a placeholder - you may need to get publication ID
    if not publication_id:
        # You'll need to query for publications first
        query = """
        query {
          publications(first: 1) {
            edges {
              node {
                id
                name
              }
            }
          }
        }
        """
        pub_response = requests.post(GRAPHQL_URL, json={'query': query}, headers=HEADERS)
        pub_data = pub_response.json()
        
        if pub_data.get('data', {}).get('publications', {}).get('edges'):
            publication_id = pub_data['data']['publications']['edges'][0]['node']['id']
        else:
            print("Warning: Could not find publication ID. Collection will remain unpublished.")
            return {}
    
    mutation = f"""
    mutation {{
      publishablePublish(id: "{collection_id}", input: {{
        publicationId: "{publication_id}"
      }}) {{
        publishable {{
          id
        }}
        userErrors {{
          field
          message
        }}
      }}
    }}
    """
    
    response = requests.post(GRAPHQL_URL, json={'query': mutation}, headers=HEADERS)
    response.raise_for_status()
    
    return response.json()


def convert_rest_condition_to_graphql(condition: str) -> Dict:
    """
    Convert REST API condition format to GraphQL format
    
    Args:
        condition: Condition string from JSON (e.g., "Product title contains: 'yak chews'")
    
    Returns:
        Dictionary with column, relation, and condition
    """
    
    # Parse condition like "Product title contains: 'yak chews'"
    if "contains" in condition.lower():
        # Extract the search term
        if "'" in condition:
            search_term = condition.split("'")[1]
        elif '"' in condition:
            search_term = condition.split('"')[1]
        else:
            # Fallback: extract after colon
            search_term = condition.split(":")[-1].strip()
        
        return {
            'column': 'TITLE',
            'relation': 'CONTAINS',
            'condition': search_term.strip()
        }
    
    # Add more condition parsers as needed
    return None


def create_collections_from_json(json_file: str = 'shopify_collections_suggestions.json'):
    """
    Create collections from the JSON configuration file
    
    Args:
        json_file: Path to collections JSON file
    """
    
    # Load collections configuration
    with open(json_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    collections = config.get('collections', [])
    
    print(f"Creating {len(collections)} collections...\n")
    
    created_collections = []
    
    for collection in collections:
        title = collection['collection_name']
        description = collection.get('description', '')
        collection_type = collection.get('collection_type', 'automatic')
        
        print(f"Creating collection: {title}")
        
        # Convert description to HTML if needed
        if not description.startswith('<'):
            description_html = f"<p>{description}</p>"
        else:
            description_html = description
        
        # Build rules for automated collections
        rules = None
        if collection_type == 'automatic' and 'conditions' in collection:
            # Parse conditions - this is a simplified parser
            # You may need to enhance this based on your condition format
            condition_str = collection['conditions']
            
            # Handle OR conditions (disjunctive)
            if ' OR ' in condition_str.upper():
                or_conditions = condition_str.split(' OR ')
                rules = []
                for cond in or_conditions:
                    rule = convert_rest_condition_to_graphql(cond.strip())
                    if rule:
                        rules.append(rule)
            else:
                rule = convert_rest_condition_to_graphql(condition_str)
                if rule:
                    rules = [rule]
        
        try:
            # Create collection
            response = create_collection(title, description_html, rules)
            
            if response.get('data', {}).get('collectionCreate', {}).get('userErrors'):
                errors = response['data']['collectionCreate']['userErrors']
                print(f"  ❌ Errors: {errors}")
            else:
                collection_data = response.get('data', {}).get('collectionCreate', {}).get('collection', {})
                collection_id = collection_data.get('id')
                print(f"  ✅ Created: {collection_data.get('title')} (ID: {collection_id})")
                
                created_collections.append({
                    'title': title,
                    'id': collection_id,
                    'handle': collection_data.get('handle')
                })
                
                # Optionally publish the collection
                # Uncomment the line below to auto-publish
                # publish_collection(collection_id)
        
        except Exception as e:
            print(f"  ❌ Error creating collection: {str(e)}")
        
        print()
    
    print(f"\n✅ Successfully created {len(created_collections)} collections!")
    return created_collections


def main():
    """Main function"""
    
    # Check if credentials are set
    if ACCESS_TOKEN == 'your-access-token-here' or SHOP_DOMAIN == 'your-store.myshopify.com':
        print("⚠️  Please set your Shopify credentials!")
        print("\nOption 1: Set environment variables:")
        print("  export SHOPIFY_SHOP_DOMAIN='your-store.myshopify.com'")
        print("  export SHOPIFY_ACCESS_TOKEN='your-token-here'")
        print("\nOption 2: Edit the script and update SHOP_DOMAIN and ACCESS_TOKEN variables")
        return
    
    try:
        created = create_collections_from_json()
        
        # Save created collections info
        with open('created_collections.json', 'w') as f:
            json.dump(created, f, indent=2)
        
        print("\n📝 Collection IDs saved to: created_collections.json")
        
    except FileNotFoundError:
        print("❌ Error: shopify_collections_suggestions.json not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == '__main__':
    main()

