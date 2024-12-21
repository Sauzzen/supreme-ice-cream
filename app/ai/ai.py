import pandas as pd
from groq import Groq

# Initialize Groq API client
client = Groq(api_key="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")

# Load datasets
budget_data = pd.read_csv('Budget.csv')
transactions_data = pd.read_csv('personal_transactions.csv')

# Suggested budget limits (in USD)
suggested_limits = [45, 140, 10, 80, 5, 30, 200, 300, 40, 1800, 160, 170, 2500, 25, 25, 260, 200, 12, 300]

# Conversion rate from USD to PHP
usd_to_php = 50

# Clean column names to avoid issues with spaces
budget_data.columns = budget_data.columns.str.strip()
transactions_data.columns = transactions_data.columns.str.strip()

# Convert suggested budget limits to PHP and update the BudgetLimit column
budget_data['BudgetLimit'] = [round(limit * usd_to_php, 2) for limit in suggested_limits]

# Save the updated budget file
budget_file_path = 'Budget_with_suggested_limits.csv'
budget_data.to_csv(budget_file_path, index=False)
print(f"Updated budget file saved as: {budget_file_path}")

# Check if 'Amount' column exists in transactions data and convert amounts to PHP
if 'Amount' in transactions_data.columns:
    transactions_data['Amount (PHP)'] = transactions_data['Amount'] * usd_to_php
else:
    print("Error: Column 'Amount' not found in the transactions data.")

# Save the updated transactions file
transactions_file_path = 'personal_transactions_converted.csv'
transactions_data.to_csv(transactions_file_path, index=False)
print(f"Updated transactions file saved as: {transactions_file_path}")

# Function to provide financial advice
def provide_financial_advice():
    print("\n=== Personalized Financial Advice ===")

    for category in budget_data['Category']:
        # Get actual spending for the current category and divide by 10
        actual_spending = transactions_data[transactions_data['Category'] == category]['Amount (PHP)'].sum() / 10

        # Check if the 'BudgetLimit' column exists and get the budget limit
        if 'BudgetLimit' in budget_data.columns:
            budget_limit_row = budget_data[budget_data['Category'] == category]
            if not budget_limit_row.empty:
                budget_limit = budget_limit_row['BudgetLimit'].values[0]
            else:
                print(f"\nWarning: No budget limit found for category '{category}'. Skipping...\n")
                continue
        else:
            print("\nError: 'BudgetLimit' column missing in the budget data.")
            return

        # Provide advice based on spending
        print(f"\nCategory: {category}")
        print(f"  - Actual Spending: ₱{actual_spending:.2f}")
        print(f"  - Budget Limit: ₱{budget_limit:.2f}")
        
        if actual_spending > budget_limit:
            print("  - Advice: You're overspending! Consider reducing expenses.\n")
        else:
            print("  - Advice: Good job staying within your budget!\n")

        # Use updated Groq API prompt for predictions
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Here is the actual spending data for the category '{category}': ₱{actual_spending:.2f}. "
                            "Please predict future spending for this category."
                        )
                    },
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            print(f"  - AI Prediction for category '{category}':")
            prediction = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                prediction += content
                print(content, end="")
            if not prediction.strip():
                print("\n  - AI Prediction: No prediction available.\n")

        except Exception as e:
            print(f"  - AI Prediction: Error fetching prediction: {e}\n")

# Run the program
if __name__ == "__main__":
    print("Welcome to the Personalized Financial Advisor!")
    while True:
        user_choice = input("Type 'advice' to get financial advice or 'exit' to quit: ").strip().lower()
        if user_choice == 'advice':
            provide_financial_advice()
        elif user_choice == 'exit':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please type 'advice' or 'exit'.")
