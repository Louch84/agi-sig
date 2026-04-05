#!/usr/bin/env python3
"""
New Western Deal Alert System
Scans perfectplace inbox for new properties from Aidan Daly / New Western
Extracts deal info and generates deal sheets automatically
"""
import subprocess
import json
import re
import os
from datetime import datetime

DEAL_DIR = "/Users/sigbotti/.openclaw/workspace/real-estate/deals/"
os.makedirs(DEAL_DIR, exist_ok=True)

def run_himalaya(cmd):
    """Run himalaya command and return output"""
    env = os.environ.copy()
    env['HIMALAYA_DEFAULT_ACCOUNT'] = 'perfectplace'
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        env=env
    )
    return result.stdout, result.stderr

def get_new_deals():
    """Get recent New Western emails from perfectplace inbox"""
    output, err = run_himalaya(
        'himalaya envelope list --output json --page 1 --page-size 30'
    )
    
    deals = []
    try:
        emails = json.loads(output)
        for e in emails:
            subject = e.get('subject', '')
            sender_name = e.get('from', {}).get('name', '')
            sender_addr = e.get('from', {}).get('addr', '')
            if 'Available' in subject or 'New Property' in subject:
                deals.append({
                    'id': e.get('id', ''),
                    'subject': subject,
                    'from': sender_name or sender_addr,
                    'date': e.get('date', '')
                })
    except json.JSONDecodeError as ex:
        print(f"JSON parse error: {ex}")
    
    return deals

def extract_deal_info(email_body):
    """Extract key deal info from email body"""
    info = {}
    
    # Extract price — handles "$125,000view" or "$125,000"
    price_match = re.search(r'Cash Price:[^0-9]*([0-9,]+)', email_body)
    if price_match:
        info['price'] = int(price_match.group(1).replace(',', ''))
    
    # Extract bedrooms
    bed_match = re.search(r'Bedrooms:\s*([0-9]+)', email_body)
    if bed_match:
        info['bedrooms'] = int(bed_match.group(1))
    
    # Extract bathrooms
    bath_match = re.search(r'Bathrooms:\s*([0-9.]+)', email_body)
    if bath_match:
        info['bathrooms'] = bath_match.group(1)
    
    # Extract address from subject (format: "Available - 123 Main St, City, ST 12345")
    addr_match = re.search(r'Available - (.+?), (.+?), (.+?) \([0-9]', email_body)
    if addr_match:
        info['address'] = addr_match.group(1).strip()
        info['city'] = addr_match.group(2).strip()
        info['state_zip'] = addr_match.group(3).strip()
    
    # Extract property description
    desc_match = re.search(r'Property Description\s*\n\s*(.+?)(?=\n\s*Property Specifications)', 
                          email_body, re.DOTALL)
    if desc_match:
        info['description'] = desc_match.group(1).strip()[:500]
    
    return info


def match_deal_to_buyers(deal_info):
    """Match a deal to buyers based on price, location, property type"""
    import os
    
    buyer_file = "/Users/sigbotti/.openclaw/workspace/real-estate/BUYER-LIST.md"
    if not os.path.exists(buyer_file):
        return []
    
    # For now, return empty — Lou fills in buyer list
    # Matching logic will be added when buyers are populated
    return []

def parse_subject_address(subject):
    """Parse address from email subject line"""
    # Format: "Available - 5810 Washington Ave, Philadelphia, PA 19143"
    # or: "East Mount Airy flip Available - 317 E Vernon Rd, Philadelphia, PA 19119"
    # or: "Graduate Hospital Flip Available - 1842 Christian St, Philadelphia, PA 19146"
    # or: "5 Unit Available - 525 Welsh St, Chester, PA 19013"
    
    addr = subject
    for prefix in ['Available - ', 'flip Available - ', 'Flip Available - ', 'Flip Available - ', 
                   'Unit Available - ', 'Duplex Available - ', 'flip Available - ']:
        addr = addr.replace(prefix, '')
    
    # Now parse "address, city, state zip"
    # City is typically 1-2 words, state is 2 letters, zip is 5 digits
    match = re.match(r'^(.+?), (.+?), ([A-Z]{2}) (\d{5})(.*)$', addr.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip(), f"{match.group(3)} {match.group(4)}"
    
    # Fallback: just try to grab last part as zip
    parts = [p.strip() for p in addr.split(',')]
    if len(parts) >= 3:
        address = parts[0]
        city = parts[1]
        state_zip = parts[2]
        return address, city, state_zip
    
    return addr, '', ''


def generate_deal_sheet(deal_info, email_body, email_id, subject):
    """Generate a deal sheet markdown file"""
    address = deal_info.get('address', 'Unknown Address')
    city = deal_info.get('city', '')
    state_zip = deal_info.get('state_zip', '')
    
    # If no address from body, parse from subject
    if not address or address == 'Unknown Address':
        address, city, state_zip = parse_subject_address(subject)
    price = deal_info.get('price', 0)
    
    # Create filename
    safe_name = address.replace(' ', '-').replace(',', '').replace('#', '')[:50]
    filename = f"deal-{safe_name}.md"
    filepath = os.path.join(DEAL_DIR, filename)
    
    arv_estimate = price * 2.5 if price else 0  # Rough ARV estimate
    your_fee = max(3000, int(price * 0.025))  # ~2.5% fee or $3K minimum
    
    content = f"""# DEAL SHEET — {address}

| Field | Details |
|-------|---------|
| **Asking Price** | ${price:,} |
| **Property Type** | Single Family Home |
| **Bedrooms** | {deal_info.get('bedrooms', 'TBD')} |
| **Bathrooms** | {deal_info.get('bathrooms', 'TBD')} |
| **Area** | {city}, {state_zip} |
| **ARV (After Repair Value)** | ${arv_estimate:,} (estimate — verify with comps) |
| **Est. Repairs** | TBD |
| **Your Fee** | ${your_fee:,}–${your_fee + 1000:,} |
| **Source** | New Western / Aidan Daly |
| **Email ID** | {email_id} |

---

## The Numbers

```
ARV (Estimate):               ${arv_estimate:,}
Your Purchase Price:           ${price:,}
Estimated Repairs:             TBD
                             ─────────────
Your Fee Potential:           ${your_fee:,}–${your_fee + 1000:,}
```

---

## Description

{deal_info.get('description', 'No description available.')}

---

## Next Steps

1. **Verify comps** — what are recent sales in {city}?
2. **Request full package** from New Western: (267) 401-8852 / aidan.daly@newwestern.com
3. **Schedule showing**
4. **Match to buyer profile** — check deal-tracker.md for buyer matches

---

## Contact

**Lou / PerfectPlace**
perfectplacelou@gmail.com

---
*Generated: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filepath

def main():
    print("🔍 Scanning perfectplace inbox for new deals...\n")
    
    deals = get_new_deals()
    print(f"Found {len(deals)} recent New Western deals")
    
    for deal in deals:
        email_id = deal['id']
        subject = deal['subject']
        sender = deal['from']
        date = deal['date']
        
        print(f"\n📬 Deal #{email_id}: {subject}")
        print(f"   From: {sender}")
        print(f"   Date: {date}")
        
        # Read the full email
        body_output, _ = run_himalaya(f'himalaya message read {email_id}')
        
        # Extract deal info from email body
        info = extract_deal_info(body_output)
        info['subject'] = subject
        
        # Try to parse address from subject
        addr, city, state_zip = parse_subject_address(subject)
        info['address'] = addr
        info['city'] = city
        info['state_zip'] = state_zip
        
        print(f"   Price: ${info.get('price', 'N/A')}")
        print(f"   Beds: {info.get('bedrooms', 'N/A')}")
        print(f"   Baths: {info.get('bathrooms', 'N/A')}")
        print(f"   Address: {info.get('address', 'N/A')}")
        
        # Generate deal sheet if we have enough info
        if info.get('price'):
            filepath = generate_deal_sheet(info, body_output, email_id, subject)
            print(f"   ✅ Deal sheet created: {filepath}")
            
            # Auto-match to buyers
            matches = match_deal_to_buyers(info)
            if matches:
                print(f"   🎯 BUYER MATCHES FOUND: {len(matches)}")
                for buyer in matches:
                    print(f"      → {buyer['name']} ({buyer['type']}) — {buyer['contact']}")
        else:
            print(f"   ⚠️ No price found — need to read email manually")
    
    print("\n✅ Scan complete")
    print(f"📁 Deal sheets saved to: {DEAL_DIR}")
    return deals

if __name__ == "__main__":
    main()
