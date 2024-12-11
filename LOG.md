## 12/10/2024 - 10:16 PM
### Modified app/schema.sql
```
last_name TEXT NOT NULL,
middle_name TEXT,
first_name TEXT NOT NULL

currency TEXT NOT NULL,
last_updated TEXT NOT NULL,
account_type TEXT CHECK (account_type IN "Savings", "Checking", "Credit") NOT NULL,
status TEXT CHECK (status IN "Active", "Inactive", "Suspended") NOT NULL,

P.S. Edit the htmls and the app/auth.py
```

try