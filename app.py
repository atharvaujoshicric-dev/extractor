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
        self.options = Options()
        self.options.add_argument("--headless")  # Run without a popup window
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.results = []

    def find_phone_numbers(self, text):
        """Uses Regex to find common mobile number formats."""
        pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        return list(set(pattern.findall(text)))

    def scrape_leads(self, target_url, target_designation):
        print(f"Scanning {target_url}...")
        self.driver.get(target_url)
        time.sleep(3) # Wait for JS to load
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # This logic looks for common 'Team' or 'About' page structures
        # It searches for elements containing the designation filter
        members = soup.find_all(lambda tag: tag.name in ['div', 'section', 'li'] and 
                               target_designation.lower() in tag.get_text().lower())

        for member in members:
            text_content = member.get_text(separator=' ')
            
            # Simple extraction heuristic
            # Note: Real-world scraping requires site-specific selectors
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            if lines:
                name = lines[0] # Usually the first line in a profile card
                phones = self.find_phone_numbers(text_content)
                
                if phones:
                    self.results.append({
                        "Name": name,
                        "Designation": target_designation,
                        "Phone": ", ".join(phones),
                        "Source": target_url
                    })

    def export_to_excel(self, filename="leads_export.xlsx"):
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_excel(filename, index=False)
            print(f"Success! {len(df)} leads exported to {filename}")
        else:
            print("No leads found matching the criteria.")

    def close(self):
        self.driver.quit()

# --- Execution ---
if __name__ == "__main__":
    extractor = LeadExtractor()
    
    # Example: Scraping a company 'Team' page
    # Replace with actual URLs you have permission to scrape
    target_site = "https://example-company.com/about-us" 
    filter_role = "Director" 

    try:
        extractor.scrape_leads(target_site, filter_role)
        extractor.export_to_excel()
    finally:
        extractor.close()
