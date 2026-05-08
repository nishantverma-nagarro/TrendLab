import os
import csv
import json
import re
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()
if not os.path.exists('data'):
    os.makedirs('data')
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
TAVILY_API_KEY = os.getenv("TAVILY_KEY")
MODEL_ID = os.getenv("GEMINI_MODEL", "models/gemini-3-flash") # Using Flash for speed/quota

def load_config():
    """ Loads the search and domain settings from config.json """
    with open('config.json', 'r') as f:
        return json.load(f)

def sanitize_text(text):
    """ Swaps banned entities and redacts toxic keywords using word boundaries. """
    try:
        if not os.path.exists('safety_policy.json'): return text
        with open('safety_policy.json', 'r', encoding='utf-8') as f:
            policy = json.load(f)
        
        sanitized = text
        
        # 1. Toxic Keywords - Using \b to prevent redacting words like "classify"
        for word in policy.get('toxic_keywords', []):
            if word.strip():
                # \b ensures we match the WHOLE word only
                pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
                sanitized = pattern.sub("[REDACTED]", sanitized)
        
        # 2. Banned Entities (Consultancy name protection)
        for entity in policy.get('banned_entities', []):
            if entity.strip():
                pattern = re.compile(rf"\b{re.escape(entity)}\b", re.IGNORECASE)
                sanitized = pattern.sub("top-tier consultancy", sanitized)
        
        # 3. Cringe Mapping
        c_map = policy.get('cringe_map', {})
        for bad, good in c_map.items():
            pattern = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
            sanitized = pattern.sub(good, sanitized)
            
        return sanitized
    except: 
        return text

def scout_trends(domain, booster, target_sites, max_results):
    """" Dynamically builds query and respects max_results from config """
    today = datetime.now().strftime("%Y-%m-%d")

    # Format the site list into (site:x OR site:y)
    site_query = " OR ".join([f"site:{site}" for site in target_sites])

    query = f"({site_query}) {domain} ({booster}) as of {today}"
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results
    }
    
    for attempt in range(3):  # Try up to 3 times
        try:
            response = requests.post(
                "https://api.tavily.com/search", 
                json=payload, 
                timeout=5
            )
            response.raise_for_status()
            return response.json().get("results", [])
            
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
            
            print(f"⏳ Connection timeout for {domain}: {e}. Retry {attempt+1}/3...")
            time.sleep(3)  # Wait 3 seconds before trying again
            continue
            
        except Exception as e:
            print(f"⚠️ Tavily Search Error for {domain}: {e}")
            break # Stop if it's a permanent error (like 401 Unauthorized)
            
    return []


def analyze_domain_with_failover(domain, results, model_list):
    """
    Analyzes one domain with multiple model fallback.
    Extracts sentiment and technical keywords while protecting URL integrity.
    """
    # 1. Map IDs to original URLs to prevent LLM hallucinations
    url_map = {f"ID_{i}": res['url'] for i, res in enumerate(results)}
    
    # 2. Package context with IDs but without raw URLs (saves tokens/prevents errors)
    context_package = ""
    for i, res in enumerate(results):
        context_package += f"--- ITEM ID_{i} ---\nTitle: {res['title']}\nContent: {res['content'][:800]}\n\n"

    prompt = f"""
    Analyze these {len(results)} technical signals for the {domain} sector. 
    Return a SINGLE JSON list of objects.
    
    REQUIRED FIELDS PER OBJECT:
    - "id": The matching ID from the context (e.g., "ID_0")
    - "topic": A crisp, professional title
    - "summary": A 2-sentence technical breakdown
    - "hype_score": Integer 1-10
    - "sentiment": Exactly one of ["Bullish", "Bearish", "Neutral"]
    - "keywords": A list of 3 specific technical terms (e.g., 'Zero-Day', 'Lidar', 'Rust')
    - "narrative": Why this matters for the industry
    
    CONTEXT:
    {context_package}
    """

    for model_name in model_list:
        try:
            print(f"🤖 Analyzing {domain} via {model_name}...")
            
            # NEW SDK CALL
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            
            # The new SDK returns text directly or via response.text
            raw_text = response.text
            
            match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if match:
                items = json.loads(match.group())
                for item in items:
                    original_id = item.get('id')
                    item['link'] = url_map.get(original_id, "Source URL Missing")
                    item['domain'] = domain
                    item['date'] = datetime.now().strftime("%Y-%m-%d")
                    
                    for key in ['topic', 'summary', 'narrative']:
                        item[key] = sanitize_text(item.get(key, ""))
                
                return items
                
        except Exception as e:
            # The error string for 429 remains detectable the same way
            if "429" in str(e):
                print(f"⚠️ {model_name} quota hit. Falling back...")
                continue
            else:
                print(f"❌ Error with {model_name}: {e}")
                break 
                
    return None

def main():
    config = load_config()
    settings = config['search_settings']
    targets = config['research_targets']
    models = config['llm_settings']['fallback_models']
    
    # Priority check: If .env has a model, put it at the front of the list
    env_default = os.getenv("GEMINI_MODEL")
    if env_default:
        models = [env_default] + [m for m in models if m != env_default]

    csv_path = 'data/trends.csv'
    if not os.path.exists('data'): os.makedirs('data')
    
    print(f"🚀 Starting Multi-Model Scout...")

    # Define fieldnames
    fieldnames = [
        'date', 'domain', 'topic', 'summary', 
        'hype_score', 'sentiment', 'keywords', 
        'narrative', 'link'
    ]

    for domain, booster in targets.items():
        print(f"🔍 Scouting {domain}...")
        raw = scout_trends(domain, booster, settings['target_sites'], settings['max_results_per_domain'])
        
        if raw:
            # Use the failover logic here
            analysis = analyze_domain_with_failover(domain, raw, models)
            
            if analysis:
                # OPEN file here to ensure incremental save and buffer flush
                file_exists = os.path.isfile(csv_path) and os.stat(csv_path).st_size > 0
                
                with open(csv_path, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    
                    # Write header only if file is new/empty
                    if not file_exists:
                        writer.writeheader()
                    
                    for entry in analysis:
                        # Cleanup temporary keys
                        if 'id' in entry:
                            del entry['id']
                        
                        writer.writerow(entry)
                
                # At this point, 'f' is closed and data is physically on the disk
                print(f"✅ Saved and Synced {domain}")
            else:
                print(f"🛑 Could not process {domain} - All models exhausted.")
        
        # 12s sleep to respect rate limits
        print(f"Sleeping for 12s to manage API load...")
        time.sleep(12)

if __name__ == "__main__":
    main()