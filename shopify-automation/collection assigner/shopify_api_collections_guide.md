# Shopify API - Creating Collections Guide

## ⚠️ Important Note
**As of October 2024**: Shopify is deprecating the REST Admin API. **GraphQL Admin API is now recommended** for all new integrations. REST API will become legacy after April 2025.

---

## 🔑 Step 1: Get API Credentials

### 1. Create a Custom App in Shopify Admin:
1. Go to **Shopify Admin → Apps → Develop apps for your store**
2. Click **"Create an app"**
3. Enter app name (e.g., "Collection Manager")
4. Click **"Create app"**

### 2. Configure API Scopes:
1. Go to **Configuration** tab
2. Click **"Configure"** under **Admin API integration**
3. Select these scopes:
   - `write_products` (to create collections)
   - `read_products` (to read products)
4. Click **"Save"**
5. Click **"Install app"**

### 3. Get Access Token:
1. Go to **API credentials** tab
2. Copy the **Admin API access token**
3. Also note your **Shop domain** (e.g., `your-store.myshopify.com`)

---

## 📡 Step 2: API Endpoints

### GraphQL Admin API (Recommended)
- **Endpoint**: `https://{shop-domain}/admin/api/2025-04/graphql.json`
- **Method**: POST
- **Headers**:
  - `X-Shopify-Access-Token`: Your access token
  - `Content-Type`: application/json

### REST Admin API (Legacy - Still Works)
- **Endpoint**: `https://{shop-domain}/admin/api/2025-04/custom_collections.json`
- **Method**: POST
- **Headers**:
  - `X-Shopify-Access-Token`: Your access token
  - `Content-Type`: application/json

---

## 🎯 Step 3: Create Collections

### Option A: Manual Collection (Custom Collection)

**Using GraphQL:**
```graphql
mutation {
  collectionCreate(input: {
    title: "Dog Treats & Chews"
    descriptionHtml: "<p>All natural dog treats and chews for your furry friend</p>"
  }) {
    collection {
      id
      title
      handle
    }
    userErrors {
      field
      message
    }
  }
}
```

**Using REST API:**
```json
POST https://{shop-domain}/admin/api/2025-04/custom_collections.json

{
  "custom_collection": {
    "title": "Dog Treats & Chews",
    "body_html": "<p>All natural dog treats and chews for your furry friend</p>"
  }
}
```

### Option B: Automated Collection (Smart Collection)

**Using GraphQL:**
```graphql
mutation {
  collectionCreate(input: {
    title: "Dog Treats & Chews"
    descriptionHtml: "<p>All natural dog treats and chews</p>"
    ruleSet: {
      appliedDisjunctively: true
      rules: [
        {
          column: TITLE
          relation: CONTAINS
          condition: "yak chews"
        }
        {
          column: TITLE
          relation: CONTAINS
          condition: "bully stick"
        }
        {
          column: TITLE
          relation: CONTAINS
          condition: "pig ears"
        }
        {
          column: TITLE
          relation: CONTAINS
          condition: "dog bone"
        }
      ]
    }
  }) {
    collection {
      id
      title
      handle
    }
    userErrors {
      field
      message
    }
  }
}
```

**Using REST API:**
```json
POST https://{shop-domain}/admin/api/2025-04/smart_collections.json

{
  "smart_collection": {
    "title": "Dog Treats & Chews",
    "body_html": "<p>All natural dog treats and chews</p>",
    "rules": [
      {
        "column": "title",
        "relation": "contains",
        "condition": "yak chews"
      },
      {
        "column": "title",
        "relation": "contains",
        "condition": "bully stick"
      },
      {
        "column": "title",
        "relation": "contains",
        "condition": "pig ears"
      },
      {
        "column": "title",
        "relation": "contains",
        "condition": "dog bone"
      }
    ],
    "disjunctive": true
  }
}
```

---

## 📋 Available Rule Columns (for Automated Collections)

- `TITLE` - Product title
- `TYPE` - Product type
- `VENDOR` - Product vendor
- `VARIANT_PRICE` - Variant price
- `TAG` - Product tags
- `PRODUCT_CATEGORY_ID` - Product category
- `VARIANT_INVENTORY` - Inventory quantity
- `VARIANT_WEIGHT` - Product weight

**Available Relations:**
- `EQUALS` - Exact match
- `NOT_EQUALS` - Not equal
- `GREATER_THAN` - Greater than
- `LESS_THAN` - Less than
- `STARTS_WITH` - Starts with
- `ENDS_WITH` - Ends with
- `CONTAINS` - Contains text
- `NOT_CONTAINS` - Does not contain

---

## 🔗 Step 4: Add Products to Manual Collections

After creating a manual collection, add products:

**Using GraphQL:**
```graphql
mutation {
  collectionAddProducts(collectionId: "gid://shopify/Collection/123456789", productIds: [
    "gid://shopify/Product/111111111",
    "gid://shopify/Product/222222222"
  ]) {
    collection {
      id
      title
    }
    userErrors {
      field
      message
    }
  }
}
```

**Using REST API:**
```json
POST https://{shop-domain}/admin/api/2025-04/collects.json

{
  "collect": {
    "product_id": 111111111,
    "collection_id": 123456789
  }
}
```

---

## 📤 Step 5: Publish Collection

Collections are created as **unpublished** by default. To make them visible:

**Using GraphQL:**
```graphql
mutation {
  publishablePublish(id: "gid://shopify/Collection/123456789", input: {
    publicationId: "gid://shopify/Publication/987654321"
  }) {
    publishable {
      id
    }
    userErrors {
      field
      message
    }
  }
}
```

**Note**: You need to get your publication ID first. Usually it's the default online store publication.

---

## 🚀 Quick Reference: Our Collections

Based on your `shopify_collections_suggestions.json`, here are the 3 collections to create:

### 1. Dog Treats & Chews (Automated)
- **Rule**: Title contains "yak chews" OR "bully stick" OR "pig ears" OR "dog bone" OR "chews"
- **Products**: 6 products

### 2. Dog Bowls (Automated)
- **Rule**: Title contains "bowl" OR "bowls"
- **Products**: 3 products

### 3. Dog Accessories (Automated)
- **Rule**: Title contains "collar" OR "raincoat"
- **Products**: 2 products

---

## ⚡ Rate Limits

- **GraphQL**: 50 points per second (cost varies by operation)
- **REST**: 2 requests per second (40 requests per app per store)

---

## 🔒 Security Best Practices

1. **Never commit API tokens** to version control
2. **Use environment variables** for credentials
3. **Store tokens securely** (use secrets management)
4. **Rotate tokens** periodically
5. **Use HTTPS** for all API calls

---

## 📚 Resources

- [Shopify GraphQL Admin API - Collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)
- [Shopify REST Admin API - Collections](https://shopify.dev/docs/api/admin-rest/2025-04/resources/customcollection)
- [CollectionCreate Mutation](https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate)

