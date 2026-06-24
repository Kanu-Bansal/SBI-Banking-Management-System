# 🏦 SBI Banking Management System

A simple banking management dashboard built with **Streamlit** and **Pandas**. Manage accounts, deposits, withdrawals, fund transfers, PIN changes, and view transaction history — all from a single dashboard.

## Features

- 📊 **Dashboard** — view total accounts, total balance, total transactions, and charts of transaction activity
- 📝 **Create Account** — open a new account with name, email, phone, PIN, and opening balance
- 💰 **Deposit** — add money to an account
- 💸 **Withdraw** — withdraw money (with balance check)
- 🔁 **Fund Transfer** — transfer money between two accounts
- 🔐 **Change PIN** — update account PIN securely
- 💳 **Balance Enquiry** — check account balance
- 📜 **Transaction History** — view and download transaction statements as CSV

## Tech Stack

- [Streamlit](https://streamlit.io/) — web app framework
- [Pandas](https://pandas.pydata.org/) — data storage and manipulation (CSV-based)
- [Plotly](https://plotly.com/python/) — interactive charts

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/sbi-banking-app.git
   cd sbi-banking-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

The app will automatically create `bank.csv` and `transactions.csv` on first run to store data.

## Notes

- Account numbers are auto-generated in the format `SBI1001`, `SBI1002`, etc.
- PINs must be exactly 4 digits.
- Data is stored locally in CSV files (`bank.csv` and `transactions.csv`), which are git-ignored to avoid committing user data.

## Disclaimer

This is a learning/demo project and is **not intended for real banking use**. PINs and balances are stored in plain-text CSV files without encryption.
