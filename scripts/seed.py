from app.db import get_db, init_db


def seed():
    print("Seeding demo database...")
    init_db()
    db = get_db()

    db.execute("DELETE FROM transactions")
    db.execute("DELETE FROM accounts")

    accounts = [
        {"id": 1, "owner": "Alice Johnson", "balance": 50000.0, "type": "checking"},
        {"id": 2, "owner": "Bob Smith", "balance": 120000.0, "type": "savings"},
        {"id": 3, "owner": "Charlie Brown", "balance": 75000.0, "type": "checking"},
        {"id": 4, "owner": "Diana Martinez", "balance": 34500.0, "type": "checking"},
        {"id": 5, "owner": "Edward Kim", "balance": 89000.0, "type": "savings"},
    ]

    transactions = [
        {"from": 1, "to": 2, "amount": 2500.0, "memo": "Monthly rent", "status": "completed"},
        {"from": 3, "to": 1, "amount": 15000.0, "memo": "Invoice #4521", "status": "completed"},
        {"from": 2, "to": 3, "amount": 500.0, "memo": "Dinner reimbursement", "status": "completed"},
        {"from": 1, "to": 4, "amount": 1200.0, "memo": "Consulting fee", "status": "completed"},
        {"from": 5, "to": 1, "amount": 8500.0, "memo": "Q3 dividend", "status": "completed"},
        {"from": 4, "to": 2, "amount": 3200.0, "memo": "Equipment purchase", "status": "completed"},
        {"from": 3, "to": 5, "amount": 45000.0, "memo": "Investment transfer", "status": "completed"},
        {"from": 2, "to": 4, "amount": 750.0, "memo": "Software subscription", "status": "pending"},
    ]

    for acc in accounts:
        db.execute(
            "INSERT OR REPLACE INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
            [acc["id"], acc["owner"], acc["balance"], acc["type"]],
        )

    for tx in transactions:
        db.execute(
            "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
            [tx["from"], tx["to"], tx["amount"], tx["memo"], tx["status"]],
        )

    db.commit()
    print(f"Seeded {len(accounts)} accounts, {len(transactions)} transactions.")


if __name__ == "__main__":
    seed()
