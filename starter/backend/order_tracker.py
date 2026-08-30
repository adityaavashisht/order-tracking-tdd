# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.
VALID_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """

    def __init__(self, storage):
        """
        Stores the given storage backend.

        Raises TypeError if the object does not implement the storage
        interface (save_order, get_order, get_all_orders).
        """
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int,
                  customer_id: str, status: str = "pending"):
        if not order_id:
            raise ValueError("Order ID is required.")
        if not item_name:
            raise ValueError("Item name is required.")
        if not customer_id:
            raise ValueError("Customer ID is required.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order)
        return order

    def get_order_by_id(self, order_id: str):
        if not order_id:
            raise ValueError("Order ID is required")
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        if not order_id:
            raise ValueError("Order ID is required")
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")

        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(f"Order with ID '{order_id}' not found.")

        order["status"] = new_status
        self.storage.save_order(order_id, order)
        return order

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        return [
            order for order in self.storage.get_all_orders().values()
            if order["status"] == status
        ]
