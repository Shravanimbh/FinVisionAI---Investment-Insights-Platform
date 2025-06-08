import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

# Fetch stock data
def fetch_stock_data(ticker, period, interval):
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)
        if data.empty:
            st.error(f"No data found for {ticker}. Please check the ticker symbol.")
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Process datetime
def process_data(data):
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('US/Eastern')
    data.reset_index(inplace=True)
    if 'Date' in data.columns:
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
    elif 'Datetime' not in data.columns:
        data.rename(columns={data.columns[0]: 'Datetime'}, inplace=True)
    return data

# Calculate metrics
def calculate_metrics(data):
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[0]
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    high = data['High'].max()
    low = data['Low'].min()
    volume = data['Volume'].sum()
    return last_close, change, pct_change, high, low, volume

# Streamlit layout
st.set_page_config(layout='wide')
st.title('📈 Real-Time Stock Dashboard')

# Sidebar inputs
st.sidebar.header('Chart Parameters')
ticker = st.sidebar.text_input('Ticker', 'AAPL')

# ✅ Updated Time Period Dropdown
time_period = st.sidebar.selectbox('Time Period', ['1D', '5D', '1W', '2W', '1M'])

# ✅ Chart Type
chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'])

# ✅ Updated Period and Interval Mapping
period_lookup = {
    '1D': '1d',
    '5D': '5d',
    '1W': '7d',
    '2W': '14d',
    '1M': '1mo'
}

interval_mapping = {
    '1D': '1m',
    '5D': '5m',
    '1W': '15m',
    '2W': '30m',
    '1M': '1h'
}

# Update chart
if st.sidebar.button('Update'):
    period = period_lookup[time_period]
    interval = interval_mapping[time_period]

    data = fetch_stock_data(ticker, period, interval)
    if data is not None:
        data = process_data(data)
        last_close, change, pct_change, high, low, volume = calculate_metrics(data)

        st.metric(label=f"{ticker} Last Price", value=f"{last_close:.2f} USD", delta=f"{change:.2f} ({pct_change:.2f}%)")
        col1, col2, col3 = st.columns(3)
        col1.metric('High', f"{high:.2f} USD")
        col2.metric('Low', f"{low:.2f} USD")
        col3.metric('Volume', f"{volume:,}")

        # Chart
        fig = go.Figure()
        if chart_type == 'Candlestick':
            fig.add_trace(go.Candlestick(
                x=data['Datetime'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close']))
        else:
            fig = px.line(data, x='Datetime', y='Close')

        fig.update_layout(title=f"{ticker} {time_period} Chart",
                          xaxis_title='Time',
                          yaxis_title='Price (USD)',
                          height=600)
        st.plotly_chart(fig, use_container_width=True)

# Sidebar mini dashboard
st.sidebar.header('Real-Time Stock Prices')
stock_symbols = ['AAPL', 'GOOGL', 'AMZN', 'MSFT']
for symbol in stock_symbols:
    real_time_data = fetch_stock_data(symbol, '1d', '1m')
    if real_time_data is not None:
        real_time_data = process_data(real_time_data)
        last_price = real_time_data['Close'].iloc[-1]
        open_price = real_time_data['Open'].iloc[0]
        change = last_price - open_price
        pct_change = (change / open_price) * 100
        st.sidebar.metric(symbol, f"{last_price:.2f} USD", f"{change:.2f} ({pct_change:.2f}%)")

# About section
st.sidebar.subheader('About')
st.sidebar.info('This dashboard provides real-time stock data for selected time periods using Yahoo Finance.')
