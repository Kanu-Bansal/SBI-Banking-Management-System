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

# CUSTOM THEME
st.markdown("""
<style>

.main{
    background-color:#F5F7FA;
}

h1,h2,h3{
    color:#1E3A8A;
}

[data-testid="stSidebar"]{
    background-color:#1E3A8A;
}

[data-testid="stSidebar"] *{
    color:white;
}

.stButton > button{
    background-color:#1E3A8A;
    color:white;
    border:none;
    border-radius:10px;
    padding:10px;
    width:100%;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# CREATE FILES (PIN/Account_No forced to text so leading zeros are preserved)
if not os.path.exists("bank.csv"):
    pd.DataFrame(columns=[
        "Account_No", "PIN", "Name", "Email", "Phone", "Balance"
    ]).to_csv("bank.csv", index=False)

if not os.path.exists("transactions.csv"):
    pd.DataFrame(columns=[
        "Account_No", "Amount", "Type", "Date"
    ]).to_csv("transactions.csv", index=False)

accounts = pd.read_csv("bank.csv", dtype={"Account_No": str, "PIN": str})
transactions = pd.read_csv("transactions.csv", dtype={"Account_No": str})

# TITLE
st.title("🏦 SBI Banking Management System")

st.markdown("""
### Welcome to SBI Banking Portal

Manage accounts, deposits,
withdrawals and transactions
from one dashboard.
""")

# SIDEBAR
menu = st.sidebar.selectbox(
    "Select Service",
    [
        "Dashboard",
        "Create Account",
        "Deposit",
        "Withdraw",
        "Fund Transfer",
        "Change PIN",
        "Balance Enquiry",
        "Transaction History"
    ]
)

# DASHBOARD
if menu == "Dashboard":

    total_accounts = len(accounts)

    total_balance = (
        accounts["Balance"].sum()
        if len(accounts) > 0
        else 0
    )

    total_transactions = len(transactions)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("👤 Total Accounts", total_accounts)

    with c2:
        st.metric("💰 Total Balance", f"₹ {total_balance:,.0f}")

    with c3:
        st.metric("📈 Transactions", total_transactions)

    st.divider()

    if len(transactions) > 0:

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                transactions,
                names="Type",
                title="Transaction Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            summary = (
                transactions
                .groupby("Type")["Amount"]
                .sum()
                .reset_index()
            )

            fig2 = px.bar(
                summary,
                x="Type",
                y="Amount",
                title="Amount by Transaction Type"
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Recent Transactions")

    if len(transactions) > 0:
        st.dataframe(transactions.tail(10), use_container_width=True)
    else:
        st.info("No transactions yet.")

# CREATE ACCOUNT
elif menu == "Create Account":

    st.subheader("📝 Create New Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    pin = st.text_input("4 Digit PIN", type="password", max_chars=4)
    balance = st.number_input("Opening Balance", min_value=0.0, step=100.0)

    if st.button("Create Account"):

        if not name.strip():
            st.error("Name is required")

        elif "@" not in email or "." not in email:
            st.error("Enter a valid email address")

        elif len(phone) != 10 or not phone.isdigit():
            st.error("Phone number must be 10 digits")

        elif len(pin) != 4 or not pin.isdigit():
            st.error("PIN must be exactly 4 digits")

        elif pin in accounts["PIN"].values:
            st.error("This PIN is already in use. Choose a different one.")

        else:
            acc_no = "SBI" + str(1001 + len(accounts))

            new_account = pd.DataFrame([{
                "Account_No": acc_no,
                "PIN": pin,
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Balance": balance
            }])

            accounts = pd.concat([accounts, new_account], ignore_index=True)
            accounts.to_csv("bank.csv", index=False)

            st.success("✅ Account Created Successfully")
            st.info(f"Your Account Number: **{acc_no}**")

# DEPOSIT
elif menu == "Deposit":

    st.subheader("💰 Deposit Money")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password", max_chars=4)
    amount = st.number_input("Deposit Amount", min_value=1.0, step=100.0)

    if st.button("Deposit"):

        mask = (accounts["Account_No"] == acc) & (accounts["PIN"] == pin)

        if mask.any():
            accounts.loc[mask, "Balance"] += amount
            accounts.to_csv("bank.csv", index=False)

            tx = pd.DataFrame([{
                "Account_No": acc,
                "Amount": amount,
                "Type": "Deposit",
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            transactions = pd.concat([transactions, tx], ignore_index=True)
            transactions.to_csv("transactions.csv", index=False)

            new_balance = accounts.loc[mask, "Balance"].iloc[0]

            st.success("✅ Deposit Successful")
            st.metric("Updated Balance", f"₹ {new_balance:,.0f}")

        else:
            st.error("❌ Invalid Account Number or PIN")

# WITHDRAW
elif menu == "Withdraw":

    st.subheader("💸 Withdraw Money")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password", max_chars=4)
    amount = st.number_input("Withdraw Amount", min_value=1.0, step=100.0)

    if st.button("Withdraw"):

        mask = (accounts["Account_No"] == acc) & (accounts["PIN"] == pin)

        if mask.any():
            current_balance = accounts.loc[mask, "Balance"].iloc[0]

            if current_balance >= amount:
                accounts.loc[mask, "Balance"] -= amount
                accounts.to_csv("bank.csv", index=False)

                tx = pd.DataFrame([{
                    "Account_No": acc,
                    "Amount": amount,
                    "Type": "Withdraw",
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                transactions = pd.concat([transactions, tx], ignore_index=True)
                transactions.to_csv("transactions.csv", index=False)

                updated_balance = accounts.loc[mask, "Balance"].iloc[0]

                st.success("✅ Withdrawal Successful")
                st.metric("Remaining Balance", f"₹ {updated_balance:,.0f}")

            else:
                st.error("❌ Insufficient Balance")

        else:
            st.error("❌ Invalid Account Number or PIN")

# FUND TRANSFER
elif menu == "Fund Transfer":

    st.subheader("🔁 Fund Transfer")

    sender_acc = st.text_input("Your Account Number")
    sender_pin = st.text_input("Your PIN", type="password", max_chars=4)
    receiver_acc = st.text_input("Receiver Account Number")
    amount = st.number_input("Transfer Amount", min_value=1.0, step=100.0)

    if st.button("Transfer"):

        sender_mask = (accounts["Account_No"] == sender_acc) & (accounts["PIN"] == sender_pin)
        receiver_mask = accounts["Account_No"] == receiver_acc

        if sender_acc == receiver_acc:
            st.error("❌ Sender and receiver account cannot be the same")

        elif sender_mask.any() and receiver_mask.any():
            sender_balance = accounts.loc[sender_mask, "Balance"].iloc[0]

            if sender_balance >= amount:
                accounts.loc[sender_mask, "Balance"] -= amount
                accounts.loc[receiver_mask, "Balance"] += amount
                accounts.to_csv("bank.csv", index=False)

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                tx1 = pd.DataFrame([{
                    "Account_No": sender_acc, "Amount": amount,
                    "Type": "Transfer Out", "Date": now
                }])
                tx2 = pd.DataFrame([{
                    "Account_No": receiver_acc, "Amount": amount,
                    "Type": "Transfer In", "Date": now
                }])

                transactions = pd.concat([transactions, tx1, tx2], ignore_index=True)
                transactions.to_csv("transactions.csv", index=False)

                st.success("✅ Transfer Successful")
                st.metric("Remaining Balance", f"₹ {accounts.loc[sender_mask, 'Balance'].iloc[0]:,.0f}")

            else:
                st.error("❌ Insufficient Balance")

        else:
            st.error("❌ Invalid Sender or Receiver Account")

# CHANGE PIN
elif menu == "Change PIN":

    st.subheader("🔐 Change PIN")

    acc = st.text_input("Account Number")
    old_pin = st.text_input("Old PIN", type="password", max_chars=4)
    new_pin = st.text_input("New PIN (4 digits)", type="password", max_chars=4)

    if st.button("Update PIN"):

        mask = (accounts["Account_No"] == acc) & (accounts["PIN"] == old_pin)

        if mask.any():
            if len(new_pin) == 4 and new_pin.isdigit():
                if new_pin == old_pin:
                    st.error("❌ New PIN cannot be the same as old PIN")
                elif new_pin in accounts["PIN"].values:
                    st.error("❌ This PIN is already used by another account")
                else:
                    accounts.loc[mask, "PIN"] = new_pin
                    accounts.to_csv("bank.csv", index=False)
                    st.success("✅ PIN Updated Successfully")
            else:
                st.error("❌ New PIN must be 4 digits")

        else:
            st.error("❌ Invalid Account or Old PIN")

# BALANCE ENQUIRY
elif menu == "Balance Enquiry":

    st.subheader("💳 Balance Check")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password", max_chars=4)

    if st.button("Check Balance"):

        mask = (accounts["Account_No"] == acc) & (accounts["PIN"] == pin)

        if mask.any():
            balance = accounts.loc[mask, "Balance"].iloc[0]
            name = accounts.loc[mask, "Name"].iloc[0]

            st.success("✅ Balance Fetched Successfully")
            st.markdown(f"**Account Holder:** {name}")
            st.metric("Available Balance", f"₹ {balance:,.0f}")

        else:
            st.error("❌ Invalid Account or PIN")

# TRANSACTION HISTORY + DOWNLOAD
elif menu == "Transaction History":

    st.subheader("📜 Transaction History")

    acc = st.text_input("Enter Account Number")

    if st.button("Show History"):

        user_tx = transactions[transactions["Account_No"] == acc]

        if len(user_tx) > 0:
            st.dataframe(user_tx, use_container_width=True)

            csv = user_tx.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇ Download Statement (CSV)",
                data=csv,
                file_name=f"{acc}_statement.csv",
                mime="text/csv"
            )

        else:
            st.warning("No transactions found")
