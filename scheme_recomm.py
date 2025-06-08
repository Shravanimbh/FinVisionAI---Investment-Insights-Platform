import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Function to scrape government schemes from Sarkari Yojana website
def get_schemes():
    url = 'https://sarkariyojana.com/'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the schemes listed
        schemes = soup.find_all('div', class_='yojana-item')
        
        scheme_data = []
        for scheme in schemes:
            title = scheme.find('a').text.strip()
            description = scheme.find('p').text.strip()
            link = scheme.find('a')['href']
            scheme_data.append({
                'title': title,
                'description': description,
                'link': link
            })
        
        return pd.DataFrame(scheme_data)
    else:
        return pd.DataFrame(columns=["title", "description", "link"])

# Streamlit UI
st.title('Investment Insight: Government Scheme Recommender')
st.write('Answer a few questions to get the best matching government schemes for your investment style.')

# Get real-time data
schemes_df = get_schemes()

# User Inputs
age = st.slider("Your Age", 18, 80)
risk = st.selectbox("Your Risk Appetite", ["Low", "Medium", "High"])
goal = st.selectbox("Your Investment Goal", ["Tax Saving", "Wealth Creation", "Retirement"])

# Filter schemes based on user input
filtered_schemes = schemes_df[schemes_df['description'].str.contains(goal, case=False)]

# Display the filtered schemes
if not filtered_schemes.empty:
    st.write("Suggested Government Schemes for You:")
    st.dataframe(filtered_schemes)
else:
    st.write("No matching schemes found. Try adjusting your criteria.")
