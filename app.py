import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="TrendLab | Intelligence Dashboard", layout="wide")

def load_data():
    try:
        df = pd.read_csv('data/trends.csv')
        # Ensure date is datetime for accurate plotting
        df['date'] = pd.to_datetime(df['date'])
        # Ensure keywords are treated as lists, not strings
        df['keywords'] = df['keywords'].apply(lambda x: eval(x) if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# --- HEADER SECTION ---
st.title("🛡️ TrendLab: Defense & Tech Intelligence")

# --- METHODOLOGY EXPANDER ---
with st.expander("ℹ️ Understanding Intelligence Scores & Methodology"):
    st.markdown("""
    ### 🧠 Methodology & Metric Definitions
    TrendLab utilizes a **Natural Language Inference (NLI)** scoring system to quantify qualitative industry data.
    
    #### 📈 The Hype Scale (0-10)
    The **Hype Score** measures the intensity of discussion, investment, and developer activity.
    * **Global Tech Hype (Baseline):** The current average innovation "noise" across all tracked sectors.
    * **Sector Hype (e.g., Software Engineering):** The specific momentum of that niche.
    * **Is High Good?** * **High Hype (>7.5):** Indicates a "Hot" market. Good for visibility, but carries high competition and potential "Bubble" risk.
        * **Low Hype (<3.0):** Indicates "Quiet" innovation. This is often where high-value, overlooked R&D happens.

    #### ⚖️ The Delta (±)
    The **Delta** is the difference between the Sector and the Global Baseline.
    * **Positive Delta:** The sector is outperforming the market (Leading).
    * **Negative Delta:** The sector is cooling down or maturing (Lagging).

    #### 🎭 Sentiment Indicators
    We categorize the "Tone" of technical discourse into three levels:
    * **🟢 Bullish (Strong Growth):** High confidence, positive breakthrough news, and massive adoption signals. High probability of near-term ROI.
    * **🟡 Neutral (Steady/Stable):** Incremental improvements, maintenance-mode discussions, or balanced pros/cons. Low volatility.
    * **🔴 Bearish (Caution/Pivot):** Negative security reports, funding cuts, or technological dead-ends. Signals a need to pivot or wait.

    #### 🎯 Strategic Zones
    * **The Alpha Zone:** (Low Hype + Bullish Sentiment). This is the **"Smart Money"** zone where trends are scientifically sound but haven't been picked up by mainstream media yet.
    * **The Peak Zone:** (High Hype + Bullish Sentiment). Validated success, but high entry cost.
    * **The Warning Zone:** (High Hype + Bearish Sentiment). High noise covering up fundamental flaws or declining interest.
    """)

if df.empty:
    st.warning("No data found. Run the tracker first!")
else:
    # --- GLOBAL SELECTOR ---
    unique_domains = sorted(df['domain'].unique())
    selected_domain = st.selectbox("🎯 Target Intelligence Sector", unique_domains)
    
    # Filter and sort by date for chronological integrity
    domain_data = df[df['domain'] == selected_domain].sort_values('date')

    st.markdown("---")

    # --- 1. METRICS BAR ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        global_hype = df['hype_score'].mean().round(2)
        st.metric("Global Tech Hype", f"{global_hype:.2f} / 10")
    with col2:
        domain_hype = domain_data['hype_score'].mean().round(2) if not domain_data.empty else 0
        delta = domain_hype - global_hype
        st.metric(f"{selected_domain} Hype", f"{domain_hype:.2f}", delta=f"{delta:.2f} vs Global")
    with col3:
        domain_bullish = (len(domain_data[domain_data['sentiment'] == 'Bullish']) / len(domain_data)) * 100 if len(domain_data) > 0 else 0
        st.metric("Sector Sentiment", f"{domain_bullish:.0f}% Bullish")
    with col4:
        st.metric("Total Signals", len(domain_data))

    # --- 2. MOMENTUM GRAPH (Modern Pandas Implementation) ---
    st.markdown("### 📈 Sector Momentum vs. Global Baseline")
    
    # Create a unique list of dates from the whole dataset to anchor the X-axis
    all_dates = pd.DataFrame(df['date'].unique(), columns=['date'])
    
    # Aggregate Global Averages
    global_trend = df.groupby('date')['hype_score'].mean().round(2).reset_index()
    global_trend.columns = ['date', 'Global Baseline']
    
    # Aggregate Sector Averages
    sector_trend = domain_data.groupby('date')['hype_score'].mean().round(2).reset_index()
    sector_trend.columns = ['date', f'{selected_domain} Intensity']
    
    # Merge on the master date list to prevent dimension errors
    chart_df = all_dates.merge(global_trend, on='date', how='left')
    chart_df = chart_df.merge(sector_trend, on='date', how='left')
    
    # Sort and Set Index
    chart_df = chart_df.sort_values('date').set_index('date')
    
    # FIX: Use modern Pandas methods for gap filling (replaces fillna(method='bfill'))
    chart_df = chart_df.interpolate(method='linear').ffill().bfill()
    
    st.line_chart(chart_df, color=["#FF4B4B", "#1C83E1"]) # Red = Global, Blue = Sector

    st.markdown("---")
    
    # --- 3. DOMAIN FEED (Newest First) ---
    st.markdown(f"### 🔍 {selected_domain} Intelligence Feed")
    
    # Use iloc[::-1] to reverse for newest-first display
    for _, row in domain_data.iloc[::-1].iterrows():
        hype_icon = "🔥" if row['hype_score'] >= 7.5 else "❄️"
        sentiment = row['sentiment']
        color, dot = ("green", "🟢") if sentiment == "Bullish" else ("red", "🔴") if sentiment == "Bearish" else ("orange", "🟡")

        title_string = f"**{hype_icon} {dot} | {row['topic']}**"
        
        with st.expander(title_string, expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**Summary:** {row['summary']}")
                st.info(f"**Narrative:** {row['narrative']}")
                # Clean keyword formatting
                signal_line = "  •  ".join([f"`{kw.upper()}`" for kw in row['keywords']])
                st.markdown(f"**Signals:** {signal_line}")
            with c2:
                st.metric("Trend Hype", f"{hype_icon} {row['hype_score']}/10")
                st.markdown(f"**Sentiment:** {dot} :{color}[{sentiment}]")
                st.markdown(f"🔗 [Source Material]({row['link']})")

    # --- 4. INTELLIGENCE CLUSTERS ---
    st.markdown("---")
    st.subheader(f"📡 {selected_domain} Intelligence Clusters")
    
    domain_keywords = [kw for sublist in domain_data['keywords'] for kw in sublist]
    if domain_keywords:
        unique_kw = sorted(list(set(domain_keywords)))
        kw_cloud = " ".join([f"`{k.upper()}`" for k in unique_kw])
        st.markdown(kw_cloud)