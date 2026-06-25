import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# PAGE CONFIG
st.set_page_config(
    page_title="SBI Banking Management System",
    page_icon="🏦",
    layout="wide"
)

# FILE PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BANK_FILE = os.path.join(BASE_DIR, "bank.csv")
TRANSACTION_FILE = os.path.join(BASE_DIR, "transactions.csv")

# CREATE FILES IF NOT EXISTS
if not os.path.exists(BANK_FILE):
    pd.DataFrame(columns=["Account_No", "PIN", "Name", "Email", "Phone", "Balance"]).to_csv(BANK_FILE, index=False)

if not os.path.exists(TRANSACTION_FILE):
    pd.DataFrame(columns=["Account_No", "Amount", "Type", "Date"]).to_csv(TRANSACTION_FILE, index=False)


# HELPER FUNCTIONS
def load_accounts():
    return pd.read_csv(BANK_FILE, dtype={"Account_No": str, "PIN": str})

def load_transactions():
    return pd.read_csv(TRANSACTION_FILE, dtype={"Account_No": str})

def save_accounts(df):
    df.to_csv(BANK_FILE, index=False)

def save_transactions(df):
    df.to_csv(TRANSACTION_FILE, index=False)


# THEME
st.markdown("""
<style>
.stApp{background:#0B1120;color:white;}
h1,h2,h3,h4{color:white!important;}
[data-testid="stSidebar"]{background:#111827;}
[data-testid="stSidebar"] *{color:white;}
[data-testid="metric-container"]{
    background:linear-gradient(135deg,#1E293B,#0F172A);
    border:1px solid #334155;
    padding:15px;
    border-radius:18px;
}
.stButton>button{
    width:100%;
    background:linear-gradient(90deg,#16a34a,#22c55e);
    color:white;
    border:none;
    border-radius:10px;
    height:50px;
}
</style>
""", unsafe_allow_html=True)


st.title("🏦 SBI Banking Management System")
st.markdown("### Manage accounts, deposits, withdrawals & transfers")

menu = st.sidebar.selectbox(
    "Select Service",
    ["Dashboard", "Create Account", "Deposit", "Withdraw",
     "Fund Transfer", "Change PIN", "Balance Enquiry", "Transaction History"]
)

# ───────────────────────── DASHBOARD ─────────────────────────
if menu == "Dashboard":
    accounts = load_accounts()
    transactions = load_transactions()

    total_balance = accounts["Balance"].sum() if len(accounts) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("👤 Total Accounts", len(accounts))
    with c2:
        st.metric("💰 Total Balance", f"₹ {total_balance:,.0f}")
    with c3:
        st.metric("📈 Transactions", len(transactions))
    with c4:
        st.metric("🏦 Active Accounts", len(accounts))

    st.divider()

    if len(transactions) > 0:

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                transactions,
                names="Type",
                hole=0.5
            )
            fig.update_layout(
                paper_bgcolor="#0B1120",
                plot_bgcolor="#0B1120",
                font_color="white"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            summary = transactions.groupby("Type")["Amount"].sum().reset_index()

            fig2 = px.bar(summary, x="Type", y="Amount", title="Transaction Summary")
            fig2.update_layout(
                paper_bgcolor="#0B1120",
                plot_bgcolor="#0B1120",
                font_color="white"
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Recent Transactions")
    st.dataframe(transactions.tail(10), use_container_width=True)


# ───────────────────────── CREATE ACCOUNT ─────────────────────────
elif menu == "Create Account":
    st.subheader("📝 Create New Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    pin = st.text_input("4 Digit PIN", type="password", max_chars=4)
    balance = st.number_input("Opening Balance", min_value=0.0, step=100.0)

    if st.button("Create Account"):
        accounts = load_accounts()

        if not name.strip():
            st.error("Name required")
        elif "@" not in email:
            st.error("Invalid email")
        elif len(phone) != 10:
            st.error("Phone must be 10 digits")
        elif len(pin) != 4:
            st.error("PIN must be 4 digits")
        else:
            if len(accounts) == 0:
                acc_no = "SBI1001"
            else:
                last_no = int(accounts["Account_No"].str.replace("SBI", "").astype(int).max())
                acc_no = "SBI" + str(last_no + 1)

            new_row = pd.DataFrame([{
                "Account_No": acc_no,
                "PIN": pin,
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Balance": balance
            }])

            accounts = pd.concat([accounts, new_row], ignore_index=True)
            save_accounts(accounts)

            st.success("Account Created Successfully")
            st.info(f"Account Number: {acc_no}")


# ───────────────────────── DEPOSIT ─────────────────────────
elif menu == "Deposit":
    st.subheader("💰 Deposit Money")

    accounts = load_accounts()
    transactions = load_transactions()

    if len(accounts) == 0:
        st.warning("No accounts found")
    else:
        # ACCOUNT SELECT DROPDOWN
        acc = st.selectbox(
            "Select Account",
            accounts["Account_No"].tolist()
        )

        holder = accounts.loc[
            accounts["Account_No"] == acc,
            "Name"
        ].iloc[0]

        balance = accounts.loc[
            accounts["Account_No"] == acc,
            "Balance"
        ].iloc[0]

        # READ-ONLY INFO
        st.text_input("Account Holder", holder, disabled=True)
        st.text_input("Current Balance", f"₹ {balance:,.0f}", disabled=True)

        amount = st.number_input("Deposit Amount", min_value=1.0, step=100.0)

        if st.button("Deposit"):
            accounts.loc[accounts["Account_No"] == acc, "Balance"] += amount
            save_accounts(accounts)

            new_tx = pd.DataFrame([{
                "Account_No": acc,
                "Amount": amount,
                "Type": "Deposit",
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])

            transactions = pd.concat([transactions, new_tx], ignore_index=True)
            save_transactions(transactions)

            new_balance = accounts.loc[
                accounts["Account_No"] == acc,
                "Balance"
            ].iloc[0]

            st.success("✅ Deposit Successful")
            st.metric("Updated Balance", f"₹ {new_balance:,.0f}")


# ───────────────────────── WITHDRAW ─────────────────────────
elif menu == "Withdraw":
    st.subheader("💸 Withdraw Money")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1.0)

    if st.button("Withdraw"):
        accounts = load_accounts()
        transactions = load_transactions()

        mask = (accounts["Account_No"] == acc) & (accounts["PIN"] == pin)

        if mask.any():
            balance = accounts.loc[mask, "Balance"].iloc[0]

            if balance >= amount:
                accounts.loc[mask, "Balance"] -= amount
                save_accounts(accounts)

                transactions = pd.concat([transactions, pd.DataFrame([{
                    "Account_No": acc,
                    "Amount": amount,
                    "Type": "Withdraw",
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])], ignore_index=True)

                save_transactions(transactions)

                st.success("Withdrawal Successful")
                st.metric("Remaining Balance", accounts.loc[mask, "Balance"].iloc[0])
            else:
                st.error("Insufficient Balance")
        else:
            st.error("Invalid credentials")


# ───────────────────────── FUND TRANSFER ─────────────────────────
elif menu == "Fund Transfer":
    st.subheader("🔁 Transfer Money")

    sender = st.text_input("Sender Account")
    pin = st.text_input("PIN", type="password")
    receiver = st.text_input("Receiver Account")
    amount = st.number_input("Amount", min_value=1.0)

    if st.button("Transfer"):
        accounts = load_accounts()
        transactions = load_transactions()

        s_mask = (accounts["Account_No"] == sender) & (accounts["PIN"] == pin)
        r_mask = accounts["Account_No"] == receiver

        if sender == receiver:
            st.error("Same account not allowed")
        elif not s_mask.any():
            st.error("Invalid sender")
        elif not r_mask.any():
            st.error("Invalid receiver")
        else:
            if accounts.loc[s_mask, "Balance"].iloc[0] >= amount:
                accounts.loc[s_mask, "Balance"] -= amount
                accounts.loc[r_mask, "Balance"] += amount

                save_accounts(accounts)

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                transactions = pd.concat([transactions, pd.DataFrame([
                    {"Account_No": sender, "Amount": amount, "Type": "Transfer Out", "Date": now},
                    {"Account_No": receiver, "Amount": amount, "Type": "Transfer In", "Date": now}
                ])], ignore_index=True)

                save_transactions(transactions)

                st.success("Transfer Successful")
            else:
                st.error("Insufficient balance")


# ───────────────────────── CHANGE PIN ─────────────────────────
elif menu == "Change PIN":
    st.subheader("🔐 Change PIN")

    acc = st.text_input("Account Number")
    old = st.text_input("Old PIN", type="password")
    new = st.text_input("New PIN", type="password")

    if st.button("Update"):
        accounts = load_accounts()

        mask = (accounts["Account_No"] == acc) & (accounts["PIN"] == old)

        if mask.any():
            accounts.loc[mask, "PIN"] = new
            save_accounts(accounts)
            st.success("PIN Updated")
        else:
            st.error("Invalid details")


# ───────────────────────── BALANCE ENQUIRY ─────────────────────────
elif menu == "Balance Enquiry":
    st.subheader("💳 Check Balance")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    if st.button("Check"):
        accounts = load_accounts()

        mask = (accounts["Account_No"] == acc) & (accounts["PIN"] == pin)

        if mask.any():
            st.metric("Balance", accounts.loc[mask, "Balance"].iloc[0])
        else:
            st.error("Invalid details")


# ───────────────────────── TRANSACTION HISTORY ─────────────────────────
elif menu == "Transaction History":
    st.subheader("📜 History")

    acc = st.text_input("Account Number")

    if st.button("Show"):
        transactions = load_transactions()

        user_tx = transactions[transactions["Account_No"] == acc]

        if len(user_tx) > 0:
            st.dataframe(user_tx)
        else:
            st.warning("No transactions found")

# FOOTER
st.divider()
st.markdown("""
<center>
<h4 style='color:#1E3A8A'>🏦 SBI Banking Management System</h4>
Developed using Python, Pandas, Streamlit & Plotly
</center>
""", unsafe_allow_html=True)