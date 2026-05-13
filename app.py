import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse
import os

# --- Optimized Driver Setup for Streamlit Cloud ---
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Try to find the system-installed chromium-driver
    # On Streamlit Cloud, this is usually at /usr/bin/chromedriver
    service = Service("/usr/bin/chromedriver")
    
    try:
        return webdriver.Chrome(service=service, options=options)
    except Exception:
        # Fallback for local testing (uses default path)
        return webdriver.Chrome(options=options)

def scrape_leads(company_query, city):
    driver = get_driver()
    
    search_query = f'site:linkedin.com/in/ "{company_query}" "{city}"'
    url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
    
    driver.get(url)
    time.sleep(3) # Increased wait for cloud latency
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_results = soup.find_all('div', class_='g')
    
    leads = []
    for res in search_results:
        try:
            title_tag = res.find('h3')
            if not title_tag: continue
            title = title_tag.text
            
            if " - " in title:
                parts = title.split(" - ")
                name = parts[0]
                designation = parts[1]
            else:
                name = title
                designation = "N/A"
                
            snippet_tag = res.find('div', class_='VwiC3b')
            snippet = snippet_tag.text if snippet_tag else ""
            
            # Basic extraction for phone-like strings
            words = snippet.split()
            phone = "Not Found"
            for word in words:
                clean_word = "".join(filter(str.isdigit, word))
                if len(clean_word) >= 10:
                    phone = word
                    break

            leads.append({
                "Name": name,
                "Designation": designation,
                "Mobile": phone
            })
        except:
            continue
            
    driver.quit()
    return leads

# --- Streamlit UI ---
st.set_page_config(page_title="Lead Extractor", layout="wide")
st.title("🏢 Contact Extractor (No-AI)")

with st.sidebar:
    st.header("Search")
    company_input = st.text_input("Company Name")
    city_input = st.text_input("City", value="San Francisco")
    search_btn = st.button("Start Extraction")

if search_btn and company_input:
    with st.spinner("Accessing web data..."):
        data = scrape_leads(company_input, city_input)
        
        if data:
            df = pd.DataFrame(data)
            
            # Filter Logic
            unique_roles = df['Designation'].unique().tolist()
            selected_roles = st.multiselect("Filter Designations", unique_roles, default=unique_roles)
            
            final_df = df[df['Designation'].isin(selected_roles)]
            st.table(final_df)
            
            # Excel Export
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results (CSV)", data=csv, file_name="leads.csv", mime="text/csv")
        else:
            st.error("Could not find data. Google might be blocking the cloud IP.")
