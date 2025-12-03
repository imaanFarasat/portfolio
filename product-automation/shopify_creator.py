import base64
import io
import re
import requests
from openai import OpenAI
from config import Config

class ShopifyProductCreator:
    def __init__(self):
        self.shop_url = Config.SHOPIFY_SHOP_URL
        self.api_token = Config.SHOPIFY_ACCESS_TOKEN
        self.api_version = Config.SHOPIFY_API_VERSION
        self.base_url = f"https://{self.shop_url}/admin/api/{self.api_version}"
        
        # Initialize OpenAI if API key is provided
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                print("✓ OpenAI initialized for product descriptions")
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
            print("Warning: OPENAI_API_KEY not set. Product descriptions will not be generated.")
    
    def upload_image_to_shopify(self, image_content, filename):
        """Upload image to Shopify and return the base64 encoded string"""
        try:
            # Create a file-like object from the image content
            if isinstance(image_content, io.BytesIO):
                # Reset position to start
                image_content.seek(0)
                image_data = image_content.read()
                # Verify we got actual data
                if not image_data or len(image_data) == 0:
                    print(f"  Warning: Empty image data for {filename}")
                    return None
            else:
                image_data = image_content
            
            # Verify image data is valid (check for common image file signatures)
            if len(image_data) < 10:
                print(f"  Warning: Image data too small for {filename} ({len(image_data)} bytes)")
                return None
            
            # Debug: Print file size
            file_size_mb = len(image_data) / (1024 * 1024)
            if file_size_mb > 20:
                print(f"  Warning: Image {filename} is {file_size_mb:.2f}MB (Shopify limit is 20MB)")
            
            # Check for JPEG signature (FF D8 FF or FF D8 E0/FF D8 E1 for JPEG)
            is_jpeg = (image_data[0:2] == b'\xff\xd8' and 
                      (image_data[2] == 0xff or image_data[2] == 0xe0 or image_data[2] == 0xe1))
            # Check for PNG signature (89 50 4E 47 0D 0A 1A 0A)
            is_png = image_data[0:8] == b'\x89PNG\r\n\x1a\n'
            # Check for HEIC/HEIF format (common on iPhones, often misnamed as .JPEG)
            # HEIC files start with various signatures, common ones:
            is_heic = (image_data[4:8] == b'ftyp' and 
                      (b'heic' in image_data[8:16] or b'heif' in image_data[8:16] or 
                       b'mif1' in image_data[8:16]))
            
            if is_heic:
                print(f"  ERROR: {filename} appears to be HEIC/HEIF format (iPhone format), not JPEG!")
                print(f"  Shopify does not support HEIC format. Please convert images to JPEG/PNG first.")
                return None
            
            # Determine content type based on file signature or extension
            if is_jpeg:
                content_type = 'image/jpeg'
            elif is_png:
                content_type = 'image/png'
            elif filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif filename.lower().endswith('.webp'):
                content_type = 'image/webp'
            else:
                # Default to JPEG
                content_type = 'image/jpeg'
            
            # Verify the file signature matches the extension
            if filename.upper().endswith('.JPEG') or filename.upper().endswith('.JPG'):
                if not is_jpeg:
                    print(f"  Warning: {filename} has .JPEG extension but doesn't have JPEG signature. First bytes: {image_data[0:10].hex()}")
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Shopify expects data URL format: data:[<mediatype>][;base64],<data>
            # But sometimes it's picky about the format, so let's ensure it's exactly right
            image_data_url = f"data:{content_type};base64,{image_base64}"
            
            # Debug: Save first image locally for testing
            # This helps verify if the image downloaded correctly from Google Drive
            if filename == 'IMG_2623.JPEG':  # Test with first image
                try:
                    with open('debug_test_image.jpg', 'wb') as f:
                        f.write(image_data)
                    print(f"  Debug: Saved {filename} locally as debug_test_image.jpg for verification")
                except Exception as e:
                    print(f"  Debug: Could not save test image: {e}")
            
            return image_data_url
        except Exception as e:
            print(f"  Error preparing image {filename}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_product_description(self, title, max_retries=3):
        """Generate product description using OpenAI with retry logic for rate limits"""
        if not self.openai_client:
            return None
        
        import time
        
        prompt = f"""Write a detailed product description for a gemstone bead product titled "{title}".

IMPORTANT REQUIREMENTS:
- Do NOT include the product title in the description (it's already shown separately)
- Do NOT use <h1> tags
- START with <h2>Product Specification</h2> section at the TOP (this is the most important part)
- After the Product Specification section, include an engaging introduction paragraph about the gemstone using <p> tags
- Use <p> tags with bullet points (•) to list key features and specifications in the Product Specification section
- Include exactly ONE <h2> tag with the text "Product Specification" (no other H2 tags)
- Be informative, professional, and highlight the beauty and quality of the gemstone
- Include information about the gemstone's properties, uses, and care instructions AFTER the Product Specification section

STRUCTURE:
1. <h2>Product Specification</h2> with bullet points (•) in <p> tags
2. Then introduction and other content

Format the response as pure HTML (no markdown code blocks, no ```html tags). Return only the HTML content."""
        
        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # Using gpt-4o-mini (cheaper) or use "gpt-4" for better quality
                    messages=[
                        {"role": "system", "content": "You are a professional product description writer for gemstone jewelry."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                description = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present (```html or ```)
                if description.startswith('```'):
                    # Find the first newline after ```
                    lines = description.split('\n')
                    if lines[0].startswith('```'):
                        # Remove first line (```html or ```)
                        lines = lines[1:]
                    # Remove last line if it's just ```
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]
                    description = '\n'.join(lines).strip()
                
                # Remove any H1 tags (product title shouldn't be in description)
                description = re.sub(r'<h1>.*?</h1>', '', description, flags=re.IGNORECASE | re.DOTALL)
                
                # Extract Product Specification section and place it at the top
                # Find Product Specification H2 tag (case-insensitive)
                spec_h2_pattern = r'<h2[^>]*>.*?Product Specification.*?</h2>'
                spec_h2_match = re.search(spec_h2_pattern, description, re.IGNORECASE | re.DOTALL)
                
                if spec_h2_match:
                    # Found Product Specification H2 tag
                    spec_h2_start = spec_h2_match.start()
                    spec_h2_end = spec_h2_match.end()
                    
                    # Get everything after the H2 tag
                    content_after_h2 = description[spec_h2_end:]
                    
                    # Find the next H2 tag (if any) to know where Product Specification section ends
                    next_h2_match = re.search(r'<h2[^>]*>', content_after_h2, re.IGNORECASE)
                    
                    if next_h2_match:
                        # There's another H2 after Product Specification - extract until that point
                        spec_content_end = spec_h2_end + next_h2_match.start()
                        product_spec_section = description[spec_h2_start:spec_content_end].strip()
                        rest_of_description = (description[:spec_h2_start].strip() + '\n\n' + description[spec_content_end:].strip()).strip()
                    else:
                        # Product Specification is at the end - extract everything from H2 to end
                        product_spec_section = description[spec_h2_start:].strip()
                        rest_of_description = description[:spec_h2_start].strip()
                    
                    # Reconstruct with Product Specification at top
                    if rest_of_description:
                        description = f'{product_spec_section}\n\n{rest_of_description}'.strip()
                    else:
                        description = product_spec_section
                else:
                    # Product Specification not found, add it at the top
                    product_spec_section = '<h2>Product Specification</h2>\n<p>• High-quality gemstone beads\n• Carefully selected and polished\n• Perfect for jewelry making\n• Available in multiple sizes</p>'
                    description = f'{product_spec_section}\n\n{description}'.strip()
                
                # Remove any other H2 tags (shouldn't be any, but just in case)
                description = re.sub(r'<h2[^>]*>(?!Product Specification).*?</h2>', '', description, flags=re.IGNORECASE | re.DOTALL)
                
                # Clean up extra whitespace
                description = re.sub(r'\n{3,}', '\n\n', description).strip()
                
                print(f"  ✓ Generated description successfully ({len(description)} characters)")
                return description
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error
                if '429' in error_str or 'rate limit' in error_str.lower() or 'quota' in error_str.lower():
                    retry_delay = 60  # Default 60 seconds for OpenAI
                    
                    if attempt < max_retries - 1:
                        print(f"  Rate limit hit. Waiting {retry_delay} seconds before retry ({attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"  Warning: Rate limit exceeded after {max_retries} attempts.")
                        raise Exception("RATE_LIMIT_EXCEEDED")
                else:
                    # Other errors - don't retry
                    print(f"  Warning: Could not generate product description: {e}")
                    if attempt == 0:  # Only show full traceback on first attempt
                        import traceback
                        traceback.print_exc()
                    return None
        
        return None
    
    def generate_meta_title_and_description(self, title, max_retries=3):
        """Generate SEO meta title and description using OpenAI"""
        if not self.openai_client:
            # Fallback: create simple meta title and description from product title
            meta_title = title[:70] if len(title) <= 70 else title[:67] + "..."
            meta_description = f"Shop {title} - High-quality gemstone beads perfect for jewelry making. Available in multiple sizes."[:160]
            return meta_title, meta_description
        
        import time
        
        prompt = f"""Generate SEO-optimized meta title and meta description for a gemstone bead product titled "{title}".

CRITICAL REQUIREMENTS:
- Meta title: EXACTLY 70 characters or less (including spaces). Create a compelling, SEO-optimized title that includes the gemstone name and key terms like "beads", "jewelry", etc. Do NOT just copy the product title - create an optimized version.
- Meta description: EXACTLY 160 characters or less (including spaces). Write an engaging description that highlights benefits, includes a call-to-action, and encourages clicks. Include relevant keywords naturally.

IMPORTANT:
- Count characters carefully - these limits are strict
- Make them unique and SEO-friendly
- Include the gemstone name and product type
- Use action words and benefits

Format your response EXACTLY like this (no extra text):
META_TITLE: [your optimized meta title, exactly 70 chars or less]
META_DESCRIPTION: [your engaging meta description, exactly 160 chars or less]"""
        
        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an SEO expert specializing in e-commerce product descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                
                result = response.choices[0].message.content.strip()
                
                # Parse the response
                meta_title = None
                meta_description = None
                
                lines = result.split('\n')
                for line in lines:
                    if line.startswith('META_TITLE:'):
                        meta_title = line.replace('META_TITLE:', '').strip()
                    elif line.startswith('META_DESCRIPTION:'):
                        meta_description = line.replace('META_DESCRIPTION:', '').strip()
                
                # Validate and enforce strict character limits
                if meta_title:
                    # Strictly enforce 70 character limit
                    if len(meta_title) > 70:
                        # Truncate at word boundary if possible
                        truncated = meta_title[:67]
                        last_space = truncated.rfind(' ')
                        if last_space > 50:  # Only truncate at word if we have enough content
                            meta_title = truncated[:last_space] + "..."
                        else:
                            meta_title = truncated + "..."
                    # Ensure it's exactly 70 or less
                    meta_title = meta_title[:70]
                else:
                    # Fallback: create from title but optimize it
                    meta_title = title[:70] if len(title) <= 70 else title[:67] + "..."
                
                if meta_description:
                    # Strictly enforce 160 character limit
                    if len(meta_description) > 160:
                        # Truncate at word boundary if possible
                        truncated = meta_description[:157]
                        last_space = truncated.rfind(' ')
                        if last_space > 120:  # Only truncate at word if we have enough content
                            meta_description = truncated[:last_space] + "..."
                        else:
                            meta_description = truncated + "..."
                    # Ensure it's exactly 160 or less
                    meta_description = meta_description[:160]
                else:
                    # Fallback: create optimized description
                    meta_description = f"Shop {title} - High-quality gemstone beads perfect for jewelry making. Available in multiple sizes."[:160]
                
                print(f"  ✓ Generated meta title ({len(meta_title)} chars) and meta description ({len(meta_description)} chars)")
                return meta_title, meta_description
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error
                if '429' in error_str or 'rate limit' in error_str.lower() or 'quota' in error_str.lower():
                    retry_delay = 60
                    
                    if attempt < max_retries - 1:
                        print(f"  Rate limit hit for meta generation. Waiting {retry_delay} seconds before retry ({attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"  Warning: Rate limit exceeded for meta generation. Using fallback.")
                        break
                else:
                    # Other errors - use fallback
                    print(f"  Warning: Could not generate meta tags: {e}")
                    if attempt == 0:
                        import traceback
                        traceback.print_exc()
                    break
        
        # Fallback: create simple meta title and description from product title
        meta_title = title[:70] if len(title) <= 70 else title[:67] + "..."
        meta_description = f"Shop {title} - High-quality gemstone beads perfect for jewelry making. Available in multiple sizes."[:160]
        return meta_title, meta_description
    
    def create_product(self, title, variants, images):
        """Create a product in Shopify with variants and images"""
        try:
            # Generate product description using OpenAI
            description = None
            if self.openai_client:
                print(f"  Generating product description using AI...")
                description = self.generate_product_description(title)
                if description:
                    print(f"  ✓ Product description generated")
                else:
                    print(f"  Warning: Could not generate description, creating product without it")
            
            # Generate meta title and description
            print(f"  Generating SEO meta title and description...")
            meta_title, meta_description = self.generate_meta_title_and_description(title)
            
            # Prepare product data
            product_data = {
                "product": {
                    "title": title,
                    "product_type": "Gemstone Beads",
                    "variants": [],
                    "options": [
                        {
                            "name": "Size",
                            "values": [v['size'] for v in variants]
                        }
                    ]
                }
            }
            
            # Note: Meta title and description will be added after product creation
            # Store them for later use
            self._pending_meta_title = meta_title
            self._pending_meta_description = meta_description
            
            # Add description if generated
            if description:
                product_data["product"]["body_html"] = description
            
            # Add variants
            for variant_data in variants:
                product_data["product"]["variants"].append({
                    "option1": variant_data['size'],
                    "price": str(variant_data['price']),
                    "inventory_management": "shopify",
                    "inventory_quantity": 0
                })
            
            # Create product using REST API
            headers = {
                "X-Shopify-Access-Token": self.api_token,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/products.json",
                json=product_data,
                headers=headers
            )
            
            if response.status_code == 201:
                product = response.json()["product"]
                product_id = product["id"]
                print(f"Product '{title}' created successfully with ID: {product_id}")
                
                # Add images using multipart/form-data (same as upload_images_to_product)
                if images:
                    for idx, image_data in enumerate(images):
                        try:
                            # Reset the BytesIO object to the beginning
                            image_data['content'].seek(0)
                            
                            # Determine content type from filename
                            content_type = 'image/jpeg'
                            if image_data['name'].lower().endswith('.png'):
                                content_type = 'image/png'
                            elif image_data['name'].lower().endswith('.gif'):
                                content_type = 'image/gif'
                            elif image_data['name'].lower().endswith('.webp'):
                                content_type = 'image/webp'
                            
                            # Prepare multipart/form-data upload
                            files = {
                                'image[attachment]': (image_data['name'], image_data['content'], content_type)
                            }
                            data = {
                                'image[position]': str(idx + 1)
                            }
                            
                            # Use multipart/form-data headers
                            multipart_headers = {
                                "X-Shopify-Access-Token": self.api_token
                            }
                            
                            image_response = requests.post(
                                f"{self.base_url}/products/{product_id}/images.json",
                                files=files,
                                data=data,
                                headers=multipart_headers,
                                timeout=60
                            )
                            
                            if image_response.status_code == 201:
                                print(f"  ✓ Image '{image_data['name']}' uploaded successfully")
                            else:
                                error_msg = image_response.text
                                # Check if response contains image data (sometimes Shopify returns 200 instead of 201)
                                try:
                                    response_json = image_response.json()
                                    if 'image' in response_json and 'id' in response_json['image']:
                                        print(f"  ✓ Image '{image_data['name']}' uploaded successfully (status {image_response.status_code})")
                                    else:
                                        print(f"  ✗ Failed to upload image '{image_data['name']}': {error_msg}")
                                except:
                                    print(f"  ✗ Failed to upload image '{image_data['name']}': {error_msg}")
                        except Exception as e:
                            print(f"Error uploading image '{image_data['name']}': {e}")
                
                # Add meta title and description using metafields API
                if hasattr(self, '_pending_meta_title'):
                    self.update_product_meta_fields(product_id, self._pending_meta_title, self._pending_meta_description)
                    delattr(self, '_pending_meta_title')
                    delattr(self, '_pending_meta_description')
                
                return product_id
            else:
                print(f"Failed to create product '{title}': {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating product '{title}': {e}")
            return None
    
    def get_product_by_title(self, title):
        """Get product ID and data if a product with the given title exists"""
        try:
            headers = {
                "X-Shopify-Access-Token": self.api_token,
                "Content-Type": "application/json"
            }
            
            # Search for products - Shopify API doesn't support title filter directly
            # We'll search and filter client-side
            # Limit to 250 products per page (Shopify's max)
            response = requests.get(
                f"{self.base_url}/products.json?limit=250",
                headers=headers
            )
            
            if response.status_code == 200:
                products = response.json().get("products", [])
                for product in products:
                    if product.get("title") == title:
                        body_html = product.get("body_html") or ""
                        body_html_clean = body_html.strip() if body_html else ""
                        # Consider it has a description if it's at least 50 characters (to avoid empty/minimal descriptions)
                        has_description = len(body_html_clean) >= 50
                        return {
                            "id": product.get("id"),
                            "body_html": body_html,
                            "has_description": has_description
                        }
                
                # If we got 250 products, there might be more pages
                # For now, we'll just check the first page
                # In production, you might want to paginate through all products
            return None
        except Exception as e:
            print(f"Error checking if product exists: {e}")
            return None
    
    def update_product_meta_fields(self, product_id, meta_title, meta_description):
        """Update product meta title and description using Shopify metafields API"""
        try:
            headers = {
                "X-Shopify-Access-Token": self.api_token,
                "Content-Type": "application/json"
            }
            
            # Shopify uses metafields for SEO meta tags
            # First, try to get existing metafields to see if they exist
            metafields_response = requests.get(
                f"{self.base_url}/products/{product_id}/metafields.json",
                headers=headers
            )
            
            existing_metafields = {}
            if metafields_response.status_code == 200:
                metafields = metafields_response.json().get("metafields", [])
                for mf in metafields:
                    if mf.get("namespace") == "global":
                        if mf.get("key") == "title_tag":
                            existing_metafields["title_tag_id"] = mf.get("id")
                        elif mf.get("key") == "description_tag":
                            existing_metafields["description_tag_id"] = mf.get("id")
            
            # Update or create meta title
            if "title_tag_id" in existing_metafields:
                # Update existing
                payload = {
                    "metafield": {
                        "id": existing_metafields["title_tag_id"],
                        "value": meta_title
                    }
                }
                requests.put(
                    f"{self.base_url}/metafields/{existing_metafields['title_tag_id']}.json",
                    json=payload,
                    headers=headers
                )
            else:
                # Create new
                payload = {
                    "metafield": {
                        "namespace": "global",
                        "key": "title_tag",
                        "value": meta_title,
                        "type": "single_line_text_field"
                    }
                }
                requests.post(
                    f"{self.base_url}/products/{product_id}/metafields.json",
                    json=payload,
                    headers=headers
                )
            
            # Update or create meta description
            if "description_tag_id" in existing_metafields:
                # Update existing
                payload = {
                    "metafield": {
                        "id": existing_metafields["description_tag_id"],
                        "value": meta_description
                    }
                }
                requests.put(
                    f"{self.base_url}/metafields/{existing_metafields['description_tag_id']}.json",
                    json=payload,
                    headers=headers
                )
            else:
                # Create new
                payload = {
                    "metafield": {
                        "namespace": "global",
                        "key": "description_tag",
                        "value": meta_description,
                        "type": "single_line_text_field"
                    }
                }
                requests.post(
                    f"{self.base_url}/products/{product_id}/metafields.json",
                    json=payload,
                    headers=headers
                )
            
            print(f"  ✓ Meta title and description added successfully")
            return True
        except Exception as e:
            print(f"  Warning: Could not update meta fields: {e}")
            return False
    
    def update_product_description(self, product_id, description):
        """Update product description in Shopify"""
        try:
            headers = {
                "X-Shopify-Access-Token": self.api_token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "product": {
                    "id": product_id,
                    "body_html": description
                }
            }
            
            response = requests.put(
                f"{self.base_url}/products/{product_id}.json",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                # Verify the description was actually saved
                try:
                    updated_product = response.json().get("product", {})
                    saved_description = updated_product.get("body_html", "")
                    if saved_description and len(saved_description) > 10:
                        print(f"  ✓ Description saved successfully ({len(saved_description)} characters)")
                        return True
                    else:
                        print(f"  Warning: Description appears empty after save")
                        return False
                except:
                    return True  # Assume success if we can't verify
            else:
                print(f"  ✗ Failed to update description. Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"  ✗ Error updating product description: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def product_exists(self, title):
        """Check if a product with the given title already exists"""
        product_data = self.get_product_by_title(title)
        return product_data is not None
    
    def assign_product_to_collections(self, product_id, title):
        """Assign product to collections based on keywords in title"""
        collections_to_assign = []
        
        # Check for keywords and assign to corresponding collections
        title_lower = title.lower()
        
        if 'round' in title_lower:
            collections_to_assign.append('299806818352')
        if 'polished' in title_lower:
            collections_to_assign.append('299806785584')
        if 'faceted' in title_lower:
            collections_to_assign.append('299806752816')
        if 'beads' in title_lower:
            collections_to_assign.append('299806720048')
        
        if not collections_to_assign:
            return []
        
        headers = {
            "X-Shopify-Access-Token": self.api_token,
            "Content-Type": "application/json"
        }
        
        assigned_collections = []
        
        for collection_id in collections_to_assign:
            try:
                # Add product to collection
                payload = {
                    "collect": {
                        "product_id": product_id,
                        "collection_id": collection_id
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/collects.json",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    assigned_collections.append(collection_id)
                else:
                    # Check if product is already in collection (that's okay)
                    if response.status_code == 422:
                        try:
                            error_data = response.json()
                            if 'errors' in error_data and 'collection_id' in error_data['errors']:
                                # Product already in collection
                                assigned_collections.append(collection_id)
                            else:
                                print(f"  Warning: Could not add product to collection {collection_id}: {response.text}")
                        except:
                            print(f"  Warning: Could not add product to collection {collection_id}: {response.text}")
                    else:
                        print(f"  Warning: Could not add product to collection {collection_id}: {response.text}")
            except Exception as e:
                print(f"  Error assigning to collection {collection_id}: {e}")
        
        return assigned_collections
    
    def upload_images_to_product(self, product_id, images):
        """Upload images to an existing product"""
        if not images:
            return []
        
        headers = {
            "X-Shopify-Access-Token": self.api_token,
            "Content-Type": "application/json"
        }
        
        uploaded_count = 0
        failed_count = 0
        
        for idx, image_data in enumerate(images):
            try:
                # Use multipart/form-data upload (more reliable than base64)
                # Reset the BytesIO object to the beginning
                image_data['content'].seek(0)
                
                # Determine content type from filename
                content_type = 'image/jpeg'
                if image_data['name'].lower().endswith('.png'):
                    content_type = 'image/png'
                elif image_data['name'].lower().endswith('.gif'):
                    content_type = 'image/gif'
                elif image_data['name'].lower().endswith('.webp'):
                    content_type = 'image/webp'
                
                # Prepare multipart/form-data upload
                files = {
                    'image[attachment]': (image_data['name'], image_data['content'], content_type)
                }
                data = {
                    'image[position]': str(idx + 1)
                }
                
                # Use multipart/form-data headers (don't set Content-Type - requests will set it with boundary)
                multipart_headers = {
                    "X-Shopify-Access-Token": self.api_token
                }
                
                image_response = requests.post(
                    f"{self.base_url}/products/{product_id}/images.json",
                    files=files,
                    data=data,
                    headers=multipart_headers,
                    timeout=60  # Increase timeout for large images
                )
                
                # Check if upload was successful (201 Created or 200 OK with image data)
                is_success = False
                if image_response.status_code in [200, 201]:
                    try:
                        response_json = image_response.json()
                        # Success if response contains image data with an ID
                        if 'image' in response_json and 'id' in response_json['image']:
                            is_success = True
                            print(f"  ✓ Image '{image_data['name']}' uploaded successfully (ID: {response_json['image']['id']})")
                            uploaded_count += 1
                    except:
                        # If we can't parse JSON, check status code
                        if image_response.status_code == 201:
                            is_success = True
                            print(f"  ✓ Image '{image_data['name']}' uploaded successfully")
                            uploaded_count += 1
                
                if not is_success:
                    error_msg = image_response.text
                    # Check if it's a size issue
                    if "too large" in error_msg.lower() or "size" in error_msg.lower():
                        print(f"  ✗ Image '{image_data['name']}' might be too large. Error: {error_msg}")
                    else:
                        print(f"  ✗ Failed to upload image '{image_data['name']}': {error_msg}")
                    failed_count += 1
            except Exception as e:
                print(f"  Error uploading image '{image_data['name']}': {e}")
                import traceback
                traceback.print_exc()
                failed_count += 1
        
        return uploaded_count, failed_count

