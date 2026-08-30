import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---


@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock


@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)


# --- Unit Tests for OrderTracker ---


def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


def test_add_order_stores_details_with_default_status(order_tracker, mock_storage):
    """Tests that order details are stored correctly and status defaults to 'pending'."""
    order_tracker.add_order("ORD002", "Mouse", 2, "CUST002")

    mock_storage.save_order.assert_called_once_with("ORD002", {
        "order_id": "ORD002",
        "item_name": "Mouse",
        "quantity": 2,
        "customer_id": "CUST002",
        "status": "pending"
    })


def test_add_order_with_explicit_status(order_tracker, mock_storage):
    """Tests that an explicitly passed status overrides the 'pending' default."""
    order_tracker.add_order("ORD003", "Keyboard", 1, "CUST003", status="shipped")

    mock_storage.save_order.assert_called_once_with("ORD003", {
        "order_id": "ORD003",
        "item_name": "Keyboard",
        "quantity": 1,
        "customer_id": "CUST003",
        "status": "shipped"
    })


def test_add_order_raises_error_for_invalid_quantity(order_tracker, mock_storage):
    """Tests that a non-positive quantity raises a ValueError."""
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD004", "Monitor", 0, "CUST004")


def test_add_order_raises_error_for_missing_required_fields(order_tracker, mock_storage):
    """Tests that an empty required field raises a ValueError."""
    with pytest.raises(ValueError, match="Item name is required"):
        order_tracker.add_order("ORD005", "", 1, "CUST005")

    mock_storage.get_order.assert_not_called()


def test_add_order_raises_error_for_empty_order_id(order_tracker, mock_storage):
    """Tests that an empty order ID raises a ValueError before storage is read."""
    with pytest.raises(ValueError, match="Order ID is required"):
        order_tracker.add_order("", "Mouse", 1, "CUST005")

    mock_storage.get_order.assert_not_called()


def test_add_order_raises_error_for_empty_customer_id(order_tracker, mock_storage):
    """Tests that an empty customer ID raises a ValueError before storage is read."""
    with pytest.raises(ValueError, match="Customer ID is required"):
        order_tracker.add_order("ORD005", "Mouse", 1, "")

    mock_storage.get_order.assert_not_called()


def test_add_order_raises_error_for_invalid_status(order_tracker, mock_storage):
    """Tests that an unrecognized initial status raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.add_order("ORD006", "Webcam", 1, "CUST006", status="banana")


def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    """Tests fetching an order that exists in storage."""
    expected = {
        "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
        "customer_id": "CUST001", "status": "pending"
    }
    mock_storage.get_order.return_value = expected

    result = order_tracker.get_order_by_id("ORD001")

    assert result == expected
    mock_storage.get_order.assert_called_once_with("ORD001")


def test_get_order_by_id_returns_none_if_not_found(order_tracker, mock_storage):
    """Tests that a missing order returns None rather than raising."""
    assert order_tracker.get_order_by_id("NONEXISTENT") is None


def test_get_order_by_id_raises_error_for_empty_id(order_tracker, mock_storage):
    """Tests that an empty order ID raises a ValueError."""
    with pytest.raises(ValueError, match="Order ID is required"):
        order_tracker.get_order_by_id("")

    mock_storage.get_order.assert_not_called()


def test_update_order_status_successfully(order_tracker, mock_storage):
    """Tests changing an order's status from 'pending' to 'shipped'."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
        "customer_id": "CUST001", "status": "pending"
    }

    result = order_tracker.update_order_status("ORD001", "shipped")

    mock_storage.save_order.assert_called_once_with("ORD001", {
        "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
        "customer_id": "CUST001", "status": "shipped"
    })
    assert result["status"] == "shipped"


def test_update_order_status_raises_error_for_invalid_status(order_tracker, mock_storage):
    """Tests that an invalid status raises before storage is ever read."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.update_order_status("ORD001", "banana")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_raises_error_if_order_not_found(order_tracker, mock_storage):
    """Tests that updating a non-existent order raises a ValueError."""
    with pytest.raises(ValueError, match="not found"):
        order_tracker.update_order_status("NONEXISTENT", "shipped")

    mock_storage.save_order.assert_not_called()


def test_update_order_status_raises_error_for_empty_id(order_tracker, mock_storage):
    """Tests that an empty order ID raises a ValueError."""
    with pytest.raises(ValueError, match="Order ID is required"):
        order_tracker.update_order_status("", "shipped")

    mock_storage.get_order.assert_not_called()


def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker, mock_storage):
    """Tests that empty storage yields an empty list."""
    assert order_tracker.list_all_orders() == []


def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    """Tests that all stored orders are returned as a list of dicts."""
    order_a = {"order_id": "A1", "item_name": "Item A", "quantity": 1,
               "customer_id": "C1", "status": "pending"}
    order_b = {"order_id": "B2", "item_name": "Item B", "quantity": 2,
               "customer_id": "C2", "status": "shipped"}
    mock_storage.get_all_orders.return_value = {"A1": order_a, "B2": order_b}

    result = order_tracker.list_all_orders()

    assert len(result) == 2
    assert order_a in result
    assert order_b in result


def test_list_orders_by_status_returns_matching_orders(order_tracker, mock_storage):
    """Tests that only orders with the given status are returned."""
    pending = {"order_id": "A1", "item_name": "Item A", "quantity": 1,
               "customer_id": "C1", "status": "pending"}
    shipped = {"order_id": "B2", "item_name": "Item B", "quantity": 2,
               "customer_id": "C2", "status": "shipped"}
    mock_storage.get_all_orders.return_value = {"A1": pending, "B2": shipped}

    result = order_tracker.list_orders_by_status("shipped")

    assert result == [shipped]


def test_list_orders_by_status_returns_empty_list_when_no_matches(order_tracker, mock_storage):
    """Tests that a status with no matching orders yields an empty list."""
    pending = {"order_id": "A1", "item_name": "Item A", "quantity": 1,
               "customer_id": "C1", "status": "pending"}
    mock_storage.get_all_orders.return_value = {"A1": pending}

    assert order_tracker.list_orders_by_status("cancelled") == []


def test_list_orders_by_status_returns_empty_list_for_empty_storage(order_tracker, mock_storage):
    """Tests that empty storage yields an empty list."""
    assert order_tracker.list_orders_by_status("pending") == []


def test_list_orders_by_status_raises_error_for_invalid_status(order_tracker, mock_storage):
    """Tests that an invalid status raises before storage is read."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.list_orders_by_status("banana")

    mock_storage.get_all_orders.assert_not_called()
