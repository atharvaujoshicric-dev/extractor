import streamlit as st
import pandas as pd
import re
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import quote

class BulkLeadExtractor:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if os.path.exists("/usr/bin/chromium-browser"):
            chrome_options.binary_location = "/usr/bin/chromium-browser"
            service = Service("/usr/bin/chromedriver")
        else:
            service = Service(ChromeDriverManager().install())
            
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.all_leads = []

    def find_phones(self, text):
        pattern = re.compile(r'(\+?\d{1,4}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
        return [f"{m[0]}{m[1]}".strip() for m in pattern.findall(text)]

    def search_and_extract(self, company, designation):
        # Google Dorking Query: Targeted at LinkedIn and contact info
        query = f'site:linkedin.com/in/ "{designation}" "{company}" "mobile" OR "contact"'
        search_url = f"https://www.google.com/search?q={quote(query)}"
        
        try:
            self.driver.get(search_url)
            time.sleep(3) # Wait for Google results
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            search_results = soup.find_all('div', class_='g') # Standard Google Result class

            for result in search_results:
                text = result.get_text(separator=' ')
                phones = self.find_phones(text)
                
                if phones:
                    title_elem = result.find('h3')
                    name = title_elem.get_text() if title_elem else "Unknown"
                    
                    self.all_leads.append({
                        "Company": company,
                        "Name": name.split('-')[0].strip(),
                        "Designation": designation,
                        "Phone": ", ".join(list(set(phones))),
                        "Source Link": result.find('a')['href'] if result.find('a') else "N/A"
                    })
        except Exception as e:
            st.error(f"Error searching for {company}: {e}")

    def close(self):
        self.driver.quit()

# --- UI ---
st.set_page_config(page_title="Bulk Contact Extractor", layout="wide")
st.title("🚀 Bulk LinkedIn & Web Contact Extractor")

st.info("Upload a CSV/Excel with a column named 'Company' to process 45+ companies at once.")

uploaded_file = st.file_uploader("Upload Company List", type=['csv', 'xlsx'])
target_role = st.text_input("Designation to find", value="CEO")

if st.button("Start Bulk Extraction"):
    if uploaded_file and target_role:
        # Load Data
        if uploaded_file.name.endswith('.csv'):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
        
        if 'Company' not in df_input.columns:
            st.error("File must have a 'Company' column!")
        else:
            companies = df_input['Company'].tolist()
            extractor = BulkLeadExtractor()
            progress_bar = st.progress(0)
            
            for i, co in enumerate(companies):
                st.write(f"Searching for {target_role} at {co}...")
                extractor.search_and_extract(co, target_role)
                progress_bar.progress((i + 1) / len(companies))
                time.sleep(2) # Prevent Google blocking
            
            if extractor.all_leads:
                final_df = pd.DataFrame(extractor.all_leads)
                st.success(f"Extraction Complete! Found {len(final_df)} contacts.")
                st.dataframe(final_df)
                
                # Excel Download
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    final_df.to_excel(writer, index=False)
                st.download_button("📥 Download Results (Excel)", output.getvalue(), "leads.xlsx")
            else:
                st.warning("No contacts found. Try a broader designation or check your company names.")
            
            extractor.close()
