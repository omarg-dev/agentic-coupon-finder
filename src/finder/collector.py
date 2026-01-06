from datetime import datetime
import json
import os
# from google import genai
from groq import Groq
from ddgs import DDGS
from src.data.database import SessionLocal
from src.data.models import Coupon, Website



class CouponFinder:
    def __init__(self):
        self.ddgs = DDGS()
        # self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def find_codes(self, domain: str):
        print(f"🔎 Finder: Searching for '{domain}' coupons...")
        
        # broader search for international/specific domains
        search_query = f'"{domain}" promo code OR "{domain}" coupon code -site:couponbirds.com'
        
        try:
            # 'wt-wt' = global (no region). Better for finding results on US-hosted sites for INT domains
            results = self.ddgs.text(search_query, max_results=15, region='wt-wt')
        except Exception as e:
            print(f"⚠️ Search Error: {e}")
            return []
        
        if not results:
            print("❌ No search results found.")
            return []
        
        # prepare payload
        snippets = []
        for r in results:
            title = r.get('title', '')
            body = r.get('body', '')
            if title or body:
                snippets.append(f"- {title}: {body}")
        
        combined_text = "\n".join(snippets)

        # use an LLM to extract codes
        try:
            print("🤖 LLM: Extracting codes from search snippets...")
            extracted_codes = self._extract_LLM(domain, combined_text)
        except Exception as e:
            print(f"⚠️ LLM extraction failed: {e}")
            extracted_codes = {}
        
        # save to database
        if extracted_codes:
            self._save_to_db(domain, extracted_codes)
        
        print(f"✅ Found {len(extracted_codes)} candidates: {list(extracted_codes.keys())}")
        return extracted_codes

    def _extract_LLM(self, domain, text_blob):
        prompt = f"""
        You are a data extraction agent. Extract active, valid coupon codes for '{domain}' from the text below.
        
        STRICT RULES:
        1. Return a JSON object with a single key "codes" containing a list of strings.
        2. IGNORE generic words like "DEAL", "OFFER", "AMAZON", "CLICK", "CODE", "SALE".
        3. IGNORE sentences or descriptions. Only extract the actual code (e.g., "SAVE20").
        4. For each code, return a description in the "descriptions" key, matching the order of codes.
        5. Return EVERY valid code you find, even if they are similar.
        6. Even if the code is not explicitly marked as working, include it.
        6. If no valid codes are found, return {{"codes": [], "descriptions": []}}.
        
        Input Text:
        {text_blob}
        """

        try:
            # LLM call
            # response = self.client.models.generate_content(
            #     model="gemini-2.5-flash-lite", 
            #     contents=prompt,
            #     config={
            #         'response_mime_type': 'application/json'
            #     }
            # )

            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            
            # parse JSON
            data = json.loads(response.choices[0].message.content)
            codes = data.get("codes", [])
            descriptions = data.get("descriptions", [])
            
            # create map {code: description}
            result_map = {}
            for i, code in enumerate(codes):
                if isinstance(code, str):
                    clean_code = code.strip().upper()
                    desc = descriptions[i] if i < len(descriptions) else "No description"
                    result_map[clean_code] = desc

            if result_map:
                print(f"💎 LLM found: {list(result_map.keys())}")
            else:
                print("🤷 LLM found no valid codes in the text.")
                
            return result_map
            
        except Exception as e:
            print(f"⚠️ LLM Error: {e}")
            return []

    def _save_to_db(self, domain, codes_maps):
        session = SessionLocal()
        try:
            # get or create website
            website = session.query(Website).filter_by(domain=domain).first()
            if not website:
                website = Website(
                    domain=domain, 
                    is_shop=True, 
                    last_scraped=datetime.now()
                )
                session.add(website)
                session.commit()
                session.refresh(website)

            # save coupons
            new_count = 0
            for code, description in codes_maps.items():
                # check if exists
                exists = session.query(Coupon).filter_by(website_id=website.id, code=code).first()
                if not exists:
                    new_coupon = Coupon(
                        website_id=website.id,
                        code=code,
                        description=description,
                        is_working=None,
                        created_at=datetime.now()
                    )
                    session.add(new_coupon)
                    new_count += 1
            
            session.commit()
            print(f"💾 Saved {new_count} new codes to The Vault.")
        
        except Exception as e:
            print(f"❌ Database Error: {e}")
            session.rollback()
        finally:
            session.close()