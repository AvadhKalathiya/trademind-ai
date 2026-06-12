import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import numpy as np

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="TradeMind AI",
    page_icon="📈",
    layout="wide"
)

# ================= GLOBAL UI STYLE =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');
.stApp {
    background: #050d1a;
    color: #e0e0e0;
    font-family: 'Rajdhani', sans-serif;
}
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(0,255,166,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,166,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}
h1 { font-family: 'Orbitron', monospace !important; color: #00ffa6 !important; font-weight: 900 !important; letter-spacing: 3px; }
h2 { font-family: 'Orbitron', monospace !important; color: #00c3ff !important; font-weight: 700 !important; letter-spacing: 2px; }
h3 { font-family: 'Rajdhani', sans-serif !important; color: #00ffa6 !important; font-weight: 600 !important; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 100%);
    border-right: 1px solid rgba(0,255,166,0.2);
}
[data-testid="stSidebar"] * { font-family: 'Rajdhani', sans-serif !important; }
.metric-card {
    background: linear-gradient(135deg, rgba(0,255,166,0.05), rgba(0,195,255,0.05));
    border: 1px solid rgba(0,255,166,0.25);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 10px 0;
    box-shadow: 0 0 20px rgba(0,255,166,0.08), inset 0 0 20px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}
.metric-card:hover {
    border-color: rgba(0,255,166,0.6);
    box-shadow: 0 0 35px rgba(0,255,166,0.18);
    transform: translateY(-2px);
}
.metric-label { color: #8888aa; font-size: 12px; text-transform: uppercase; letter-spacing: 2px; }
.metric-value { color: #00ffa6; font-size: 28px; font-weight: 700; font-family: 'Orbitron', monospace; }
.metric-sub { color: #00c3ff; font-size: 13px; }
.stButton > button {
    background: linear-gradient(90deg, #00ffa6, #00c3ff) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    letter-spacing: 1px !important;
    padding: 10px 28px !important;
    box-shadow: 0 0 20px rgba(0,255,166,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 35px rgba(0,255,166,0.5) !important;
}
hr { border-color: rgba(0,255,166,0.15) !important; }
.ai-analysis-box {
    background: linear-gradient(135deg, rgba(0,195,255,0.08), rgba(0,255,166,0.05));
    border: 1px solid rgba(0,195,255,0.35);
    border-radius: 16px;
    padding: 28px 32px;
    margin: 20px 0;
    box-shadow: 0 0 40px rgba(0,195,255,0.12);
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #cce8ff;
}
.badge-buy {
    display: inline-block;
    background: linear-gradient(90deg, #00ffa6, #00ff6a);
    color: #000; font-weight: 900;
    padding: 8px 24px; border-radius: 30px;
    font-family: 'Orbitron', monospace; font-size: 18px; letter-spacing: 3px;
    box-shadow: 0 0 25px rgba(0,255,166,0.5); margin: 8px 0;
}
.badge-sell {
    display: inline-block;
    background: linear-gradient(90deg, #ff4444, #ff0080);
    color: #fff; font-weight: 900;
    padding: 8px 24px; border-radius: 30px;
    font-family: 'Orbitron', monospace; font-size: 18px; letter-spacing: 3px;
    box-shadow: 0 0 25px rgba(255,68,68,0.5); margin: 8px 0;
}
.badge-hold {
    display: inline-block;
    background: linear-gradient(90deg, #f0a500, #ff8c00);
    color: #000; font-weight: 900;
    padding: 8px 24px; border-radius: 30px;
    font-family: 'Orbitron', monospace; font-size: 18px; letter-spacing: 3px;
    box-shadow: 0 0 25px rgba(240,165,0,0.5); margin: 8px 0;
}
.footer-box {
    margin-top: 60px; padding: 40px; border-radius: 16px;
    background: linear-gradient(135deg, rgba(0,255,166,0.05), rgba(0,195,255,0.05));
    border: 1px solid rgba(0,255,166,0.2); text-align: center;
    box-shadow: 0 0 40px rgba(0,255,166,0.08);
}
.author-name {
    display: inline-block;
    background: rgba(0,255,166,0.08);
    border: 1px solid rgba(0,255,166,0.2);
    color: #00ffa6; padding: 10px 22px; border-radius: 10px;
    font-family: 'Rajdhani', sans-serif; font-size: 17px;
    font-weight: 600; margin: 6px; letter-spacing: 1px;
}
@keyframes pulse-glow {
    0%, 100% { text-shadow: 0 0 20px rgba(0,255,166,0.4); }
    50% { text-shadow: 0 0 50px rgba(0,255,166,0.8), 0 0 80px rgba(0,255,166,0.3); }
}
.stApp h1 { animation: pulse-glow 3s ease-in-out infinite; }
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
}
.block-container { animation: fadeInUp 0.8s ease-out; }
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.title("TRADEMIND AI")
st.markdown(
    "<p style='color:#8888aa; font-family:Rajdhani; font-size:16px; letter-spacing:2px;'>"
    "REAL-TIME FORECASTING · SARIMA MODEL · ACCURACY BACKTEST · LOCAL RECOMMENDATION ENGINE</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# ================= SIDEBAR =================
st.sidebar.markdown("## PARAMETERS")
st.sidebar.markdown("<hr style='border-color:rgba(0,255,166,0.2)'>", unsafe_allow_html=True)
start_date = st.sidebar.date_input('Start Date', date(2025, 1, 1))
end_date = st.sidebar.date_input('End Date', date(2026, 1, 1))
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <div style="background:rgba(0,255,166,0.05); border:1px solid rgba(0,255,166,0.15);
    border-radius:10px; padding:14px 16px; font-family:Rajdhani; font-size:13px; line-height:2;">
        <div style="color:#00ffa6; font-weight:700; letter-spacing:2px; margin-bottom:8px;">TICKER EXAMPLES</div>
        <div style="color:#00c3ff; font-weight:600; margin-top:6px;">&#127470;&#127475; INDIA (.NS or .BO)</div>
        <div style="color:#aaaacc;">&nbsp;&nbsp;TCS.NS &nbsp;&middot;&nbsp; RELIANCE.NS</div>
        <div style="color:#aaaacc;">&nbsp;&nbsp;SBIN.BO &nbsp;&middot;&nbsp; INFY.BO</div>
        <div style="color:#00c3ff; font-weight:600; margin-top:8px;">&#127757; US / GLOBAL</div>
        <div style="color:#aaaacc;">&nbsp;&nbsp;AAPL &nbsp;&middot;&nbsp; TSLA &nbsp;&middot;&nbsp; GOOGL</div>
        <div style="color:#00c3ff; font-weight:600; margin-top:8px;">&#8383; CRYPTO</div>
        <div style="color:#aaaacc;">&nbsp;&nbsp;BTC-USD &nbsp;&middot;&nbsp; ETH-USD</div>
    </div>
    """,
    unsafe_allow_html=True
)
ticker = st.sidebar.text_input(
    "Ticker Symbol",
    placeholder="e.g. TCS.NS / AAPL / BTC-USD"
).strip().upper()

if not ticker:
    st.sidebar.error("Please enter a ticker symbol.")
    st.markdown("""
    <div style='text-align:center; margin-top:80px; color:#445566;'>
        <div style='font-family:Orbitron; font-size:40px; margin-bottom:20px;'>&#128200;</div>
        <div style='font-family:Orbitron; font-size:16px; letter-spacing:3px; color:#00ffa6;'>AWAITING TICKER INPUT</div>
        <div style='font-family:Rajdhani; margin-top:10px; color:#556677;'>Enter a stock symbol in the sidebar to begin analysis</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ================= VALIDATE DATE RANGE =================
if start_date >= end_date:
    st.error("Start Date must be before End Date.")
    st.stop()

# ================= FETCH DATA =================
with st.spinner(f"Fetching data for {ticker}..."):
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        st.stop()

if data is None or data.empty:
    st.error(f"No data found for **{ticker}**. Please check the ticker symbol and date range.")
    st.stop()

# Flatten MultiIndex columns if present
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# Remove duplicate columns if any
data = data.loc[:, ~data.columns.duplicated()]

# Reset index, bring Date as a column
data.index.name = "Date"
data.reset_index(inplace=True)

# Ensure Date column is datetime
data["Date"] = pd.to_datetime(data["Date"])

# Drop rows where all price columns are NaN
price_cols = [c for c in data.columns if c != "Date"]
data.dropna(subset=price_cols, how="all", inplace=True)

if data.empty:
    st.error("All fetched rows are empty after cleaning. Try a different ticker or date range.")
    st.stop()

# ================= CURRENCY =================
is_indian = ticker.endswith(".NS") or ticker.endswith(".BO")
curr = "₹" if is_indian else "$"

# ================= QUICK METRICS =================
st.markdown("### MARKET SNAPSHOT")
try:
    close_col = "Close" if "Close" in data.columns else price_cols[0]
    latest_price = float(data[close_col].iloc[-1])
    prev_price = float(data[close_col].iloc[-2]) if len(data) > 1 else latest_price
    change = latest_price - prev_price
    pct = (change / prev_price) * 100 if prev_price != 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Latest Close</div>
            <div class='metric-value'>{curr}{latest_price:.2f}</div>
            <div class='metric-sub'>{ticker}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        clr = "#00ffa6" if change >= 0 else "#ff4444"
        arr = "+" if change >= 0 else "-"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Daily Change</div>
            <div class='metric-value' style='color:{clr}'>{arr}{abs(change):.2f}</div>
            <div class='metric-sub' style='color:{clr}'>{pct:+.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        high = float(data["High"].max()) if "High" in data.columns else float("nan")
        high_str = f"{curr}{high:.2f}" if not np.isnan(high) else "N/A"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Period High</div>
            <div class='metric-value'>{high_str}</div>
            <div class='metric-sub'>Max recorded</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        low = float(data["Low"].min()) if "Low" in data.columns else float("nan")
        low_str = f"{curr}{low:.2f}" if not np.isnan(low) else "N/A"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Period Low</div>
            <div class='metric-value' style='color:#ff6680'>{low_str}</div>
            <div class='metric-sub'>Min recorded</div>
        </div>""", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Could not render market snapshot: {e}")

# ================= RAW DATA =================
with st.expander("View Raw Data", expanded=False):
    st.write(f"Data from {start_date} to {end_date} — {len(data)} records")
    st.dataframe(data, use_container_width=True)

# ================= VISUALIZATION =================
st.markdown("---")
st.header("PRICE VISUALIZATION")
plot_columns = [col for col in data.columns if col != "Date"]
fig = px.line(data, x="Date", y=plot_columns, title=f"{ticker} — Price Movement", height=500)
fig.update_layout(
    plot_bgcolor="rgba(5,13,26,0.8)", paper_bgcolor="rgba(5,13,26,0)", font_color="#e0e0e0",
    xaxis=dict(gridcolor="rgba(0,255,166,0.07)"),
    yaxis=dict(gridcolor="rgba(0,255,166,0.07)")
)
st.plotly_chart(fig, use_container_width=True)

# ================= COLUMN SELECTION =================
column = st.selectbox("Select column for forecasting", plot_columns)

# Work on a clean copy with just Date + selected column
df = data[["Date", column]].dropna().copy()
df.reset_index(drop=True, inplace=True)

if len(df) < 30:
    st.error("Not enough data points for forecasting. Please select a wider date range.")
    st.stop()

# ================= ADF TEST (silent) =================
try:
    adf_result = adfuller(df[column].dropna())
    p_value = adf_result[1]
    is_stationary = p_value < 0.05
except Exception:
    is_stationary = False

# ================= DECOMPOSITION =================
st.markdown("---")
st.header("SEASONAL DECOMPOSITION")
decomp_period = min(12, len(df) // 2 - 1)
if decomp_period < 2:
    st.warning("Not enough data for seasonal decomposition.")
else:
    try:
        decomposition = seasonal_decompose(df[column], model="additive", period=decomp_period)
        dc1, dc2 = st.columns(2)
        with dc1:
            trend_fig = go.Figure()
            trend_fig.add_trace(go.Scatter(
                x=df["Date"], y=decomposition.trend,
                line=dict(color="#00ffa6", width=2), name="Trend"
            ))
            trend_fig.update_layout(
                title="Trend Component",
                plot_bgcolor="rgba(5,13,26,0.8)", paper_bgcolor="rgba(5,13,26,0)",
                font_color="#e0e0e0", height=300
            )
            st.plotly_chart(trend_fig, use_container_width=True)
        with dc2:
            sea_fig = go.Figure()
            sea_fig.add_trace(go.Scatter(
                x=df["Date"], y=decomposition.seasonal,
                line=dict(color="#ff6680", width=2), name="Seasonal"
            ))
            sea_fig.update_layout(
                title="Seasonal Component",
                plot_bgcolor="rgba(5,13,26,0.8)", paper_bgcolor="rgba(5,13,26,0)",
                font_color="#e0e0e0", height=300
            )
            st.plotly_chart(sea_fig, use_container_width=True)

        resid_fig = go.Figure()
        resid_fig.add_trace(go.Scatter(
            x=df["Date"], y=decomposition.resid,
            line=dict(color="#f0a500", width=2), name="Residuals", mode="markers+lines"
        ))
        resid_fig.update_layout(
            title="Residuals",
            plot_bgcolor="rgba(5,13,26,0.8)", paper_bgcolor="rgba(5,13,26,0)",
            font_color="#e0e0e0", height=280
        )
        st.plotly_chart(resid_fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Decomposition could not be completed: {e}")

# ================= MODEL TRAINING =================
st.markdown("---")
st.header("SARIMA FORECASTING MODEL")

series = df.set_index("Date")[column]

with st.spinner("Training SARIMA model on historical data..."):
    try:
        model = sm.tsa.statespace.SARIMAX(
            series,
            order=(2, 1, 2),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        fitted_model = model.fit(disp=False)
        st.success("Model trained successfully using historical data.")
    except Exception as e:
        st.error(f"Model training failed: {e}")
        st.stop()

# ================= FORECAST =================
forecast_period = st.number_input("Forecast Period (Days)", min_value=1, max_value=365, value=10)
forecast_period = int(forecast_period)

try:
    forecast_result = fitted_model.get_forecast(steps=forecast_period)
    forecast_values = forecast_result.predicted_mean
    conf_int = forecast_result.conf_int()
    future_dates = pd.date_range(
        start=series.index[-1] + timedelta(days=1),
        periods=forecast_period, freq="D"
    )
    predictions = pd.DataFrame({
        "Date": future_dates,
        "Predicted Price": forecast_values.values,
        "Lower CI (95%)": conf_int.iloc[:, 0].values,
        "Upper CI (95%)": conf_int.iloc[:, 1].values
    })
except Exception as e:
    st.error(f"Forecast generation failed: {e}")
    st.stop()

with st.expander("View Forecast Table", expanded=False):
    st.dataframe(predictions, use_container_width=True)

# ================= ACTUAL VS PREDICTED CHART =================
st.subheader("Actual vs Predicted")
df_plot = df.copy()
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df_plot["Date"], y=df_plot[column],
    mode="lines", name="Actual Price",
    line=dict(color="#00ffa6", width=2.5)
))
fig2.add_trace(go.Scatter(
    x=list(predictions["Date"]) + list(predictions["Date"])[::-1],
    y=list(predictions["Upper CI (95%)"]) + list(predictions["Lower CI (95%)"])[::-1],
    fill="toself", fillcolor="rgba(0,195,255,0.08)",
    line=dict(color="rgba(255,255,255,0)"),
    name="95% Confidence Interval"
))
fig2.add_trace(go.Scatter(
    x=predictions["Date"], y=predictions["Predicted Price"],
    mode="lines", name="Predicted Price",
    line=dict(color="#00c3ff", width=2.5, dash="dash")
))
forecast_start_str = str(df_plot["Date"].iloc[-1])[:10]
fig2.add_shape(
    type="line", x0=forecast_start_str, x1=forecast_start_str,
    y0=0, y1=1, xref="x", yref="paper",
    line=dict(dash="dot", color="rgba(255,255,255,0.3)", width=1)
)
fig2.add_annotation(
    x=forecast_start_str, y=1, xref="x", yref="paper",
    text="Forecast Start", showarrow=False,
    font=dict(color="#888", size=11), yshift=10
)
fig2.update_layout(
    title=f"{ticker} — Actual vs Forecasted ({forecast_period} days)",
    plot_bgcolor="rgba(5,13,26,0.8)", paper_bgcolor="rgba(5,13,26,0)",
    font_color="#e0e0e0",
    xaxis=dict(gridcolor="rgba(0,255,166,0.07)", title="Date"),
    yaxis=dict(gridcolor="rgba(0,255,166,0.07)", title="Price"),
    legend=dict(bgcolor="rgba(5,13,26,0.8)", bordercolor="rgba(0,255,166,0.2)", borderwidth=1),
    height=480
)
st.plotly_chart(fig2, use_container_width=True)

# ================= ACCURACY BACKTEST =================
st.markdown("---")
st.header("📊 SARIMA ACCURACY BACKTEST")
st.markdown("**Real accuracy check**: We train on earlier data and predict the *last N days* of your chosen period. Compare with actual prices.")
st.info("Example: Dates 01/01/2025 – 01/01/2026 + Horizon=30 → shows how accurate the model would have been predicting the last 30 days.")

horizon = st.slider("Backtest Horizon (days)", min_value=5, max_value=90, value=30, step=5)

if len(df) > horizon + 60:
    with st.spinner("Running backtest..."):
        full_series = df.set_index("Date")[column]
        train_end_idx = len(full_series) - horizon
        train_series = full_series.iloc[:train_end_idx]
        test_series = full_series.iloc[train_end_idx:]

        try:
            model_bt = sm.tsa.statespace.SARIMAX(
                train_series,
                order=(2, 1, 2),
                seasonal_order=(1, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            fitted_bt = model_bt.fit(disp=False)
            forecast_bt = fitted_bt.forecast(steps=horizon)

            actual = test_series.values.astype(float)
            pred = forecast_bt.values.astype(float)

            mae = np.mean(np.abs(actual - pred))
            rmse = np.sqrt(np.mean((actual - pred) ** 2))
            with np.errstate(divide="ignore", invalid="ignore"):
                mape = np.mean(np.abs((actual - pred) / actual)) * 100 if np.all(actual != 0) else np.nan

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Mean Absolute Error (MAE)", f"{mae:.2f}")
            with c2:
                st.metric("Root Mean Square Error (RMSE)", f"{rmse:.2f}")
            with c3:
                st.metric("Mean Absolute % Error (MAPE)", f"{mape:.2f}%" if not np.isnan(mape) else "N/A")

            bt_dates = full_series.index[train_end_idx:]
            bt_fig = go.Figure()
            bt_fig.add_trace(go.Scatter(
                x=bt_dates, y=actual,
                mode="lines", name="Actual Price",
                line=dict(color="#00ffa6", width=3)
            ))
            bt_fig.add_trace(go.Scatter(
                x=bt_dates, y=pred,
                mode="lines", name="Backtest Predicted",
                line=dict(color="#00c3ff", width=3, dash="dash")
            ))
            bt_fig.update_layout(
                title=f"Backtest Accuracy — Last {horizon} days",
                plot_bgcolor="rgba(5,13,26,0.8)", paper_bgcolor="rgba(5,13,26,0)",
                font_color="#e0e0e0", height=420
            )
            st.plotly_chart(bt_fig, use_container_width=True)

            if not np.isnan(mape):
                if mape < 8:
                    st.success(f"✅ Excellent accuracy! MAPE = {mape:.1f}%")
                elif mape < 15:
                    st.info(f"✅ Good accuracy. MAPE = {mape:.1f}%")
                else:
                    st.warning(f"⚠️ MAPE = {mape:.1f}% — Model has room for improvement on this ticker.")

        except Exception as e:
            st.error(f"Backtest error: {e}")
else:
    st.warning("Not enough data for backtest. Please select a longer date range (at least horizon + 60 days).")

# ================= FORECAST SUMMARY =================
st.markdown("---")
st.header("FORECAST SUMMARY")

last_price = float(df[column].iloc[-1])
pred_end = float(predictions["Predicted Price"].iloc[-1])
pred_change_pct = ((pred_end - last_price) / last_price) * 100 if last_price != 0 else 0.0
pred_min = float(predictions["Predicted Price"].min())
pred_max = float(predictions["Predicted Price"].max())

col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Forecast End Price</div>
        <div class='metric-value'>{curr}{pred_end:.2f}</div>
        <div class='metric-sub'>After {forecast_period} days</div>
    </div>""", unsafe_allow_html=True)
with col_g2:
    fc = "#00ffa6" if pred_change_pct >= 0 else "#ff4444"
    fa = "+" if pred_change_pct >= 0 else "-"
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Expected Return</div>
        <div class='metric-value' style='color:{fc}'>{fa}{abs(pred_change_pct):.2f}%</div>
        <div class='metric-sub'>vs current price</div>
    </div>""", unsafe_allow_html=True)
with col_g3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Forecast Range</div>
        <div class='metric-value' style='font-size:18px'>{curr}{pred_min:.2f} – {curr}{pred_max:.2f}</div>
        <div class='metric-sub'>Min to Max predicted</div>
    </div>""", unsafe_allow_html=True)

# ================= LOCAL RECOMMENDATION ENGINE =================
st.markdown("---")
st.header("🧠 LOCAL RECOMMENDATION ENGINE")

if pred_change_pct > 5.0:
    badge_html = "<span class='badge-buy'>BUY</span>"
    rec_text = "Strong bullish forecast. Expected return &gt;5%. Good entry opportunity."
elif pred_change_pct < -3.0:
    badge_html = "<span class='badge-sell'>SELL</span>"
    rec_text = "Bearish signal. Consider exiting or hedging position."
else:
    badge_html = "<span class='badge-hold'>HOLD</span>"
    rec_text = "Sideways/neutral movement expected. Maintain current position."

st.markdown(
    f"""
    <div class='ai-analysis-box'>
        <strong style='color:#00c3ff; font-family:Orbitron; font-size:13px; letter-spacing:3px;'>
        SARIMA RECOMMENDATION ENGINE &mdash; {ticker}
        </strong><br><br>
        {badge_html}<br><br>
        <strong>Predicted Change:</strong> {pred_change_pct:+.2f}%<br><br>
        {rec_text}<br><br>
        <strong>Key Insight:</strong> Based purely on SARIMA forecast + backtest accuracy.<br>
        <span style='color:#ffaa00; font-size:13px;'>&#9888;&#65039; This is NOT financial advice. Use only for educational purposes.</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ================= FOOTER =================
st.markdown("---")
st.markdown("""
<div class='footer-box'>
    <div style='font-family:Orbitron; font-size:20px; color:#00ffa6; letter-spacing:3px; margin-bottom:8px;'>
        TradeMind AI
    </div>
    <div style='font-family:Rajdhani; color:#556677; font-size:14px; letter-spacing:2px; margin-bottom:24px;'>
        yFinance &middot; SARIMA &middot; Built-in Accuracy Backtest &middot; Local Recommendation Engine
    </div>
    <div style='margin-bottom:20px;'>
        <span class='author-name'>Avadh Kalathiya</span>
    </div>
    <div style='font-family:Rajdhani; color:#334455; font-size:13px;'>
        MBIT - CVM University
    </div>
</div>
""", unsafe_allow_html=True)