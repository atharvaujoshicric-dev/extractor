import streamlit as st
import pandas as pd
import re
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup

class LeadExtractor:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # Adding a User-Agent makes the scraper look like a real person
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # This logic works both locally and on Streamlit Cloud
            if os.path.exists("/usr/bin/chromium-browser"):
                # Streamlit Cloud Linux Environment
                chrome_options.binary_location = "/usr/bin/chromium-browser"
                service = Service("/usr/bin/chromedriver")
            else:
                # Local Windows/Mac Environment
                service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            st.error(f"Driver Initialization Failed: {e}")
            self.driver = None

    def find_phone_numbers(self, text):
        # Improved regex for international and local numbers
        pattern = re.compile(r'(\+?\d{1,4}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
        matches = pattern.findall(text)
        # Clean up nested tuples from regex groups
        return [f"{m[0]}{m[1]}".strip() for m in matches]

    def scrape_leads(self, target_url, target_designation):
        if not self.driver:
            return
            
        try:
            self.driver.get(target_url)
            time.sleep(5) # Let JS load
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.results = []
            
            # Find elements containing the designation
            # We look for common container tags
            containers = soup.find_all(['div', 'li', 'section', 'tr'])
            
            for item in containers:
                text = item.get_text(separator=' ', strip=True)
                if target_designation.lower() in text.lower():
                    phones = self.find_phone_numbers(text)
                    if phones:
                        # Extract first line as Name (common pattern)
                        name_guess = text.split('\n')[0].strip()[:50] 
                        self.results.append({
                            "Name/Context": name_guess,
                            "Designation": target_designation,
                            "Phone": ", ".join(list(set(phones))),
                            "Source": target_url
                        })
            
            # Remove duplicates based on phone number
            return pd.DataFrame(self.results).drop_duplicates(subset=['Phone']) if self.results else None
            
        except Exception as e:
            st.error(f"Scraping Error: {e}")
            return None

    def close(self):
        if self.driver:
            self.driver.quit()

# --- Streamlit Interface ---
st.set_page_config(page_title="Lead Scraper", layout="wide")
st.title("📂 Contact & Designation Extractor")

col1, col2 = st.columns(2)
with col1:
    url = st.text_input("Company URL", placeholder="https://company.com/team")
with col2:
    role = st.text_input("Designation Filter", placeholder="CEO, Manager, etc.")

if st.button("Run Extractor", use_container_width=True):
    if url and role:
        extractor = LeadExtractor()
        with st.spinner("Processing... This may take 10-20 seconds."):
            df = extractor.scrape_leads(url, role)
            
            if df is not None and not df.empty:
                st.success(f"Found {len(df)} unique leads!")
                st.dataframe(df, use_container_width=True)
                
                # Excel Download
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                st.download_button(
                    "Download Excel Results",
                    data=output.getvalue(),
                    file_name="leads.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No data found. Ensure the URL is public and contains the designation.")
        extractor.close()
    else:
        st.error("Please enter both URL and Designation.")
