from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import UserTable
from app.models.order_table import OrderTable
import re

def generate_user_id(db: Session, role: str) -> str:
    """
    Generates a sequential user ID based on role.
    admin -> admin_001
    employee -> emp_001
    """
    prefix = "admin_" if role == "admin" else "emp_"
    
    # Find the last ID with this prefix
    # casting might be tricky so we can just grab the max string that matches or filter first
    # For safety and database independence simplicity, we can query all or use regex if supported by DB specific
    # But for a simple approach:
    
    last_user = db.query(UserTable.user_id)\
        .filter(UserTable.user_id.like(f"{prefix}%"))\
        .order_by(UserTable.user_id.desc())\
        .first()

    if not last_user:
        return f"{prefix}001"
    
    last_id_str = last_user.user_id
    # Extract number part
    match = re.search(r"(\d+)$", last_id_str)
    if match:
        next_num = int(match.group(1)) + 1
        return f"{prefix}{next_num:03d}"
    else:
        # Fallback if pattern doesn't match well (though it should)
        return f"{prefix}001"

def generate_order_id(db: Session) -> str:
    """
    Generates a sequential order ID.
    ord_001
    """
    prefix = "ord_"
    
    last_order = db.query(OrderTable.order_id)\
        .filter(OrderTable.order_id.like(f"{prefix}%"))\
        .order_by(OrderTable.order_id.desc())\
        .first()

    if not last_order:
        return f"{prefix}001"
    
    last_id_str = last_order.order_id
    match = re.search(r"(\d+)$", last_id_str)
    if match:
        next_num = int(match.group(1)) + 1
        return f"{prefix}{next_num:03d}"
    else:
        return f"{prefix}001"
