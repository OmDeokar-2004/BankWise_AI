import streamlit as st
from src.database import init_db, seed_demo_data
from src.ui import render_sidebar, render_dashboard, render_accounts, render_transactions, render_loans, render_cards, render_fraud, render_analytics, render_ai_assistant

st.set_page_config(page_title="BankWise AI", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")
init_db()
seed_demo_data()

st.markdown("""
<style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    [data-testid="stSidebar"] {background: #101a2b;}
    [data-testid="stSidebar"] * {color: #eef4ff;}
    div[data-testid="stMetric"] {background: #f5f8fc; border: 1px solid #e5ebf3; padding: 14px; border-radius: 12px;}
    .hero {padding: 22px 24px; border-radius: 16px; background: linear-gradient(120deg,#14243d,#24558b); color: white; margin-bottom: 18px;}
    .hero h1 {color:white; margin:0; font-size:2rem;}
    .hero p {color:#dce9fa; margin:.35rem 0 0 0;}
    .muted {color:#667085; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

page = render_sidebar()
st.markdown('<div class="hero"><h1>🏦 BankWise AI</h1><p>Intelligent banking operations · Analytics · AI assistance</p></div>', unsafe_allow_html=True)

routes = {
    "Dashboard": render_dashboard,
    "Accounts": render_accounts,
    "Transactions": render_transactions,
    "Loans": render_loans,
    "Cards": render_cards,
    "Fraud Detection": render_fraud,
    "Analytics": render_analytics,
    "AI Assistant": render_ai_assistant,
}
routes[page]()
st.caption("BankWise AI is an educational demo using synthetic data. It is not connected to a financial institution.")
