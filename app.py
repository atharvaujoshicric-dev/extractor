import streamlit as st
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class LeadExtractor:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Check if we are running on Streamlit Cloud
        # Streamlit Cloud uses /usr/bin/chromium-browser
        import os
        if os.path.exists("/usr/bin/chromium-browser"):
            chrome_options.binary_location = "/usr/bin/chromium-browser"
            service = Service("/usr/bin/chromedriver")
        else:
            # Local development fallback
            service = Service(ChromeDriverManager().install())
            
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.results = []

    def find_phone_numbers(self, text):
        # Regex for common phone patterns
        pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        return list(set(pattern.findall(text)))

    def scrape_leads(self, target_url, target_designation):
        try:
            self.driver.get(target_url)
            time.sleep(5)  # Increased wait for Cloud environments
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find elements containing the designation
            members = soup.find_all(lambda tag: tag.name in ['div', 'section', 'li', 'span'] and 
                                   target_designation.lower() in tag.get_text().lower())

            for member in members:
                text_content = member.get_text(separator=' ')
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
                if lines:
                    name = lines[0]
                    phones = self.find_phone_numbers(text_content)
                    
                    if phones:
                        self.results.append({
                            "Name": name,
                            "Designation": target_designation,
                            "Phone": ", ".join(phones),
                            "Source": target_url
                        })
        except Exception as e:
            st.error(f"Error scraping {target_url}: {str(e)}")

    def export_to_excel(self):
        if self.results:
            return pd.DataFrame(self.results)
        return None

    def close(self):
        self.driver.quit()

# --- Streamlit UI ---
st.title("📞 Lead Extractor Pro")
st.write("Extract names and numbers without AI.")

target_url = st.text_input("Enter Company URL (e.g., https://site.com/team)")
designation = st.text_input("Enter Designation Filter (e.g., Director)")

if st.button("Start Extraction"):
    if target_url and designation:
        with st.spinner("Initializing browser and scanning..."):
            extractor = LeadExtractor()
            try:
                extractor.scrape_leads(target_url, designation)
                df = extractor.export_to_excel()
                
                if df is not None:
                    st.success(f"Found {len(df)} leads!")
                    st.dataframe(df)
                    
                    # Excel Download Logic
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=output.getvalue(),
                        file_name="leads_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("No matches found. Try a different URL or designation.")
            finally:
                extractor.close()
    else:
        st.error("Please provide both a URL and a designation.")
