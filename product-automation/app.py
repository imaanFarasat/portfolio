from flask import Flask, request, jsonify
from google_sheets_reader import GoogleSheetsReader
from google_drive_reader import GoogleDriveReader
from shopify_creator import ShopifyProductCreator
from config import Config
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for triggering product import"""
    # Verify webhook secret if configured
    if Config.WEBHOOK_SECRET:
        secret = request.headers.get('X-Webhook-Secret')
        if secret != Config.WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Initialize readers and creator
        sheets_reader = GoogleSheetsReader(Config.GOOGLE_CREDENTIALS_FILE)
        drive_reader = GoogleDriveReader(Config.GOOGLE_CREDENTIALS_FILE)
        shopify_creator = ShopifyProductCreator()
        
        # Read products from Google Sheet
        products = sheets_reader.parse_products(Config.GOOGLE_SHEETS_ID)
        
        results = {
            "total_products": len(products),
            "created": [],
            "skipped": [],
            "failed": []
        }
        
        # Process each product
        for row_number, product_data in products.items():
            title = product_data['title']
            variants = product_data['variants']
            
            # Check if product already exists
            if shopify_creator.product_exists(title):
                results["skipped"].append({
                    "title": title,
                    "reason": "Product already exists"
                })
                continue
            
            # Get images from Google Drive
            images = drive_reader.get_images_for_product(
                Config.GOOGLE_DRIVE_FOLDER_ID,
                row_number
            )
            
            # Create product in Shopify
            product_id = shopify_creator.create_product(title, variants, images)
            
            if product_id:
                results["created"].append({
                    "title": title,
                    "product_id": product_id,
                    "variants_count": len(variants),
                    "images_count": len(images)
                })
            else:
                results["failed"].append({
                    "title": title,
                    "reason": "Failed to create product"
                })
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sync', methods=['POST'])
def sync():
    """Manual sync endpoint (same as webhook but can be called directly)"""
    return webhook()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

