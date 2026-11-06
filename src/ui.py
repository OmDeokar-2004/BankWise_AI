import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import query_df, execute, add_transaction
from src.ai import ask_gemini

def money(x):
    return f"₹{float(x):,.2f}"

def render_sidebar():
    st.sidebar.markdown("## 🏦 BankWise AI")
    st.sidebar.caption("Banking operations workspace")
    page = st.sidebar.radio("NAVIGATION", ["Dashboard","Accounts","Transactions","Loans","Cards","Fraud Detection","Analytics","AI Assistant"], label_visibility="collapsed")
    st.sidebar.divider()
    st.sidebar.info("Demo environment\n\nAll customer and transaction records are synthetic.")
    return page

def render_dashboard():
    st.title("Banking Overview")
    acc = query_df("SELECT * FROM accounts")
    tx = query_df("SELECT * FROM transactions")
    loans = query_df("SELECT * FROM loans")
    customers = query_df("SELECT * FROM customers")
    total_balance = acc.balance.sum() if not acc.empty else 0
    flagged = int((tx.status=="Flagged").sum()) if not tx.empty else 0
    c = st.columns(4)
    c[0].metric("Total customers", f"{len(customers):,}")
    c[1].metric("Active accounts", f"{int((acc.status=='Active').sum()):,}")
    c[2].metric("Total deposits", money(total_balance))
    c[3].metric("Flagged transactions", f"{flagged:,}", delta="Review required" if flagged else None)
    st.subheader("Operational snapshot")
    left,right = st.columns(2)
    with left:
        if not acc.empty:
            by_type = acc.groupby("account_type",as_index=False).balance.sum()
            st.plotly_chart(px.pie(by_type,names="account_type",values="balance",hole=.55,title="Balance by account type"),use_container_width=True)
    with right:
        if not tx.empty:
            trend = tx.assign(txn_date=pd.to_datetime(tx.txn_date)).groupby([tx.txn_date.dt.to_period("W").astype(str),"txn_type"],as_index=False).amount.sum()
            trend.columns=["Week","Type","Amount"]
            st.plotly_chart(px.bar(trend,x="Week",y="Amount",color="Type",barmode="group",title="Weekly transaction volume"),use_container_width=True)
    st.subheader("Recent transactions")
    recent = query_df("""SELECT t.id,c.name,a.account_number,t.txn_type,t.amount,t.description,t.channel,t.txn_date,t.status
                        FROM transactions t JOIN accounts a ON a.id=t.account_id JOIN customers c ON c.id=a.customer_id
                        ORDER BY t.txn_date DESC,t.id DESC LIMIT 8""")
    st.dataframe(recent, use_container_width=True, hide_index=True)

def render_accounts():
    st.title("Account Management")
    df = query_df("""SELECT a.id,c.name,c.email,c.city,a.account_number,a.account_type,a.balance,a.status
                     FROM accounts a JOIN customers c ON c.id=a.customer_id ORDER BY a.id""")
    st.dataframe(df, use_container_width=True, hide_index=True)
    with st.expander("Add a demo customer and account"):
        with st.form("new_account"):
            name=st.text_input("Customer name")
            email=st.text_input("Email (demo)")
            phone=st.text_input("Phone (demo)")
            city=st.text_input("City",value="Pune")
            typ=st.selectbox("Account type",["Savings","Current","Salary"])
            opening=st.number_input("Opening balance (₹)",min_value=0.0,value=10000.0,step=500.0)
            submitted=st.form_submit_button("Create account")
            if submitted:
                if not name.strip():
                    st.error("Enter a customer name.")
                else:
                    cid=execute("INSERT INTO customers(name,email,phone,city) VALUES(?,?,?,?)",(name,email,phone,city))
                    execute("INSERT INTO accounts(customer_id,account_number,account_type,balance,status) VALUES(?,?,?,?,?)",
                            (cid,f"BW{100000+cid+5000}",typ,opening,"Active"))
                    st.success("Demo account created. Refreshing...")
                    st.rerun()

def render_transactions():
    st.title("Transaction Management")
    st.write("Record simulated credits and debits against local demo accounts.")
    accounts=query_df("""SELECT a.id,a.account_number,c.name,a.balance FROM accounts a JOIN customers c ON c.id=a.customer_id WHERE a.status='Active'""")
    if not accounts.empty:
        options={f"{r.account_number} · {r['name']} · {money(r.balance)}":int(r.id) for _,r in accounts.iterrows()}
        with st.form("transaction_form"):
            label=st.selectbox("Account",list(options.keys()))
            typ=st.selectbox("Transaction type",["Credit","Debit"])
            amount=st.number_input("Amount (₹)",min_value=1.0,value=1000.0,step=100.0)
            desc=st.text_input("Description",value="Demo transaction")
            channel=st.selectbox("Channel",["UPI","Card","Net Banking","ATM","Branch"])
            submitted=st.form_submit_button("Record transaction")
            if submitted:
                try:
                    add_transaction(options[label],typ,amount,desc,channel)
                    st.success("Demo transaction recorded.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    st.subheader("Transaction history")
    df=query_df("""SELECT t.id,c.name,a.account_number,t.txn_type,t.amount,t.description,t.channel,t.txn_date,t.status,t.risk_score
                   FROM transactions t JOIN accounts a ON a.id=t.account_id JOIN customers c ON c.id=a.customer_id
                   ORDER BY t.txn_date DESC,t.id DESC""")
    st.dataframe(df,use_container_width=True,hide_index=True)

def render_loans():
    st.title("Loan Portfolio")
    df=query_df("""SELECT l.id,c.name,l.loan_type,l.principal,l.interest_rate,l.tenure_months,l.outstanding,l.status
                   FROM loans l JOIN customers c ON c.id=l.customer_id""")
    cols=st.columns(3)
    cols[0].metric("Loan accounts",len(df))
    cols[1].metric("Principal portfolio",money(df.principal.sum() if len(df) else 0))
    cols[2].metric("Outstanding",money(df.outstanding.sum() if len(df) else 0))
    st.dataframe(df,use_container_width=True,hide_index=True)
    if not df.empty:
        st.plotly_chart(px.bar(df,x="name",y="outstanding",color="loan_type",title="Outstanding balance by demo customer"),use_container_width=True)

def render_cards():
    st.title("Card Management")
    df=query_df("""SELECT ca.id,c.name,ca.card_type,'•••• ' || ca.last_four AS masked_number,ca.limit_amount,ca.status
                   FROM cards ca JOIN customers c ON c.id=ca.customer_id""")
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.caption("Only masked demo card identifiers are shown. Never enter real card details into this application.")
    with st.expander("Update demo card status"):
        if not df.empty:
            card_id=st.selectbox("Select card",df.id.tolist())
            status=st.selectbox("New status",["Active","Blocked","Expired"])
            if st.button("Update status"):
                execute("UPDATE cards SET status=? WHERE id=?",(status,int(card_id)))
                st.success("Demo card status updated.")
                st.rerun()

def render_fraud():
    st.title("Transaction Monitoring")
    st.write("Simple rules-based demo monitoring. A high score is an alert for review, not a fraud verdict.")
    df=query_df("""SELECT t.id,c.name,a.account_number,t.amount,t.description,t.channel,t.txn_date,t.risk_score,t.status
                   FROM transactions t JOIN accounts a ON a.id=t.account_id JOIN customers c ON c.id=a.customer_id
                   ORDER BY t.risk_score DESC,t.txn_date DESC""")
    threshold=st.slider("Alert threshold",50,95,75)
    alerts=df[df.risk_score>=threshold] if not df.empty else df
    a,b=st.columns(2)
    a.metric("Transactions reviewed",len(df))
    b.metric("Alerts at selected threshold",len(alerts))
    st.dataframe(alerts,use_container_width=True,hide_index=True)
    st.info("Demo scoring rule: large amounts receive higher scores. Production fraud detection requires validated models, monitoring, human review and regulatory controls.")

def render_analytics():
    st.title("Banking Analytics")
    tx=query_df("SELECT * FROM transactions")
    if tx.empty:
        st.info("No transaction data available.")
        return
    tx["txn_date"]=pd.to_datetime(tx["txn_date"])
    a,b=st.columns(2)
    with a:
        by_channel=tx.groupby("channel",as_index=False).amount.sum()
        st.plotly_chart(px.bar(by_channel,x="channel",y="amount",title="Transaction amount by channel"),use_container_width=True)
    with b:
        by_type=tx.groupby("txn_type",as_index=False).amount.sum()
        st.plotly_chart(px.pie(by_type,names="txn_type",values="amount",title="Credit vs debit volume",hole=.45),use_container_width=True)
    daily=tx.groupby(tx.txn_date.dt.date,as_index=False).amount.sum()
    daily.columns=["Date","Amount"]
    st.plotly_chart(px.line(daily,x="Date",y="Amount",markers=True,title="Daily transaction activity"),use_container_width=True)
    st.download_button("Download transaction data (CSV)",tx.to_csv(index=False).encode("utf-8"),"bankwise_transactions.csv","text/csv")

def render_ai_assistant():
    st.title("BankWise AI Assistant")
    st.write("Ask about the demo banking modules, transaction monitoring, or general banking concepts.")
    st.warning("Do not enter passwords, PINs, OTPs, CVVs, full card numbers, or real customer information.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history=[]
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt=st.chat_input("Ask BankWise AI...")
    if prompt:
        st.session_state.chat_history.append({"role":"user","content":prompt})
        customer_count = int(query_df("SELECT COUNT(*) n FROM customers").iloc[0,0])
        account_count = int(query_df("SELECT COUNT(*) n FROM accounts").iloc[0,0])
        flagged_count = int(query_df("SELECT COUNT(*) n FROM transactions WHERE status='Flagged'").iloc[0,0])
        context = f"Customers: {customer_count}; Accounts: {account_count}; Flagged transactions: {flagged_count}."
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer=ask_gemini(prompt,context)
                st.markdown(answer)
        st.session_state.chat_history.append({"role":"assistant","content":answer})
    if st.button("Clear conversation"):
        st.session_state.chat_history=[]
        st.rerun()
