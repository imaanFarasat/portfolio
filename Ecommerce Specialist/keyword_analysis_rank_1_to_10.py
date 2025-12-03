import csv
import json

# Read the CSV file
data = []
with open(r'c:\Users\imanf\Downloads\rezagemcollection.ca-organic.Positions-ca-20251130-2025-12-01T08_25_00Z.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        if row['Position'] and 1 <= int(row['Position']) <= 10:
            data.append(row)

# Sort by position, then by traffic (descending)
data_sorted = sorted(data, key=lambda x: (int(x['Position']), -float(x['Traffic']) if x['Traffic'] else 0))

# Create summary statistics
position_counts = {}
for item in data_sorted:
    pos = int(item['Position'])
    position_counts[pos] = position_counts.get(pos, 0) + 1

# Generate markdown table
markdown_table = "# Keywords Ranking 1-10 Analysis\n\n"
markdown_table += "## Summary Statistics\n\n"
markdown_table += "| Position | Number of Keywords |\n"
markdown_table += "|----------|-------------------|\n"
for pos in sorted(position_counts.keys()):
    markdown_table += f"| {pos} | {position_counts[pos]} |\n"

markdown_table += f"\n**Total Keywords Ranking 1-10: {len(data_sorted)}**\n\n"
markdown_table += "---\n\n"

# Create detailed table
markdown_table += "## Detailed Keyword Analysis (Ranked 1-10)\n\n"
markdown_table += "| # | Keyword | Position | Previous | Search Volume | Keyword Difficulty | CPC | Traffic | Traffic % | Traffic Cost | Competition | URL | Intent | Position Type |\n"
markdown_table += "|---|---------|----------|----------|---------------|-------------------|-----|---------|-----------|--------------|-------------|-----|--------|---------------|\n"

for idx, item in enumerate(data_sorted, 1):
    keyword = item['Keyword']
    position = item['Position']
    prev_pos = item['Previous position']
    search_vol = item['Search Volume']
    kw_diff = item['Keyword Difficulty']
    cpc = item['CPC']
    traffic = item['Traffic']
    traffic_pct = item['Traffic (%)']
    traffic_cost = item['Traffic Cost']
    competition = item['Competition']
    url = item['URL'].replace('https://rezagemcollection.ca', '...')
    intent = item['Keyword Intents']
    pos_type = item['Position Type']
    
    # Truncate long URLs
    if len(url) > 50:
        url = url[:47] + "..."
    
    markdown_table += f"| {idx} | {keyword} | {position} | {prev_pos} | {search_vol} | {kw_diff} | {cpc} | {traffic} | {traffic_pct} | {traffic_cost} | {competition} | {url} | {intent} | {pos_type} |\n"

# Save to file
with open('Keywords_Ranking_1_to_10_Analysis.md', 'w', encoding='utf-8') as f:
    f.write(markdown_table)

print(f"Analysis complete! Generated table with {len(data_sorted)} keywords.")
print(f"\nPosition breakdown:")
for pos in sorted(position_counts.keys()):
    print(f"  Position {pos}: {position_counts[pos]} keywords")

