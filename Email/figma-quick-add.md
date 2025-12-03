# Quick Guide: Adding 20 Figma Designs to Your Portfolio

## Step 1: Find Free Figma Templates

Go to: **https://www.figma.com/community**

### Search Terms for Free Templates:
- "free landing page"
- "free form design"
- "free dashboard"
- "free UI kit"
- "free web design"
- "free mobile app"
- "free ecommerce"
- "free portfolio"

## Step 2: Get Embed Link

1. Open the Figma file
2. Click **"Share"** (top right)
3. Click **"Copy link"**
4. Convert to embed format:

**Original:** `https://www.figma.com/file/ABC123/Design-Name?node-id=0-1`

**Embed:** `https://embed.figma.com/design/ABC123/Design-Name?node-id=0-1&embed-host=share`

**Quick conversion:**
- Replace `www.figma.com/file/` → `embed.figma.com/design/`
- Add `&embed-host=share` at the end

## Step 3: Add to Portfolio

Open `email_portfolio.html` and find the Figma Portfolio section (around line 3469).

Copy this template for each design:

```html
<div style="background: #ffffff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h3 style="font-size: 1.3rem; font-weight: 600; margin-bottom: 15px; color: #1a1a1a;">Design Title</h3>
    <p style="color: #666666; margin-bottom: 20px; line-height: 1.6; font-size: 0.95rem;">
        Description of your design.
    </p>
    <div style="position: relative; width: 100%; padding-bottom: 56.25%; background: #f5f5f5; border-radius: 8px; overflow: hidden; border: 1px solid #e5e5e5;">
        <iframe 
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;" 
            src="YOUR_EMBED_URL_HERE" 
            allowfullscreen>
        </iframe>
    </div>
</div>
```

## Popular Free Figma Collections:

1. **UI8.net** - Has free section with quality templates
2. **Dribbble** - Search "Figma file" + "free"
3. **Behance** - Many designers share free Figma files
4. **Figma Community** - Largest collection, all free

## Tips:

- Look for templates with "Free" or "Open Source" tags
- Check the license - most community files are free to use
- You can duplicate files to your own Figma account
- Use the search filters: "Free" + "Templates" + Category

## Example Categories for 20 Designs:

1. Landing Pages (5-6 designs)
2. Forms (3-4 designs)  
3. Dashboards (3-4 designs)
4. Web Components (3-4 designs)
5. Mobile App Designs (2-3 designs)

This gives you variety and shows different design skills!

