"""
PohonKu Internal Blockchain — DNS Token Ledger
SHA-256 hash chain untuk immutability transaksi DNS
"""
import hashlib, json
from datetime import datetime

DNS_TOTAL_SUPPLY = 1_000_000_000

def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def compute_block_hash(block_number: int, prev_hash: str,
                       sender: str, receiver: str,
                       amount: float, tx_type: str,
                       timestamp: str) -> str:
    payload = f"{block_number}|{prev_hash}|{sender}|{receiver}|{amount}|{tx_type}|{timestamp}"
    return _sha256(payload)

def genesis_hash() -> str:
    return _sha256("POHONKU_GENESIS_BLOCK_DNS_1000000000_ARBORIA")

def verify_chain(transactions) -> tuple[bool, int]:
    """
    Verifikasi integrity seluruh chain.
    Return: (is_valid, invalid_at_block)
    """
    if not transactions:
        return True, -1
    prev_hash = genesis_hash()
    for tx in sorted(transactions, key=lambda x: x.block_number):
        expected = compute_block_hash(
            tx.block_number, prev_hash,
            tx.sender_wallet or "SYSTEM",
            tx.receiver_wallet or "SYSTEM",
            tx.amount, tx.tx_type,
            tx.timestamp.isoformat()
        )
        if tx.block_hash != expected:
            return False, tx.block_number
        prev_hash = tx.block_hash
    return True, -1

def wallet_address(user_id: int, username: str) -> str:
    raw = f"PK-{user_id:04d}-{username}-ARBORIA"
    h = _sha256(raw)[:8].upper()
    return f"PK-{h}"
