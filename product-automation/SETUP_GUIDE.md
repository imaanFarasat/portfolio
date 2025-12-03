# Complete Setup Guide - Getting All Required Values

This guide will walk you through getting each required value for your `.env` file.

## 1. GOOGLE_SHEETS_ID

**What it is:** The unique identifier for your Google Sheet

**How to get it:**
1. Open your Google Sheet in a web browser
2. Look at the URL in your address bar
3. The URL will look like: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`
4. Copy the long string between `/d/` and `/edit`
   - Example: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
5. This is your `GOOGLE_SHEETS_ID`

**Example:**
```
GOOGLE_SHEETS_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

---

## 2. GOOGLE_DRIVE_FOLDER_ID

**What it is:** The unique identifier for the parent folder in Google Drive where your product image folders are stored

**How to get it:**
1. Open Google Drive in your web browser
2. Navigate to the parent folder that contains your numbered folders (2, 6, etc.)
3. Click on the folder to open it
4. Look at the URL in your address bar
5. The URL will look like: `https://drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
6. Copy the long string after `/folders/`
   - Example: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
7. This is your `GOOGLE_DRIVE_FOLDER_ID`

**Important:** This should be the PARENT folder that contains folders named "2", "6", etc. (the row numbers)

**Example:**
```
GOOGLE_DRIVE_FOLDER_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

---

## 3. GOOGLE_CREDENTIALS_FILE (credentials.json)

**What it is:** A JSON file containing your Google API credentials for authentication

**How to get it:**

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Product Automation")
5. Click "Create"

### Step 2: Enable Required APIs
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API" and click on it
3. Click "Enable"
4. Go back to the Library
5. Search for "Google Drive API" and click on it
6. Click "Enable"

### Step 3: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace account)
   - Fill in the required fields (App name, User support email, Developer contact email)
   - Click "Save and Continue" through the steps
   - Click "Back to Dashboard" when done
4. Back at "Create OAuth client ID":
   - Application type: Choose "Desktop app"
   - Name: Enter a name (e.g., "Product Automation Client")
   - Click "Create"
5. A popup will appear with your credentials
6. Click "Download JSON"
7. Save the file as `credentials.json` in your project folder (`F:\Iman\Portfolio\product-automation\`)

**Example:**
```
GOOGLE_CREDENTIALS_FILE=credentials.json
```

**Note:** The file should be in the same folder as your Python scripts.

---

## 4. SHOPIFY_SHOP_URL

**What it is:** Your Shopify store's URL (without https://)

**How to get it:**
1. Log in to your Shopify admin panel
2. Look at the URL in your browser
3. It will look like: `https://your-shop-name.myshopify.com/admin`
4. Copy just the shop part: `your-shop-name.myshopify.com`
5. This is your `SHOPIFY_SHOP_URL`

**Example:**
```
SHOPIFY_SHOP_URL=my-gemstone-store.myshopify.com
```

**Note:** Don't include `https://` or `/admin` - just the shop domain.

---

## 5. SHOPIFY_ACCESS_TOKEN

**What it is:** An API access token that allows the script to create products in your Shopify store

**How to get it:**

### Option A: Using Custom App (Recommended)
1. Log in to your Shopify admin panel
2. Go to "Settings" (bottom left)
3. Click "Apps and sales channels"
4. Click "Develop apps" (or "Manage private apps" if you see it)
5. Click "Create an app"
6. Enter an app name (e.g., "Product Automation")
7. Click "Create app"
8. Click "Configure Admin API scopes"
9. Under "Admin API integration scopes", enable:
   - `read_products`
   - `write_products`
   - `read_product_listings`
   - `write_product_listings`
10. Click "Save"
11. Click "Install app"
12. Click "Install" to confirm
13. After installation, you'll see "API credentials"
14. Under "Admin API access token", click "Reveal token once"
15. Copy the token (it's a long string starting with `shpat_...`)
16. This is your `SHOPIFY_ACCESS_TOKEN`

**Example:**
```
SHOPIFY_ACCESS_TOKEN=shpat_1234567890abcdefghijklmnopqrstuvwxyz
```

**Important:** Keep this token secret! Don't share it or commit it to public repositories.

---

## 6. SHOPIFY_API_VERSION

**What it is:** The version of Shopify's API to use

**How to get it:**
- This is just a version number
- Use the latest stable version: `2024-01` or `2024-04` or `2024-07` or `2024-10`
- Check [Shopify API Versioning](https://shopify.dev/api/usage/versioning) for the latest version
- As of 2024, `2024-01` is a safe choice

**Example:**
```
SHOPIFY_API_VERSION=2024-01
```

---

## 7. WEBHOOK_SECRET (Optional - for Railway)

**What it is:** A secret key to protect your webhook endpoint (only needed if deploying to Railway)

**How to get it:**
- Generate any random string (at least 32 characters)
- You can use an online generator or create one yourself
- Example: `my-super-secret-webhook-key-12345`

**Example:**
```
WEBHOOK_SECRET=my-super-secret-webhook-key-12345
```

---

## Final .env File Example

Create a file named `.env` in your project root (`F:\Iman\Portfolio\product-automation\.env`) with all values:

```env
# Google API Credentials
GOOGLE_SHEETS_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_DRIVE_FOLDER_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_CREDENTIALS_FILE=credentials.json

# Shopify Credentials
SHOPIFY_SHOP_URL=my-gemstone-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_1234567890abcdefghijklmnopqrstuvwxyz
SHOPIFY_API_VERSION=2024-01

# Webhook (for Railway - optional)
WEBHOOK_SECRET=my-super-secret-webhook-key-12345
```

**Important Notes:**
- Replace all example values with your actual values
- Don't use quotes around the values
- Make sure `credentials.json` is in the same folder as your Python scripts
- Never commit `.env` or `credentials.json` to version control (they're already in `.gitignore`)

---

## Quick Checklist

- [ ] Got GOOGLE_SHEETS_ID from Google Sheet URL
- [ ] Got GOOGLE_DRIVE_FOLDER_ID from Google Drive folder URL
- [ ] Created Google Cloud project
- [ ] Enabled Google Sheets API and Google Drive API
- [ ] Created OAuth credentials and downloaded credentials.json
- [ ] Got SHOPIFY_SHOP_URL from Shopify admin
- [ ] Created Shopify custom app and got access token
- [ ] Created .env file with all values
- [ ] Placed credentials.json in project folder

Once you have all these, you're ready to run the script!

