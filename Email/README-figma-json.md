# Figma Designs JSON Guide

## Overview

The `figma-designs.json` file contains 25 design templates:
- **10 Form Designs** - Various form types (login, signup, contact, etc.)
- **15 Landing Page Designs** - Different landing page styles and categories

## Structure

Each design has:
- `id`: Unique identifier
- `title`: Design name
- `description`: Brief description
- `category`: Design category
- `style`: Design style
- `embedUrl`: Figma embed URL (empty - you need to fill this)
- `tags`: Searchable tags

## How to Use

### Step 1: Find Figma Templates

1. Go to https://www.figma.com/community
2. Search for designs matching the titles/categories in the JSON
3. Example searches:
   - "login form template"
   - "saas landing page"
   - "ecommerce landing page"

### Step 2: Get Embed URLs

For each design:
1. Open the Figma file
2. Click "Share" → "Copy link"
3. Convert to embed format:
   - Replace `www.figma.com/file/` with `embed.figma.com/design/`
   - Add `&embed-host=share` at the end

### Step 3: Update JSON

1. Open `figma-designs.json`
2. Find the design you want to add
3. Paste the embed URL in the `embedUrl` field
4. Save the file

### Step 4: Generate HTML

Option 1: Use the generator (if running locally):
- Open `generate-figma-html.html` in a browser
- Click "Generate All HTML" or specific category
- Copy the generated HTML

Option 2: Manual copy:
- Use the template in `email_portfolio.html`
- Copy the structure for each design
- Replace placeholders with JSON data

## Example JSON Entry

```json
{
  "id": "form-1",
  "title": "Login Form Design",
  "description": "Modern login form with clean UI...",
  "category": "Authentication",
  "style": "Minimalist",
  "embedUrl": "https://embed.figma.com/design/ABC123/Login-Form?node-id=0-1&embed-host=share",
  "tags": ["login", "authentication", "minimalist"]
}
```

## Categories Included

### Forms (10):
- Authentication (Login, Signup, Password Reset)
- Contact & Communication
- E-commerce (Checkout)
- Data Collection (Survey, Feedback)
- Booking & Applications

### Landing Pages (15):
- SaaS Products
- E-commerce
- Portfolio
- Mobile Apps
- Events
- Services
- Education
- Real Estate
- Food & Beverage
- Fitness
- Non-profit
- Tech Startup
- Travel
- Creative Agency
- Healthcare

## Tips

1. **Search Strategy**: Use the tags and categories to find matching Figma templates
2. **Quality Check**: Preview designs before adding embed URLs
3. **Consistency**: Keep descriptions concise and professional
4. **Organization**: Group similar designs together in your portfolio

## Next Steps

1. Find 25 Figma designs matching the JSON entries
2. Get embed URLs for each
3. Update the JSON file
4. Generate HTML using the helper tool
5. Add to `email_portfolio.html` in the Figma Portfolio section

