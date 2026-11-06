import os

SYSTEM_PROMPT = """You are BankWise AI, an educational banking operations assistant.
Help explain general banking concepts, demo app workflows, transaction categories,
budgeting basics, and how to interpret the synthetic dashboard.
Never request passwords, OTPs, PINs, CVVs, full card numbers, or account credentials.
Do not claim to execute a real payment, approve a real loan, or access a real bank.
Do not provide individualized investment, tax, legal, or credit decisions.
Clearly state that all data in this application is synthetic when relevant."""

def ask_gemini(question, context=""):
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        return fallback_answer(question, context) + "\n\n*Tip: Add GOOGLE_API_KEY to your .env file to enable Gemini responses.*"
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0.25)
        prompt = f"{SYSTEM_PROMPT}\n\nDashboard context:\n{context}\n\nUser question: {question}"
        result = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
        return result.content
    except Exception as exc:
        return f"Gemini could not be reached ({type(exc).__name__}).\n\n{fallback_answer(question, context)}"

def fallback_answer(question, context=""):
    q = question.lower()
    if any(x in q for x in ["fraud","suspicious","risk"]):
        return ("BankWise AI marks demo transactions with a risk score of 75 or higher as flagged. "
                "Review the amount, channel, date and customer context before taking any action. "
                "A flag is only a review signal, not proof of fraud.")
    if any(x in q for x in ["loan","emi","interest"]):
        return ("The Loans module shows synthetic loan principal, interest rate, tenure and outstanding balance. "
                "For a real loan, compare the lender's official terms, fees and repayment schedule.")
    if any(x in q for x in ["balance","account","transaction"]):
        return ("Use Accounts to inspect demo account balances and Transactions to record simulated credits or debits. "
                "These operations update only the local demo database, not a real bank account.")
    return ("I can help explain the BankWise AI modules, synthetic banking data, transaction monitoring, "
            "basic banking terminology and dashboard insights. What would you like to explore?")
