from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user, require_admin
from app.models.user import UserTable
from app.models.employee_scan_log import EmployeeScanLog
from app.models.order_table import OrderTable
from app.models.product import Product
from app.models.notification import Notification
from app.schemas.employee_schema import EmployeeCreateRequest, EmployeeCreateResponse
from app.core.security import hash_password
from app.core.id_generator import generate_user_id
from sqlalchemy import func

router = APIRouter()


@router.post("/create", response_model=EmployeeCreateResponse)
def create_employee(
    payload: EmployeeCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(require_admin)
):
    """Create a new employee account"""
    # Check if username already exists
    existing = db.query(UserTable).filter(UserTable.user_username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    # Generate employee ID
    employee_id = generate_user_id(db, "employee")
    
    # Create new employee
    new_employee = UserTable(
        user_id=employee_id,
        user_username=payload.username,
        user_password=hash_password(payload.password),
        role="employee"
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return EmployeeCreateResponse(
        employee_id=new_employee.user_id,
        username=new_employee.user_username,
        message="Employee created successfully"
    )


@router.get("/employees")
def get_all_employees(
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(require_admin)
):
    """Get all employees with their statistics"""
    employees = db.query(UserTable).filter(UserTable.role == "employee").all()
    
    result = []
    for emp in employees:
        # Get scan logs count
        scans_count = db.query(func.count(EmployeeScanLog.scan_id)).filter(
            EmployeeScanLog.employee_id == emp.user_id
        ).scalar() or 0
        
        # Get completed orders count (orders that this employee worked on and are completed)
        completed_orders = db.query(func.count(func.distinct(EmployeeScanLog.order_id))).join(
            OrderTable, EmployeeScanLog.order_id == OrderTable.order_id
        ).filter(
            EmployeeScanLog.employee_id == emp.user_id,
            OrderTable.status == "COMPLETED"
        ).scalar() or 0
        
        result.append({
            "employee_id": emp.user_id,
            "username": emp.user_username,
            "role": emp.role,
            "created_at": emp.created_at,
            "items_scanned": scans_count,
            "orders_completed": completed_orders,
            "status": "active"  # You can add a status field to UserTable if needed
        })
    
    return result


@router.get("/employees/{employee_id}")
def get_employee_detail(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(require_admin)
):
    """Get detailed information about a specific employee"""
    employee = db.query(UserTable).filter(
        UserTable.user_id == employee_id,
        UserTable.role == "employee"
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get scan logs count
    scans_count = db.query(func.count(EmployeeScanLog.scan_id)).filter(
        EmployeeScanLog.employee_id == employee.user_id
    ).scalar() or 0

    total_inventory_updated = db.query(func.coalesce(func.sum(EmployeeScanLog.scanned_quantity), 0)).filter(
        EmployeeScanLog.employee_id == employee.user_id
    ).scalar() or 0
    
    # Get completed orders count
    completed_orders = db.query(func.count(func.distinct(EmployeeScanLog.order_id))).join(
        OrderTable, EmployeeScanLog.order_id == OrderTable.order_id
    ).filter(
        EmployeeScanLog.employee_id == employee.user_id,
        OrderTable.status == "COMPLETED"
    ).scalar() or 0
    
    # Get recent scan logs
    recent_scans = db.query(EmployeeScanLog).filter(
        EmployeeScanLog.employee_id == employee.user_id
    ).order_by(EmployeeScanLog.scanned_at.desc()).limit(10).all()

    scanned_products = db.query(
        EmployeeScanLog.product_id,
        Product.item_name,
        Product.size,
        func.sum(EmployeeScanLog.scanned_quantity).label("total_scanned"),
        func.max(EmployeeScanLog.scanned_at).label("last_scanned_at"),
    ).join(
        Product, Product.product_id == EmployeeScanLog.product_id
    ).filter(
        EmployeeScanLog.employee_id == employee.user_id
    ).group_by(
        EmployeeScanLog.product_id,
        Product.item_name,
        Product.size,
    ).order_by(
        func.max(EmployeeScanLog.scanned_at).desc()
    ).all()

    scanned_orders = db.query(
        EmployeeScanLog.order_id,
        OrderTable.client_name,
        OrderTable.status,
        func.count(EmployeeScanLog.scan_id).label("scan_events"),
        func.sum(EmployeeScanLog.scanned_quantity).label("total_scanned"),
        func.max(EmployeeScanLog.scanned_at).label("last_scanned_at"),
    ).join(
        OrderTable, OrderTable.order_id == EmployeeScanLog.order_id
    ).filter(
        EmployeeScanLog.employee_id == employee.user_id
    ).group_by(
        EmployeeScanLog.order_id,
        OrderTable.client_name,
        OrderTable.status,
    ).order_by(
        func.max(EmployeeScanLog.scanned_at).desc()
    ).all()

    inventory_updates = db.query(
        Notification.notification_id,
        Notification.title,
        Notification.message,
        Notification.reference_id,
        Notification.created_at,
        Product.item_name,
        Product.size,
    ).outerjoin(
        Product, Product.product_id == Notification.reference_id
    ).filter(
        Notification.actor_user_id == employee.user_id,
        Notification.type == "inventory_update",
    ).order_by(
        Notification.created_at.desc()
    ).limit(50).all()

    products_added_count = db.query(
        func.count(func.distinct(Notification.reference_id))
    ).filter(
        Notification.actor_user_id == employee.user_id,
        Notification.type == "inventory_update",
    ).scalar() or 0
    
    return {
        "employee_id": employee.user_id,
        "username": employee.user_username,
        "role": employee.role,
        "created_at": employee.created_at,
        "items_scanned": scans_count,
        "orders_completed": completed_orders,
        "inventory_updated": int(total_inventory_updated),
        "products_added_count": int(products_added_count),
        "status": "active",
        "scanned_products": [
            {
                "product_id": row.product_id,
                "item_name": row.item_name,
                "size": row.size,
                "total_scanned": int(row.total_scanned or 0),
                "last_scanned_at": row.last_scanned_at,
            }
            for row in scanned_products
        ],
        "scanned_orders": [
            {
                "order_id": row.order_id,
                "client_name": row.client_name,
                "status": row.status.value if hasattr(row.status, "value") else str(row.status),
                "scan_events": int(row.scan_events or 0),
                "total_scanned": int(row.total_scanned or 0),
                "last_scanned_at": row.last_scanned_at,
            }
            for row in scanned_orders
        ],
        "inventory_updates": [
            {
                "notification_id": row.notification_id,
                "product_id": row.reference_id,
                "item_name": row.item_name,
                "size": row.size,
                "title": row.title,
                "message": row.message,
                "created_at": row.created_at,
            }
            for row in inventory_updates
        ],
        "recent_scans": [
            {
                "scan_id": log.scan_id,
                "order_id": log.order_id,
                "product_id": log.product_id,
                "scanned_quantity": log.scanned_quantity,
                "scanned_at": log.scanned_at
            }
            for log in recent_scans
        ]
    }
