"""Test script to verify OpenAI description generation is working"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ OPENAI_API_KEY not found in .env file")
    print("   Add it to your .env file: OPENAI_API_KEY=sk-your_key_here")
    exit(1)

print(f"✓ Found OPENAI_API_KEY (length: {len(api_key)} characters)")
print(f"  Key starts with: {api_key[:7]}...")

try:
    client = OpenAI(api_key=api_key)
    print("✓ OpenAI client initialized")
    
    # Test generation with the exact same prompt format as the main script
    print("\nTesting description generation...")
    test_title = "Shattuckite Polished Round Gemstone Beads"
    
    prompt = f"""Write a detailed product description for a gemstone bead product titled "{test_title}".

The description should:
1. Start with an engaging introduction about the gemstone
2. Include a section with <h2>Product Specification</h2>
3. Use <p> tags with bullet points (•) to list key features and specifications
4. Be informative, professional, and highlight the beauty and quality of the gemstone
5. Include information about the gemstone's properties, uses, and care instructions

Format the response in HTML with proper tags."""
    
    print(f"Testing with title: {test_title}")
    print("Generating description using gpt-4o-mini...")
    print("(This may take a few seconds...)")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional product description writer for gemstone jewelry."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    description = response.choices[0].message.content.strip()
    
    print(f"\n✓ SUCCESS! Generated description ({len(description)} characters)")
    print("=" * 70)
    print("FULL DESCRIPTION:")
    print("=" * 70)
    print(description)
    print("=" * 70)
    
    # Check if it has the required section
    if '<h2>Product Specification</h2>' in description:
        print("\n✓ Contains <h2>Product Specification</h2> section")
    else:
        print("\n⚠ Missing <h2>Product Specification</h2> section (will be added automatically)")
    
    # Check for bullet points
    if '•' in description or '<li>' in description or '<p>' in description:
        print("✓ Contains bullet points/list formatting")
    
    # Show token usage
    if hasattr(response, 'usage'):
        usage = response.usage
        print(f"\nToken usage:")
        print(f"  Input tokens: {usage.prompt_tokens}")
        print(f"  Output tokens: {usage.completion_tokens}")
        print(f"  Total tokens: {usage.total_tokens}")
        print(f"  Estimated cost: ${usage.total_tokens * 0.15 / 1000000:.6f}")
    
    print(f"\n{'='*70}")
    print("✓✓✓ Description generation is WORKING! ✓✓✓")
    print(f"  You can now use this in your main script.")
    print(f"{'='*70}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("1. Check if your API key is correct")
    print("2. Make sure you have credits in your OpenAI account")
    print("3. Check your OpenAI account at: https://platform.openai.com/usage")

