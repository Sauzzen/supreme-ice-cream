DROP TABLE IF EXISTS users;

DROP TABLE IF EXISTS names;

DROP TABLE IF EXISTS accounts;

DROP TABLE IF EXISTS transactions;

DROP TABLE IF EXISTS categories;

DROP TABLE IF EXISTS budgets;

DROP TABLE IF EXISTS debts;

DROP TABLE IF EXISTS bills;

-- Users table: Stores user information.
CREATE TABLE
  users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_id INTEGER NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (name_id) REFERENCES names (id)
  );

-- Name table: Stores user legal name
CREATE TABLE
  names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    no_middle_name INTEGER DEFAULT 0,
    last_name TEXT NOT NULL
  );

-- Accounts table: Tracks user accounts (e.g., individual, shared in future).
CREATE TABLE
  accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_name TEXT NOT NULL,
    account_type TEXT CHECK (account_type IN ("Credit", "Debit")) NOT NULL,
    balance REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (id)
  );

-- Transactions table: Logs all income, expenses, and debts.
CREATE TABLE
  transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    transaction_type TEXT NOT NULL,
    category_id TEXT NOT NULL, -- could use some check in whatnot
    transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
  );

-- Categories table: Predefined or user-defined categories for transactions.
CREATE TABLE
  categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
  );

-- Budgets table: Tracks user-defined budgets per category.
CREATE TABLE
  budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER UNIQUE NOT NULL,
    budget_limit REAL NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
  );

-- Debt table: Manages debts specifically (e.g., lender/borrower).
CREATE TABLE
  debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lender_name TEXT NOT NULL,
    amount REAL NOT NULL,
    due_date TEXT,
    is_paid INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id)
  );

-- Bills table: Tracks recurring or one-time bills for users.
CREATE TABLE
  bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    transaction_id INTEGER,
    bill_name TEXT NOT NULL,
    amount REAL NOT NULL,
    due_date TEXT NOT NULL,
    is_paid INTEGER DEFAULT 0, -- 0: Unpaid, 1: Paid
    payment_date TEXT, -- Optional: when the bill was paid
    FOREIGN KEY (account_id) REFERENCES accounts (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
  );