import requests
from bs4 import BeautifulSoup
import pandas as pd

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

# Example of fetching and displaying data
schemes_df = get_schemes()
print(schemes_df.head())
