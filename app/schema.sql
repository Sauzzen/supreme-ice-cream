DROP TABLE IF EXISTS user;

CREATE TABLE
  user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    first_name TEXT NOT NULL
  );

CREATE TABLE
  balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    balance INTEGER NOT NULL,
    currency TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    account_type TEXT CHECK (account_type IN "Savings", "Checking", "Credit") NOT NULL,
    status TEXT CHECK (status IN "Active", "Inactive", "Suspended") NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
  );