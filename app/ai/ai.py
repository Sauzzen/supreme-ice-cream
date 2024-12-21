import pandas as pd
import pickle

# Constants
USD_TO_PHP = 50

# Suggested budget limits (in USD, divided by 10)
SUGGESTED_LIMITS = [limit / 10 for limit in [450, 1400, 100, 800, 50, 300, 2000, 3000, 400, 18000, 1600, 1700, 25000, 250, 250, 2600, 2000, 120, 3000]]

# Function to save the model to a .obj file
def save_model(budget_data, transactions_data, filename='financial_advisor_model.obj'):
    model_data = {
        "budget_data": budget_data,
        "transactions_data": transactions_data,
        "usd_to_php": USD_TO_PHP,
        "suggested_limits": SUGGESTED_LIMITS,
    }
    with open(filename, 'wb') as file:
        pickle.dump(model_data, file)
    print(f"Model saved as '{filename}'")

# Function to load the model from a .obj file
def load_model(filename='financial_advisor_model.obj'):
    with open(filename, 'rb') as file:
        return pickle.load(file)

# Function to provide financial advice
def provide_financial_advice(budget_data, transactions_data):
    print("\n=== Personalized Financial Advice ===")
    for category in budget_data['Category']:
        # Get actual spending for the current category
        actual_spending = transactions_data[transactions_data['Category'] == category]['Amount (PHP)'].sum()

        # Check if the 'BudgetLimit' column exists and get the budget limit
        if 'BudgetLimit' in budget_data.columns:
            budget_limit_row = budget_data[budget_data['Category'] == category]
            if not budget_limit_row.empty:
                budget_limit = budget_limit_row['BudgetLimit'].values[0]
            else:
                print(f"Warning: No budget limit found for category '{category}'. Skipping...\n")
                continue
        else:
            print("Error: 'BudgetLimit' column missing in the budget data.")
            return

        # Provide advice based on spending
        if actual_spending > budget_limit:
            print(f"Category: {category}")
            print(f"  - Actual Spending: ₱{actual_spending:.2f}")
            print(f"  - Budget Limit: ₱{budget_limit:.2f}")
            print("  - Advice: You're overspending! Consider reducing expenses.\n")
        else:
            print(f"Category: {category}")
            print(f"  - Actual Spending: ₱{actual_spending:.2f}")
            print(f"  - Budget Limit: ₱{budget_limit:.2f}")
            print("  - Advice: Good job staying within your budget!\n")

# Main Program
if __name__ == "__main__":
    print("Welcome to the Personalized Financial Advisor!")
    
    # Load datasets
    budget_data = pd.read_csv('Budget.csv')
    transactions_data = pd.read_csv('personal_transactions.csv')

    # Clean column names to avoid issues with spaces
    budget_data.columns = budget_data.columns.str.strip()
    transactions_data.columns = transactions_data.columns.str.strip()

    # Update budget data with converted limits
    budget_data['BudgetLimit'] = [round(limit * USD_TO_PHP, 2) for limit in SUGGESTED_LIMITS]

    # Update transactions data with converted amounts
    if 'Amount' in transactions_data.columns:
        transactions_data['Amount (PHP)'] = transactions_data['Amount'] * USD_TO_PHP / 10
    else:
        print("Error: Column 'Amount' not found in the transactions data.")
    
    # Save updated datasets
    budget_data.to_csv('Budget_with_suggested_limits.csv', index=False)
    transactions_data.to_csv('personal_transactions_converted.csv', index=False)
    print("Updated datasets saved.")

    # Save the model
    save_model(budget_data, transactions_data)

    # Main loop
    while True:
        user_choice = input("Type 'advice' to get financial advice, 'load' to reload the model, or 'exit' to quit: ").strip().lower()
        if user_choice == 'advice':
            provide_financial_advice(budget_data, transactions_data)
        elif user_choice == 'load':
            loaded_model = load_model()
            budget_data = loaded_model['budget_data']
            transactions_data = loaded_model['transactions_data']
            print("Model reloaded successfully!")
        elif user_choice == 'exit':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please type 'advice', 'load', or 'exit'.")
