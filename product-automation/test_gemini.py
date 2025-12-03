"""Test script to verify Gemini AI description generation is working"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"✓ Found GEMINI_API_KEY (length: {len(api_key)} characters)")

try:
    genai.configure(api_key=api_key)
    print("✓ Configured Gemini AI")
    
    # List available models
    print("\nListing available models...")
    models = genai.list_models()
    available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    
    if available_models:
        print(f"✓ Found {len(available_models)} available models:")
        for model in available_models[:5]:  # Show first 5
            print(f"  - {model}")
        
        # Try to use a model
        preferred_models = ['models/gemini-1.5-pro', 'models/gemini-pro', 'models/gemini-1.5-flash']
        model_to_use = None
        
        for preferred in preferred_models:
            if preferred in available_models:
                model_to_use = preferred.replace('models/', '')
                break
        
        if not model_to_use:
            model_to_use = available_models[0].replace('models/', '')
        
        print(f"\n✓ Using model: {model_to_use}")
        model = genai.GenerativeModel(model_to_use)
        
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
        print("Generating description...")
        response = model.generate_content(prompt)
        
        if hasattr(response, 'text'):
            description = response.text.strip()
            print(f"\n✓ SUCCESS! Generated description ({len(description)} characters)")
            print("=" * 60)
            print("FULL DESCRIPTION:")
            print("=" * 60)
            print(description)
            print("=" * 60)
            
            # Check if it has the required section
            if '<h2>Product Specification</h2>' in description:
                print("\n✓ Contains <h2>Product Specification</h2> section")
            else:
                print("\n⚠ Missing <h2>Product Specification</h2> section (will be added automatically)")
            
            # Check for bullet points
            if '•' in description or '<li>' in description or '<p>' in description:
                print("✓ Contains bullet points/list formatting")
            
            print(f"\n✓ Description generation is WORKING!")
            print(f"  You can use this in your main script.")
        elif hasattr(response, 'candidates') and response.candidates:
            description = response.candidates[0].content.parts[0].text.strip()
            print(f"\n✓ SUCCESS! Generated description ({len(description)} characters)")
            print("=" * 60)
            print(description)
            print("=" * 60)
        else:
            print("❌ Response doesn't have expected format")
            print(f"Response type: {type(response)}")
            print(f"Response attributes: {dir(response)}")
            print(f"Response: {response}")
    else:
        print("❌ No available models found")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

