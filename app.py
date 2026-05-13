import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import urllib.parse

# --- Function: Web Scraper ---
def scrape_leads(company_query, city):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # We use Google Dorking to find LinkedIn profiles without needing a LinkedIn Login
    search_query = f'site:linkedin.com/in/ "{company_query}" "{city}"'
    url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
    
    driver.get(url)
    time.sleep(2) # Allow time for bypass/loading
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_results = soup.find_all('div', class_='g')
    
    leads = []
    for res in search_results:
        try:
            title = res.find('h3').text if res.find('h3') else ""
            # Title usually looks like: "John Doe - Senior Manager - Company Name"
            if " - " in title:
                parts = title.split(" - ")
                name = parts[0]
                designation = parts[1]
            else:
                name = title
                designation = "N/A"
                
            snippet = res.find('div', class_='VwiC3b').text if res.find('div', class_='VwiC3b') else ""
            
            # Basic Regex-free phone extraction from snippets
            words = snippet.split()
            phone = "Not Found"
            for word in words:
                if any(char.isdigit() for char in word) and len(word) > 9:
                    phone = word
                    break

            leads.append({
                "Name": name,
                "Designation": designation,
                "Mobile": phone,
                "Source": "LinkedIn/Google"
            })
        except Exception:
            continue
            
    driver.quit()
    return leads

# --- Streamlit UI ---
st.set_page_config(page_title="Lead Extractor Pro", layout="wide")
st.title("🏢 Contact & Designation Extractor")
st.markdown("Extract names, roles, and numbers without AI API keys.")

with st.sidebar:
    st.header("Search Parameters")
    company_input = st.text_input("Company Name / LinkedIn URL")
    city_input = st.text_input("City Name", value="New York")
    search_btn = st.button("Extract Leads")

if search_btn and company_input:
    with st.spinner(f"Searching for employees at {company_input}..."):
        data = scrape_leads(company_input, city_input)
        
        if data:
            df = pd.DataFrame(data)
            
            # --- Filtering ---
            st.subheader("Filter Results")
            all_designations = df['Designation'].unique().tolist()
            selected_desig = st.multiselect("Filter by Designation", all_designations, default=all_designations)
            
            filtered_df = df[df['Designation'].isin(selected_desig)]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # --- Export to Excel ---
            output_file = "extracted_leads.xlsx"
            filtered_df.to_excel(output_file, index=False)
            
            with open(output_file, "rb") as file:
                st.download_button(
                    label="📥 Export to Excel",
                    data=file,
                    file_name="company_leads.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("No results found. Try adjusting the company name or check your connection.")

elif search_btn:
    st.warning("Please enter a company name or link.")
