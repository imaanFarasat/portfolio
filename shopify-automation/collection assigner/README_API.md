# Shopify Collections API - Quick Start

## 📋 Files Overview

- **`create_collections_api.py`** - GraphQL API version (recommended)
- **`create_collections_rest.py`** - REST API version (simpler, legacy)
- **`shopify_api_collections_guide.md`** - Detailed API documentation
- **`shopify_collections_suggestions.json`** - Collection configurations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Set Up Credentials

**Option A: Environment Variables (Recommended)**
```bash
# Windows PowerShell
$env:SHOPIFY_SHOP_DOMAIN="your-store.myshopify.com"
$env:SHOPIFY_ACCESS_TOKEN="your-access-token-here"

# Linux/Mac
export SHOPIFY_SHOP_DOMAIN="your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="your-access-token-here"
```

**Option B: Edit Script Directly**
Edit the script and update:
```python
SHOP_DOMAIN = 'your-store.myshopify.com'
ACCESS_TOKEN = 'your-access-token-here'
```

### 3. Get Shopify API Credentials

1. Go to **Shopify Admin → Apps → Develop apps**
2. Click **"Create an app"**
3. Configure **Admin API integration** with scopes:
   - `write_products`
   - `read_products`
4. Install the app
5. Copy the **Admin API access token**

### 4. Run the Script

**Using GraphQL (Recommended):**
```bash
python create_collections_api.py
```

**Using REST API (Simpler):**
```bash
python create_collections_rest.py
```

## 📝 What the Script Does

1. Reads `shopify_collections_suggestions.json`
2. Creates 3 collections:
   - Dog Treats & Chews (automated)
   - Dog Bowls (automated)
   - Dog Accessories (automated)
3. Saves created collection IDs to `created_collections.json`

## 🔍 Verify Collections

After running, check your Shopify admin:
- **Products → Collections**
- You should see 3 new collections

## ⚠️ Troubleshooting

### Error: "Invalid API key"
- Check your access token is correct
- Ensure the app is installed
- Verify API scopes include `write_products`

### Error: "Collection already exists"
- Collections with the same title already exist
- Either delete existing collections or rename in JSON

### Error: "Rate limit exceeded"
- Wait a few seconds and try again
- REST API: 2 requests/second
- GraphQL: 50 points/second

## 📚 Next Steps

- **Add products manually**: Use Shopify admin or API
- **Publish collections**: Collections are created as unpublished
- **Customize rules**: Edit conditions in `shopify_collections_suggestions.json`

## 🔗 Resources

- [Shopify GraphQL Admin API](https://shopify.dev/docs/api/admin-graphql)
- [Shopify REST Admin API](https://shopify.dev/docs/api/admin-rest)
- [API Rate Limits](https://shopify.dev/docs/api/usage/rate-limits)

