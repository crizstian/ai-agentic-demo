from app.db import get_db, init_db


def seed():
    print("Seeding demo database...")
    init_db()
    db = get_db()

    accounts = [
        {"id": "DEMO-001", "owner": "Alice Demo", "balance": 12450.0, "type": "checking"},
        {"id": "DEMO-002", "owner": "Bob Demo", "balance": 3200.5, "type": "savings"},
        {"id": "DEMO-003", "owner": "Charlie Demo", "balance": 87500.0, "type": "checking"},
    ]

    transactions = [
        {"from": "DEMO-001", "to": "DEMO-002", "amount": 250.0, "memo": "Rent split", "status": "completed"},
        {"from": "DEMO-003", "to": "DEMO-001", "amount": 1200.0, "memo": "Invoice payment", "status": "completed"},
        {"from": "DEMO-002", "to": "DEMO-003", "amount": 50.0, "memo": "Lunch", "status": "completed"},
        {"from": "DEMO-001", "to": "DEMO-003", "amount": -10.0, "memo": "Bad transfer demo", "status": "pending"},
        {"from": "DEMO-002", "to": "DEMO-001", "amount": 999.99, "memo": "Refund", "status": "completed"},
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
    print("Demo data seeded successfully.")


if __name__ == "__main__":
    seed()
