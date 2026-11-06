# 🏦 BankWise AI — AI Banking Management Assistant

BankWise AI is an educational banking operations dashboard built with **Python, Streamlit, SQLite, Plotly, LangChain and Google Gemini**. It combines everyday banking-management workflows with an AI assistant and a rules-based transaction monitoring demo.
# Public URL - https://bankwiseai-btutj4fuwnkq5w8rkfrbs7.streamlit.app/
> **Important:** This is a learning/demo application. It uses synthetic data, is not connected to any bank, does not process real payments, and must not be used to make actual lending, fraud, investment, or credit decisions.

## Features

- **Dashboard:** customer and account KPIs, deposit totals, transaction activity and recent transactions.
- **Account management:** inspect synthetic customer accounts and create new demo accounts.
- **Transactions:** record simulated credits and debits with balance checks.
- **Loan portfolio:** view demo loan principal, interest rate, tenure and outstanding amounts.
- **Card management:** inspect masked demo cards and change their demo status.
- **Fraud monitoring:** configurable threshold over a simple illustrative risk score.
- **Analytics:** channel, transaction-type and daily activity charts; CSV export.
- **AI assistant:** Gemini-powered Q&A when an API key is configured; useful fallback responses otherwise.
- **SQLite persistence:** demo records remain available locally between app runs.

## Tech stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Language | Python |
| Database | SQLite |
| Data analysis | Pandas |
| Visualizations | Plotly Express |
| Generative AI | Google Gemini via LangChain |
| Configuration | python-dotenv |

## Project structure

```text
BankWise_AI/
├── app.py
├── src/
│   ├── __init__.py
│   ├── ai.py
│   ├── database.py
│   └── ui.py
├── data/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/BankWise_AI.git
cd BankWise_AI
```

### 2. Create a virtual environment

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini (optional)

Copy `.env.example` to `.env` and add your Google Gemini API key:

```env
GOOGLE_API_KEY=your_actual_api_key
```

Without a key, the app still runs using built-in fallback assistant responses. Never commit `.env` or publish API keys.

### 5. Launch

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Demo data

The app creates a local SQLite database at `data/bankwise.db` and seeds synthetic customers, accounts, transactions, loans and cards on first launch. To reset the demo data, stop the app and delete `data/bankwise.db`; it will be recreated on the next launch.

## Deploy on Streamlit Community Cloud

1. Push the project to a GitHub repository.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create a new app and select the repository and `app.py`.
4. Add `GOOGLE_API_KEY` under the app's Secrets if Gemini is required.
5. Deploy.

The local SQLite database is intended for demos. Hosted ephemeral storage may reset, and SQLite is not suitable for a multi-user production banking service.

## Safety and limitations

- All seeded records are synthetic examples.
- Do not input real customer data or confidential financial information.
- No authentication, authorization, KYC, payment gateway, core banking integration, or audit-grade controls are implemented.
- The transaction risk score is a deliberately simple illustrative rule, not a validated fraud model.
- The assistant is informational and can make mistakes. It must not be treated as financial, legal, tax, investment, or credit advice.
- A production banking system would require security engineering, encryption, access controls, secure secrets management, audit logging, compliance review, monitoring, resilience testing and professional domain validation.

## Future enhancements

- Role-based access control and audit logs.
- Advanced anomaly detection trained on approved, properly governed data.
- Multi-factor authentication for a secure test environment.
- Loan EMI calculator and configurable repayment schedules.
- Retrieval-augmented generation over approved banking policy documents.
- PostgreSQL deployment and automated tests.

## Acknowledgements

Built as an educational project to explore Python application development, data analytics, database integration and Generative AI.
