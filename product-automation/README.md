# Product Automation - Google Sheets to Shopify

This project automates the process of importing products from Google Sheets to Shopify. It reads product data from a Google Sheet, fetches images from Google Drive folders, and creates products in Shopify with variants.

## Features

- Reads products from Google Sheets with automatic variant detection
- Fetches product images from Google Drive folders (named by row number)
- Creates Shopify products with size and price variants
- **Auto-generates product descriptions using OpenAI** (optional)
- Automatically assigns products to collections based on keywords (Round, Polished, Faceted, Beads)
- Continuous monitoring mode - checks for new products every 20 seconds
- Supports both local execution and Railway deployment as a webhook

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON file
   - Save it as `credentials.json` in the project root

### 3. OpenAI Setup (Optional)

If you want automatic product descriptions generated:

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the API key (starts with `sk-...`)
5. Add it to your `.env` file as `OPENAI_API_KEY`

**Note:** This is optional. If you don't provide an OpenAI API key, products will be created without descriptions. OpenAI uses a pay-as-you-go model (very affordable, ~$0.15 per 1M tokens).

### 4. Shopify Setup

1. Go to your Shopify admin panel
2. Create a private app or use an existing one
3. Enable the following permissions:
   - Read and write products
   - Read and write product images
4. Copy your Shopify shop URL and access token

### 5. Environment Variables

Create a `.env` file in the project root:

```env
# Google API Credentials
GOOGLE_SHEETS_ID=your_google_sheet_id_here
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_parent_folder_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json

# Shopify Credentials
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token_here
SHOPIFY_API_VERSION=2024-01

# Webhook (for Railway)
WEBHOOK_SECRET=your_webhook_secret_here

# OpenAI (Optional - for auto-generating product descriptions)
OPENAI_API_KEY=your_openai_api_key_here
```

**How to find Google Sheet ID:**
- Open your Google Sheet
- Look at the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
- Copy the `SHEET_ID_HERE` part

**How to find Google Drive Folder ID:**
- Open your parent folder in Google Drive
- Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
- Copy the `FOLDER_ID_HERE` part

### 6. Google Sheet Format

Your Google Sheet should follow this format:

| Title | Size | Price |
|-------|------|-------|
| Product Name 1 | 4 mm | 10 |
| | 6 mm | 14 |
| | 8 mm | 18 |
| Product Name 2 | 10 mm | 12 |
| | 14 mm | 17 |

- The first row should be headers (Title, Size, Price)
- Products start from row 2
- Each product's title is in the first column
- Variants are rows below the product title with empty first column
- The row number of the product title determines the Google Drive folder name

### 7. Google Drive Folder Structure

- Create a parent folder in Google Drive
- Inside the parent folder, create subfolders named with row numbers (e.g., "2", "6")
- Place product images in the corresponding folder
- Supported image formats: JPG, PNG, GIF, WebP

## Usage

### Local Execution

Run the main script:

```bash
python main.py
```

This will:
1. Read all products from your Google Sheet
2. Fetch images from corresponding Google Drive folders
3. Create products in Shopify with variants

### Railway Deployment

1. Create a Railway account and project
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard
4. Set the start command: `python app.py`
5. Railway will automatically deploy your app

### Webhook Usage

Once deployed on Railway, you can trigger the sync by:

**POST request to `/webhook`:**
```bash
curl -X POST https://your-app.railway.app/webhook \
  -H "X-Webhook-Secret: your_webhook_secret_here"
```

**POST request to `/sync`:**
```bash
curl -X POST https://your-app.railway.app/sync
```

**Health check:**
```bash
curl https://your-app.railway.app/health
```

## Project Structure

```
product-automation/
├── main.py                 # Main script for local execution
├── app.py                  # Flask app for Railway webhook
├── config.py              # Configuration management
├── google_sheets_reader.py # Google Sheets integration
├── google_drive_reader.py # Google Drive integration
├── shopify_creator.py      # Shopify product creation
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
├── credentials.json       # Google API credentials (not in git)
└── README.md              # This file
```

## Notes

- Products that already exist in Shopify (by title) will be skipped
- The script will authenticate with Google APIs on first run (browser will open)
- Authentication tokens are saved locally for subsequent runs
- Make sure your Google Drive folder names match the row numbers exactly

## Troubleshooting

1. **Authentication errors**: Delete `token.pickle` and `token_drive.pickle` and re-authenticate
2. **Folder not found**: Ensure folder names match row numbers exactly (e.g., "2" not "02")
3. **Shopify API errors**: Check your access token and API version
4. **Image upload fails**: Ensure images are in supported formats and not corrupted

## License

MIT

