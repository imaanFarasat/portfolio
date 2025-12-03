from google_sheets_reader import GoogleSheetsReader
from google_drive_reader import GoogleDriveReader
from shopify_creator import ShopifyProductCreator
from config import Config
import time
import sys

def process_products(continuous=False, check_interval=300):
    """Process products from Google Sheet and upload to Shopify"""
    
    # Initialize readers and creator
    print("Initializing Google Sheets reader...")
    sheets_reader = GoogleSheetsReader(Config.GOOGLE_CREDENTIALS_FILE)
    
    print("Initializing Google Drive reader...")
    drive_reader = GoogleDriveReader(Config.GOOGLE_CREDENTIALS_FILE)
    
    print("Initializing Shopify creator...")
    shopify_creator = ShopifyProductCreator()
    
    processed_count = 0
    rate_limit_hit = False  # Track if we hit rate limits in this cycle
    
    while True:
        try:
            # Reset rate limit flag at start of each cycle
            rate_limit_hit = False
            
            # Read products from Google Sheet
            print(f"\n{'='*60}")
            print(f"Checking for new products... (Run #{processed_count + 1})")
            print(f"{'='*60}")
            products = sheets_reader.parse_products(Config.GOOGLE_SHEETS_ID)
            
            print(f"Found {len(products)} products in Google Sheet")
            
            new_products_found = 0
            descriptions_generated_this_cycle = 0
            max_descriptions_per_cycle = 1  # Only generate 1 description per cycle to avoid rate limits
            
            # Process each product
            for row_number, product_data in products.items():
                title = product_data['title']
                variants = product_data['variants']
                
                print(f"\nProcessing product: {title} (Row {row_number})")
                print(f"  Variants: {len(variants)}")
                
                # Check if product already exists in Shopify
                existing_product = shopify_creator.get_product_by_title(title)
                
                if existing_product:
                    product_id = existing_product["id"]
                    has_description = existing_product.get("has_description", False)
                    
                    print(f"  Product '{title}' already exists in Shopify (ID: {product_id})")
                    
                    if has_description:
                        desc_length = len(existing_product.get("body_html", "") or "")
                        print(f"  Product already has a description ({desc_length} characters). Skipping generation.")
                    
                    # If product exists but doesn't have a description, generate and add it
                    # But only if we haven't hit rate limits and haven't exceeded max per cycle
                    if (not has_description and shopify_creator.openai_client and 
                        not rate_limit_hit and descriptions_generated_this_cycle < max_descriptions_per_cycle):
                        print(f"  Product has no description. Generating one...")
                        try:
                            description = shopify_creator.generate_product_description(title)
                            
                            if description:
                                if shopify_creator.update_product_description(product_id, description):
                                    print(f"  ✓ Product description added successfully")
                                    descriptions_generated_this_cycle += 1
                                else:
                                    print(f"  ✗ Failed to update product description")
                            else:
                                print(f"  Warning: Could not generate description")
                        except Exception as e:
                            if 'RATE_LIMIT_EXCEEDED' in str(e):
                                rate_limit_hit = True
                                print(f"  Rate limit reached. Skipping remaining descriptions this cycle.")
                            else:
                                print(f"  Warning: Could not generate description: {e}")
                        
                        # Add delay between description generations to avoid rate limits
                        if shopify_creator.openai_client and descriptions_generated_this_cycle < max_descriptions_per_cycle:
                            print(f"  Waiting 5 seconds before next description generation...")
                            time.sleep(5)
                    elif not has_description and shopify_creator.openai_client:
                        if rate_limit_hit:
                            print(f"  Skipping description generation (rate limit hit)")
                        elif descriptions_generated_this_cycle >= max_descriptions_per_cycle:
                            print(f"  Skipping description generation (max per cycle reached, will try next cycle)")
                    
                    print(f"  Skipping... (already processed)")
                    continue
                
                # This is a NEW product - process it
                new_products_found += 1
                print(f"  ✨ NEW PRODUCT DETECTED! Processing...")
                
                # Get images from Google Drive
                print(f"  Fetching images from folder '{row_number}'...")
                images = drive_reader.get_images_for_product(
                    Config.GOOGLE_DRIVE_FOLDER_ID,
                    row_number
                )
                
                print(f"  Found {len(images)} images")
                
                # Create product in Shopify
                print(f"  Creating product in Shopify...")
                product_id = shopify_creator.create_product(title, variants, images)
                
                if product_id:
                    print(f"  ✓ Successfully created product '{title}'")
                    
                    # Assign product to collections based on keywords in title
                    print(f"  Assigning product to collections based on title keywords...")
                    assigned_collections = shopify_creator.assign_product_to_collections(product_id, title)
                    
                    if assigned_collections:
                        print(f"  ✓ Product assigned to {len(assigned_collections)} collection(s)")
                        # Map collection IDs to names for display
                        collection_names = {
                            '299806818352': 'Round',
                            '299806785584': 'Polished',
                            '299806752816': 'Faceted',
                            '299806720048': 'Beads'
                        }
                        collection_list = [collection_names.get(cid, cid) for cid in assigned_collections]
                        print(f"    Collections: {', '.join(collection_list)}")
                    else:
                        print(f"  No collections matched for this product")
                else:
                    print(f"  ✗ Failed to create product '{title}'")
            
            if new_products_found == 0:
                print(f"\n✓ No new products found. All products are already in Shopify.")
            else:
                print(f"\n✓ Processed {new_products_found} new product(s)")
            
            processed_count += 1
            
            # If not running continuously, exit after one run
            if not continuous:
                print("\n" + "="*60)
                print("Product import completed!")
                break
            
            # If running continuously, wait before next check
            if continuous:
                print(f"\nWaiting {check_interval} seconds before next check...")
                print("(Press Ctrl+C to stop)")
                time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\n\nStopped by user. Exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\nError during processing: {e}")
            import traceback
            traceback.print_exc()
            
            if not continuous:
                break
            
            print(f"Waiting {check_interval} seconds before retry...")
            time.sleep(check_interval)

def main():
    """Main function - run once or continuously"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import products from Google Sheets to Shopify')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (default: runs continuously every 20 seconds)')
    parser.add_argument('--interval', '-i', type=int, default=20,
                       help='Check interval in seconds (default: 20 seconds)')
    
    args = parser.parse_args()
    
    # Default to continuous mode unless --once is specified
    continuous_mode = not args.once
    
    process_products(continuous=continuous_mode, check_interval=args.interval)

if __name__ == "__main__":
    main()

