def calculate_sacs(inflow, outflow):
    """Calculate SACS (Simple Automated Cash Flow) values"""
    # The excess is the core metric for the SACS long-term growth projection
    excess = inflow - outflow
    return {
        'inflow': inflow,
        'outflow': outflow,
        'excess': excess
    }

def calculate_private_reserve_target(monthly_expenses, insurance_deductibles=0):
    """Private Reserve Target = (6 x monthly expenses) + insurance deductibles"""
    # Industry standard: 6 months of expenses + any known insurance deductibles
    target = (6 * monthly_expenses) + insurance_deductibles
    return target

def calculate_tcc(balances):
    """
    Calculate TCC (Total Client Chart) values
    Rules from PRD:
    - Client 1 Retirement Total = sum of Client 1 retirement accounts
    - Client 2 Retirement Total = sum of Client 2 retirement accounts
    - Non-Retirement Total = sum of non-retirement accounts (NOT including trust)
    - Grand Total = Client1 Retirement + Client2 Retirement + Non-Retirement + Trust
    - Liabilities = displayed separately, NOT subtracted from net worth
    """
    client1_retirement = 0
    client2_retirement = 0
    non_retirement = 0
    trust = 0
    liabilities = 0

    # Initialize lists to categorize accounts for the UI rendering
    retirement_accounts = []
    non_retirement_accounts = []
    trust_accounts = []
    liability_accounts = []

    # Iterate through all raw balances and categorize them based on type and ownership
    for b in balances:
        category = b['account_category']
        owner = b['owner']
        # Fallback to 0 if balance is missing to prevent math errors
        balance = b['balance'] or 0

        if category == 'retirement':
            # Retirement accounts must be strictly isolated by individual owner
            if owner == 'client1':
                client1_retirement += balance
            else:
                client2_retirement += balance
            retirement_accounts.append(dict(b))

        elif category == 'non_retirement':
            # Non-retirement groups both individual and joint accounts
            non_retirement += balance
            non_retirement_accounts.append(dict(b))

        elif category == 'trust':
            # Trust assets (usually real estate) are kept separate from liquid non-retirement
            trust += balance
            trust_accounts.append(dict(b))

        elif category == 'liability':
            # Liabilities are tracked but MUST NOT be subtracted from the net worth totals
            liabilities += balance
            liability_accounts.append(dict(b))

    # Grand Total aggregates all positive assets (ignoring liabilities per PRD)
    grand_total = client1_retirement + client2_retirement + non_retirement + trust

    return {
        'client1_retirement': client1_retirement,
        'client2_retirement': client2_retirement,
        'non_retirement': non_retirement,
        'trust': trust,
        'liabilities': liabilities,
        'grand_total': grand_total,
        'retirement_accounts': retirement_accounts,
        'non_retirement_accounts': non_retirement_accounts,
        'trust_accounts': trust_accounts,
        'liability_accounts': liability_accounts
    }

def format_currency(amount):
    """Format number as currency string"""
    # Handle None values gracefully to prevent UI crashes
    if amount is None:
        return '$0'
    return '${:,.0f}'.format(amount)