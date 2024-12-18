from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

from datetime import date

bp = Blueprint("dashboard", __name__)


def get_user(id):
    user = (
        get_db()
        .execute(
            "SELECT u.id, name_id, username, email, password, first_name, middle_name, no_middle_name, last_name"
            " FROM users u JOIN names n ON u.name_id = n.id"
            " WHERE u.id = ?",
            (id,),
        )
        .fetchone()
    )

    if user is None:
        abort(404, f"User id {id} doesn't exist.")

    return user


@bp.route("/<int:id>/update_profile", methods=("GET", "POST"))
@login_required
def update_profile(id):
    user = get_user(id)

    if request.method == "POST":
        username = request.form["username"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        no_middle_name = "no_middle_name" in request.form
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        error = None

        if not username:
            error = "Username is required."
        elif not first_name:
            error = "First Name is required"
        elif no_middle_name == False and not middle_name:
            error = "Middle Name is required"
        elif no_middle_name and middle_name:
            error = "I thought you have no middle name?"
        elif not last_name:
            error = "Last Name is required"
        elif not password or not confirm_password:
            error = "Password and Confirmation are required."
        elif password != confirm_password:
            error = "Passwords doesn't match."

        if error is not None:
            flash(error)
        else:
            try:
                db = get_db()
                db.execute("BEGIN TRANSACTION")
                db.execute(
                    "UPDATE names SET first_name = ?, middle_name = ?, no_middle_name = ?, last_name = ?"
                    " WHERE id = ?",
                    (
                        first_name,
                        middle_name,
                        no_middle_name,
                        last_name,
                        user["name_id"],
                    ),
                )
                db.execute(
                    "UPDATE users SET username = ?, email = ?, password = ?"
                    " WHERE id = ?",
                    (username, email, password, id),
                )
                db.commit()
                db.rollback()
            except:
                pass
            else:
                return redirect(url_for("dashboard.index"))

    return render_template("dashboard/update_profile.html", user=user)


@bp.route("/")
@login_required
def index():
    db = get_db()

    name = db.execute(
        "SELECT s.id, name_id, first_name, last_name FROM users s JOIN names n ON s.name_id = n.id WHERE s.id = ?",
        (g.user["id"],),
    ).fetchone()

    accounts = db.execute(
        "SELECT a.id, account_name, account_type, balance FROM accounts a JOIN users u ON a.user_id = u.id WHERE u.id = ?",
        (g.user["id"],),
    ).fetchall()

    transactions = db.execute(
        "SELECT t.id, amount, transaction_type, category, description, transaction_date FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE a.user_id = ? ORDER BY transaction_date DESC",
        (g.user["id"],),
    ).fetchmany(3)

    bills = db.execute(
        "SELECT b.id, bill_name, amount, due_date FROM bills b JOIN users u ON b.user_id = u.id WHERE u.id = ?",
        (g.user["id"],),
    ).fetchall()

    return render_template(
        "dashboard/index.html",
        name=name,
        accounts=accounts,
        transactions=transactions,
        bills=bills,
    )


# TODO: do this
@bp.route("/settings")
@login_required
def settings():
    return "settings"


@bp.route("/budget")
@login_required
def budget():
    return "budget"


@bp.route("/wallet")
@login_required
def wallet():
    return "wallet"


# Transactions


@bp.route("/transactions")
@login_required
def transactions():
    db = get_db()

    name = db.execute(
        "SELECT s.id, name_id, first_name, last_name FROM users s JOIN names n ON s.name_id = n.id WHERE s.id = ?",
        (g.user["id"],),
    ).fetchone()

    transactions = db.execute(
        "SELECT t.id, amount, transaction_type, category, description, transaction_date FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE a.user_id = ? ORDER BY transaction_date DESC",
        (g.user["id"],),
    ).fetchall()

    accounts = db.execute(
        "SELECT a.id, account_name, account_type, balance FROM accounts a JOIN users u ON a.user_id = u.id WHERE u.id = ?",
        (g.user["id"],),
    ).fetchall()

    return render_template(
        "dashboard/transactions.html",
        transactions=transactions,
        name=name,
        accounts=accounts,
    )


@bp.route("/add_transaction", methods=("POST",))
@login_required
def add_transaction():
    account_id = request.form["account_id"]
    amount = request.form["amount"]
    transaction_type = request.form["transaction_type"]
    category = request.form["category"]
    description = request.form["description"]
    db = get_db()
    error = None

    if not account_id:
        error = "Account is required"
    elif not amount:
        error = "Amount is required"
    elif not transaction_type:
        error = "Transaction Type is required"
    elif not category:
        error = "Category is required"

    if error is None:
        try:
            db.execute("BEGIN TRANSACTION")
            db.execute(
                "INSERT INTO transactions (account_id, amount, transaction_type, category, description) VALUES (?, ?, ?, ?, ?)",
                (account_id, amount, transaction_type, category, description),
            )
            account_balance = db.execute(
                "SELECT balance FROM accounts WHERE id = ?",
                (account_id,),
            ).fetchone()
            db.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (
                    account_balance[0] + float(amount),
                    account_id,
                ),
            )
            db.commit()
            db.rollback()
        except db.IntegrityError:
            error = f"Error"
        else:
            return redirect(url_for("dashboard.transactions"))

    flash(error)
    return redirect(url_for("dashboard.transactions"))


def get_transaction(id):
    transaction = (
        get_db()
        .execute(
            "SELECT * FROM transactions" " WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if transaction is None:
        abort(404, f"Transaction id {id} doesn't exist.")

    return transaction


@bp.route("/<int:id>/update_transaction", methods=("GET", "POST"))
@login_required
def update_transaction(id):
    transaction = get_transaction(id)  # Get the current transaction
    db = get_db()

    # Fetch user details and accounts
    name = db.execute(
        "SELECT s.id, name_id, first_name, last_name "
        "FROM users s JOIN names n ON s.name_id = n.id "
        "WHERE s.id = ?",
        (g.user["id"],),
    ).fetchone()

    transactions = db.execute(
        "SELECT t.id, amount, transaction_type, category, description, transaction_date FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE a.user_id = ? ORDER BY transaction_date DESC",
        (g.user["id"],),
    ).fetchall()

    accounts = db.execute(
        "SELECT a.id, account_name, account_type, balance "
        "FROM accounts a JOIN users u ON a.user_id = u.id "
        "WHERE u.id = ?",
        (g.user["id"],),
    ).fetchall()

    if request.method == "POST":
        account_id = request.form["account_id"]
        amount = request.form["amount"]
        transaction_type = request.form["transaction_type"]
        category = request.form["category"]
        description = request.form["description"]
        error = None

        # Validate inputs
        if not account_id:
            error = "Account is required."
        elif not amount:
            error = "Amount is required."
        elif not transaction_type:
            error = "Transaction Type is required."
        elif not category:
            error = "Category is required."
        try:
            amount = float(amount)  # Ensure amount is numeric
        except ValueError:
            error = "Amount must be a valid number."

        if error is not None:
            flash(error)
        else:
            try:
                db.execute("BEGIN TRANSACTION")  # Start transaction

                # Restore balance for the original account
                original_balance = db.execute(
                    "SELECT balance FROM accounts WHERE id = ?",
                    (transaction["account_id"],),
                ).fetchone()
                if original_balance:
                    db.execute(
                        "UPDATE accounts SET balance = ? WHERE id = ?",
                        (
                            original_balance[0] - float(transaction["amount"]),
                            transaction["account_id"],
                        ),
                    )

                # Update the new account balance
                new_account_balance = db.execute(
                    "SELECT balance FROM accounts WHERE id = ?",
                    (account_id,),
                ).fetchone()
                if new_account_balance:
                    db.execute(
                        "UPDATE accounts SET balance = ? WHERE id = ?",
                        (new_account_balance[0] + amount, account_id),
                    )

                # Update the transaction details
                db.execute(
                    "UPDATE transactions SET account_id = ?, amount = ?, transaction_type = ?, category = ?, description = ? "
                    "WHERE id = ?",
                    (account_id, amount, transaction_type, category, description, id),
                )
                db.commit()  # Commit changes
            except Exception as e:
                db.rollback()  # Rollback on error
                error = f"An error occurred: {str(e)}"
                flash(error)
            else:
                return redirect(url_for("dashboard.transactions"))

    return render_template(
        "dashboard/update_transaction.html",
        id=id,
        transaction=transaction,
        transactions=transactions,
        name=name,
        accounts=accounts,
    )


@bp.route("/<int:id>/delete_transaction", methods=("GET", "POST"))
@login_required
def delete_transaction(id):
    transaction = get_transaction(id)
    db = get_db()
    db.execute("BEGIN TRANSACTION")
    account_balance = db.execute(
        "SELECT balance FROM accounts WHERE id = ?",
        (transaction["account_id"],),
    ).fetchone()
    db.execute(
        "UPDATE accounts SET balance = ? WHERE id = ?",
        (account_balance[0] - float(transaction["amount"]), transaction['account_id']),
    )
    db.execute("DELETE FROM transactions WHERE id = ?", (id,))
    db.commit()
    db.rollback()
    return redirect(url_for("dashboard.transactions"))


# Bills


@bp.route("/bills")
@login_required
def bills():
    db = get_db()

    name = db.execute(
        "SELECT s.id, name_id, first_name, last_name FROM users s JOIN names n ON s.name_id = n.id WHERE s.id = ?",
        (g.user["id"],),
    ).fetchone()

    bills = db.execute(
        "SELECT * FROM bills WHERE user_id = ?",
        (g.user["id"],),
    ).fetchall()

    accounts = db.execute(
        "SELECT a.id, account_name, account_type, balance FROM accounts a JOIN users u ON a.user_id = u.id WHERE u.id = ?",
        (g.user["id"],),
    ).fetchall()

    return render_template(
        "dashboard/bills.html",
        bills=bills,
        name=name,
        accounts=accounts,
    )


@bp.route("/add_bill", methods=("POST",))
@login_required
def add_bill():
    user_id = g.user["id"]
    account_id = request.form["account_id"]
    category_name = request.form["category_name"]
    bill_name = request.form["bill_name"]
    amount = request.form["amount"]
    due_date = request.form["due_date"]
    is_recurring = request.form["is_recurring"]
    frequency = request.form["frequency"]
    is_paid = request.form["is_paid"]
    db = get_db()
    error = None

    category = db.execute(
        "SELECT COUNT(*) FROM categories WHERE category_name = ?", (category_name,)
    ).fetchone()

    if category[0] == 0:
        db.execute(
            "INSERT INTO categories (category_name) VALUES (?)",
            (category_name,),
        )
        category_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    else:
        category_id = db.execute("SELECT id from categories WHERE category_name = ?", (category_name,)).fetchone()

    if not account_id:
        error = "Account is required"
    elif not category_name:
        error = "Category Name is required"
    elif not bill_name:
        error = "Bill Name is required"
    elif not due_date:
        error = "Due Date is required"

    if error is None:
        try:
            if is_paid == 1:
                db.execute(
                    "INSERT INTO transactions (account_id, amount, transaction_type, category, description) VALUES (?, ?, ?, ?, ?)",
                    (
                        account_id,
                        -1 * amount,
                        "Bill Payment",
                        category_name,
                        f"Payment of bill: {bill_name}",
                    ),
                )
                payment_date = date.today().strftime("%Y-%m-%d")
            else:
                payment_date = None
            transaction_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute(
                "INSERT INTO bills (user_id, account_id, category_id, transaction_id, bill_name, amount, due_date, is_recurring, frequency, is_paid, payment_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    account_id,
                    category_id,
                    transaction_id,
                    bill_name,
                    amount,
                    due_date,
                    is_recurring,
                    frequency,
                    is_paid,
                    payment_date,
                ),
            )
            db.commit()
        except db.IntegrityError:
            error = f"Error"
        else:
            return redirect(url_for("dashboard.bills"))

    flash(error)
    return redirect(url_for("dashboard.bills"))


def get_bill(id):
    bill = (
        get_db()
        .execute(
            "SELECT * FROM bills WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if bill is None:
        abort(404, f"Transaction id {id} doesn't exist.")

    return bill


@bp.route("/<int:id>/update_bill", methods=("GET", "POST"))
@login_required
def update_bill(id):
    bill = get_bill(id)  # Get the current transaction
    db = get_db()

    # Fetch user details and accounts
    name = db.execute(
        "SELECT s.id, name_id, first_name, last_name "
        "FROM users s JOIN names n ON s.name_id = n.id "
        "WHERE s.id = ?",
        (g.user["id"],),
    ).fetchone()

    bills = db.execute(
        "SELECT * FROM bills WHERE user_id = ?",
        (g.user["id"],),
    ).fetchall()

    accounts = db.execute(
        "SELECT a.id, account_name, account_type, balance "
        "FROM accounts a JOIN users u ON a.user_id = u.id "
        "WHERE u.id = ?",
        (g.user["id"],),
    ).fetchall()

    if request.method == "POST":
        account_id = request.form["account_id"]
        category_name = request.form["category_name"]
        bill_name = request.form["bill_name"]
        amount = request.form["amount"]
        due_date = request.form["due_date"]
        is_recurring = request.form["is_recurring"]
        frequency = request.form["frequency"]
        is_paid = request.form["is_paid"]
        error = None

        category = db.execute(
            "SELECT COUNT(*) FROM categories WHERE category_name = ?", (category_name,)
        ).fetchone()

        if category[0] == 0:
            db.execute(
                "INSERT INTO categories (category_name) VALUES (?)",
                (category_name,),
            )
            category_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        else:
            category_id = db.execute("SELECT id from categories WHERE category_name = ?", (category_name,)).fetchone()

        # Validate inputs
        if not account_id:
            error = "Account is required"
        elif not category_name:
            error = "Category Name is required"
        elif not bill_name:
            error = "Bill Name is required"
        elif not due_date:
            error = "Due Date is required"

        if error is not None:
            flash(error)
        else:
            try:
                db.execute("BEGIN TRANSACTION")  # Start transaction

                # Restore balance for the original account
                original_balance = db.execute(
                    "SELECT balance FROM accounts WHERE id = ?",
                    (bill["account_id"],),
                ).fetchone()
                if original_balance and bill["is_paid"] == 1:
                    db.execute(
                        "DELETE FROM transactions WHERE id = ?",
                        (bill["transaction_id"],),
                    )

                # Update the new account balance
                new_account_balance = db.execute(
                    "SELECT balance FROM accounts WHERE id = ?",
                    (account_id,),
                ).fetchone()
                if new_account_balance and is_paid == 1:
                    db.execute(
                        "INSERT INTO transactions (account_id, amount, transaction_type, category, description) VALUES (?, ?, ?, ?, ?)",
                        (
                            account_id,
                            -1 * amount,
                            "Bill Payment",
                            category_name,
                            f"Payment of bill: {bill_name}",
                        ),
                    )
                    payment_date = date.today().strftime("%Y-%m-%d")
                    transaction_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                elif is_paid == 0:
                    payment_date = None
                    transaction_id = None

                # Update the transaction details
                db.execute(
                    "UPDATE bills SET user_id = ?, account_id = ?, category_id = ?, transaction_id = ?, bill_name = ?, amount = ?, due_date = ?, is_recurring = ?, frequency = ?, is_paid = ?, payment_date = ?"
                    " WHERE id = ?",
                    (g.user['id'], account_id, category_id, transaction_id, bill_name, amount, due_date, is_recurring, frequency, is_paid, payment_date, id),
                )
                db.commit()  # Commit changes
            except Exception as e:
                db.rollback()  # Rollback on error
                error = f"An error occurred: {str(e)}"
                flash(error)
            else:
                return redirect(url_for("dashboard.bills"))

    return render_template(
        "dashboard/update_bill.html",
        id=id,
        bill=bill,
        bills=bills,
        name=name,
        accounts=accounts,
    )


@bp.route("/<int:id>/delete_bill", methods=("GET", "POST"))
@login_required
def delete_bill(id):
    bill = get_bill(id)
    db = get_db()
    db.execute("DELETE FROM bills WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("dashboard.bills"))
