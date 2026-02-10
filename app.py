import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")
st.title("📈 Stock Market Peer Analysis Dashboard")

# 2. Load and Prepare Data
@st.cache_data
def load_data():
    nflx = pd.read_csv("NFLX.csv")
    tsla = pd.read_csv("TSLA.csv")
    
    nflx['Source'] = 'Netflix'
    tsla['Source'] = 'Tesla'
    
    df = pd.concat([nflx, tsla])
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# 3. Sidebar - Filters
st.sidebar.header("User Input Features")
selected_stocks = st.sidebar.multiselect(
    "Select Stocks",
    options=df['Source'].unique(),
    default=df['Source'].unique()
)

filtered_df = df[df['Source'].isin(selected_stocks)]

min_date = filtered_df['Date'].min().date()
max_date = filtered_df['Date'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

final_df = filtered_df[
    (filtered_df['Date'].dt.date >= start_date) & 
    (filtered_df['Date'].dt.date <= end_date)
]

# 4. Main Panel - Key Metric Cards
st.header("Key Performance Metrics")

cols = st.columns(len(selected_stocks))

for i, stock in enumerate(selected_stocks):
    with cols[i]:
        stock_data = final_df[final_df['Source'] == stock]
        latest_price = stock_data['Close'].iloc[-1]
        prev_price = stock_data['Close'].iloc[-2]
        delta = latest_price - prev_price
        
        # Front of card (Metric)
        st.metric(label=f"{stock} Close Price", value=f"${latest_price:.2f}", delta=f"{delta:.2f}")
        
        # "Back" of card (Data Info)
        with st.expander(f"View {stock} Details"):
            st.write(f"Highest Price: ${stock_data['High'].max():.2f}")
            st.write(f"Lowest Price: ${stock_data['Low'].min():.2f}")
            st.write(f"Average Volume: {stock_data['Volume'].mean():,.0f}")

# --- Peer Average Card ---
st.markdown("---")
st.subheader("Peer Comparison Metrics")

# Calculate Peer Average
peer_avg = final_df.groupby('Date')['Close'].mean()
latest_avg = peer_avg.iloc[-1]
prev_avg = peer_avg.iloc[-2]
avg_delta = latest_avg - prev_avg

# Front of card
st.metric(label="Peer Average Close Price", value=f"${latest_avg:.2f}", delta=f"{avg_delta:.2f}")

# "Back" of card (Data Info)
with st.expander("View Peer Average Details"):
    st.write(f"Historical Average Price: ${peer_avg.mean():.2f}")
    st.write(f"Total Companies in Peers: {len(selected_stocks)}")

# 5. Visualizations
st.markdown("---")
st.subheader(f"Stock price Comparison: {', '.join(selected_stocks)}")

fig = px.line(
    final_df, 
    x='Date', 
    y='Close', 
    color='Source',
    title="Close Price Comparison",
    labels={'Close': 'Stock Price ($)', 'Source': 'Company'}
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

#Display Raw Data
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data View")
    st.dataframe(final_df)