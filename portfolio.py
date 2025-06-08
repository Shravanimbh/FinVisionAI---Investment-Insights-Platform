import streamlit as st
import PyPDF2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber
import re
import plotly.express as px
import plotly.graph_objects as go

# === Function to extract data from PDF using pdfplumber ===
def extract_data_from_pdf(pdf_file):
    text = ''
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return text

# === Function to parse investment data using regex (supports stocks, gold, govt schemes) ===
def parse_investment_data(text):
    lines = text.split('\n')
    data = {
        'Asset': [],
        'Investment (₹ Lakhs)': [],
        'Sector': [],
        'Risk Level': [],
        'Category': []
    }

    pattern = re.compile(r'([A-Z]{2,6})\s+(\d+(?:\.\d+)?)\s+([A-Za-z/&\s]+?)\s+(Low|Medium|High|Very Low)', re.IGNORECASE)

    for line in lines:
        match = pattern.search(line)
        if match:
            try:
                asset, invest, sector, risk = match.groups()
                asset_upper = asset.upper()
                invest_val = float(invest)

                # Classify into category
                if any(keyword in sector.lower() for keyword in ['stock', 'equity', 'shares']):
                    category = 'Stock'
                elif 'gold' in sector.lower():
                    category = 'Gold'
                elif any(keyword in sector.lower() for keyword in ['gov', 'nps', 'scheme', 'bond']):
                    category = 'Govt Scheme'
                else:
                    category = 'Others'

                data['Asset'].append(asset_upper)
                data['Investment (₹ Lakhs)'].append(invest_val)
                data['Sector'].append(sector.strip().title())
                data['Risk Level'].append(risk.title())
                data['Category'].append(category)
            except Exception:
                continue

    return pd.DataFrame(data)

# === Streamlit UI ===
with st.sidebar:
    st.header("📁 Upload Portfolio")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

if pdf_file:
    raw_text = extract_data_from_pdf(pdf_file)
    investment_data = parse_investment_data(raw_text)

    if investment_data.empty:
        st.warning("⚠️ No valid portfolio data found in the PDF. Please check the format or try another PDF.")
    else:
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📉 Charts", "📥 Download"])

        # === TAB 1: Overview ===
        with tab1:
            st.subheader("💼 Investment Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                total = investment_data['Investment (₹ Lakhs)'].sum()
                st.metric("Total Investment", f"₹{total:.2f} Lakhs")

            with col2:
                if not investment_data.empty:
                    top = investment_data.loc[investment_data['Investment (₹ Lakhs)'].idxmax()]
                    st.metric("Top Holding", f"{top['Asset']}", f"₹{top['Investment (₹ Lakhs)']} Lakhs")
                else:
                    st.metric("Top Holding", "N/A", "₹0 Lakhs")

            with col3:
                st.metric("Sectors", f"{investment_data['Sector'].nunique()}")

            st.markdown("### 📋 Investment Data")
            st.dataframe(investment_data, use_container_width=True)

            with st.expander("📝 Show Raw Text from PDF"):
                st.text_area("Extracted Text", raw_text, height=200)

        # === TAB 2: Charts ===
        with tab2:
            st.markdown("### 📈 Interactive Charts")

            # Donut Chart - Asset Allocation
            st.subheader("Asset Allocation")
            donut_data = investment_data.groupby('Asset')['Investment (₹ Lakhs)'].sum().reset_index()
            fig_donut = px.pie(
                donut_data,
                values='Investment (₹ Lakhs)',
                names='Asset',
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig_donut.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)
            st.caption("A donut chart showing how your assets are distributed.")

            # Dummy data for Investment Growth (you can replace it with real historical data)
            st.subheader("Investment Growth")
            time_points = ['1M', '3M', '6M']
            values = [5, 12, 20]  # You can dynamically calculate growth if date-wise data is present
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=time_points,
                y=values,
                mode='lines+markers',
                line=dict(color='MediumPurple', width=4)
            ))
            fig_line.update_layout(
                xaxis_title="Time",
                yaxis_title="Investment (₹ Lakhs)",
                margin=dict(t=30, b=30)
            )
            st.plotly_chart(fig_line, use_container_width=True)
            st.caption("Line graph showing the growth of your investments over time.")
            
                        # Category-wise Distribution
            st.subheader("Category-wise Investment Distribution")
            category_data = investment_data.groupby('Category')['Investment (₹ Lakhs)'].sum().reset_index()

            fig_bar = px.bar(
                category_data,
                x='Category',
                y='Investment (₹ Lakhs)',
                color='Category',
                color_discrete_map={
                    'Stock': 'steelblue',
                    'Gold': 'gold',
                    'Govt Scheme': 'seagreen',
                    'Others': 'gray'
                },
                text_auto=True
            )
            fig_bar.update_layout(
                xaxis_title="Category",
                yaxis_title="Total Investment (₹ Lakhs)",
                title="Total Investment by Category",
                margin=dict(t=40, b=30)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # Optional: Boxplot for Investment Spread by Category
            st.subheader("Investment Spread per Asset Type")
            fig_box = px.box(
                investment_data,
                x='Category',
                y='Investment (₹ Lakhs)',
                color='Category',
                color_discrete_sequence=px.colors.qualitative.Set2,
                points='all'  # show all data points
            )
            fig_box.update_layout(
                yaxis_title="Investment (₹ Lakhs)",
                xaxis_title="Category",
                margin=dict(t=30, b=30)
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # === TAB 3: Download ===
        with tab3:
            st.markdown("### 📥 Export Data")
            csv = investment_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="portfolio_analysis.csv",
                mime="text/csv"
            )

else:
    st.info("Please upload a PDF to start analyzing.")

# === Footer ===
st.markdown("---")

