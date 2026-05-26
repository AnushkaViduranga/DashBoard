import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from header_footer import render_header, render_footer, render_empty_state
import pandas as pd
from api_client import get_finance
from config import CURRENCY_SYMBOL, PERIOD_OPTIONS, DEFAULT_PERIOD

def show():
    import streamlit as st
    st.markdown("""
<style>
@media (max-width: 480px) {
    [data-testid="stMainBlockContainer"] { padding: 12px 10px !important; }
    [data-testid="stMetric"] { min-width: 0 !important; }
    [data-testid="stMetricValue"] { font-size: 20px !important; }
    [data-testid="stMetricLabel"] { font-size: 11px !important; }
    h1 { font-size: 20px !important; }
    h2 { font-size: 17px !important; }
    h3 { font-size: 15px !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    [data-testid="stHorizontalBlock"] > div { min-width: 140px !important; flex: 1 !important; }
}
@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] { padding: 16px 12px !important; }
    [data-testid="stMetricValue"] { font-size: 22px !important; }
}
/* Accessibility — improved text contrast */
[data-testid="stMetricLabel"] { color: #C8C8D8 !important; font-size: 13px !important; }
[data-testid="stMetricValue"] { color: #F4F1EB !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }
/* Chart labels contrast */
.element-container p { color: #C8C8D8 !important; }
/* Selectbox contrast */
[data-testid="stSelectbox"] label { color: #C8C8D8 !important; font-size: 13px !important; }
[data-testid="stSelectbox"] > div > div {
    background: #1C1A3A !important;
    border-color: rgba(123,92,245,0.3) !important;
    color: #F4F1EB !important;
}
/* File uploader contrast */
[data-testid="stFileUploader"] label { color: #C8C8D8 !important; }
/* Dataframe contrast */
[data-testid="stDataFrame"] { border: 1px solid rgba(123,92,245,0.15) !important; }
/* Focus indicators for keyboard navigation */
button:focus, input:focus, select:focus {
    outline: 2px solid #7B5CF5 !important;
    outline-offset: 2px !important;
}
</style>
""", unsafe_allow_html=True)
    render_header("Finance Dashboard")
    period = st.selectbox("Period", PERIOD_OPTIONS, index=PERIOD_OPTIONS.index(DEFAULT_PERIOD))
    data = get_finance(period)
    if not data:
        render_empty_state()
        return
    if False: st.error("x finance data."); return
    kpis = data["kpis"]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Revenue", f"{CURRENCY_SYMBOL}{kpis['total_revenue']:,.2f}")
    c2.metric("Total Expenses", f"{CURRENCY_SYMBOL}{kpis['total_expenses']:,.2f}")
    c3.metric("Net Profit", f"{CURRENCY_SYMBOL}{kpis['net_profit']:,.2f}")
    c4.metric("Profit Margin", f"{kpis['profit_margin']:.1f}%",
              delta="Low" if kpis["profit_margin"] < 15 else None, delta_color="inverse")
    c1,c2,c3 = st.columns(3)
    c1.metric("Cash in Bank", f"{CURRENCY_SYMBOL}{kpis['cash_in_bank']:,.2f}")
    c2.metric("Monthly Burn Rate", f"{CURRENCY_SYMBOL}{kpis['monthly_burn']:,.2f}")
    c3.metric("Cash Runway", f"{kpis['cash_runway_months']:.1f} months",
              delta="⚠ Critical" if kpis["cash_runway_months"] < 3 else "Healthy",
              delta_color="inverse" if kpis["cash_runway_months"] < 3 else "normal")
    st.markdown("---")
    st.subheader("Revenue vs Expenses")
    df_trend = pd.DataFrame(data["monthly_trend"]).set_index("month")
    st.line_chart(df_trend[["revenue","expenses"]])
    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("Expense breakdown")
        df_exp = pd.DataFrame(data["expense_breakdown"]).set_index("category")
        st.bar_chart(df_exp["amount"])
    with c_right:
        st.subheader("Monthly profit trend")
        df_profit = pd.DataFrame(data["monthly_trend"]).set_index("month")
        st.bar_chart(df_profit["profit"])
    st.markdown("---")
    st.subheader("Cash balance trend")
    df_cash = pd.DataFrame(data["cash_trend"]).set_index("date")
    st.area_chart(df_cash["closing_balance"])
    st.caption(f"Monthly burn rate: **{CURRENCY_SYMBOL}{kpis['monthly_burn']:,.2f}** — Runway: **{kpis['cash_runway_months']:.1f} months**")
    render_footer()