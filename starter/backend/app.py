from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.errorhandler(ValueError)
def handle_validation_error(e):
    """Turns any validation error raised by OrderTracker into a 400 response."""
    return jsonify({"error": str(e)}), 400


def not_found(order_id):
    """Builds the standard 404 response for an order that does not exist."""
    return jsonify({"error": f"Order with ID '{order_id}' not found."}), 404


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id')

    # Detect duplicates here so a conflict maps to 409 rather than 400.
    if order_id and order_tracker.get_order_by_id(order_id):
        return jsonify({"error": f"Order with ID '{order_id}' already exists."}), 409

    order = order_tracker.add_order(
        order_id,
        data.get('item_name'),
        data.get('quantity'),
        data.get('customer_id'),
        data.get('status', 'pending'),
    )
    return jsonify(order), 201


@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return not_found(order_id)
    return jsonify(order), 200


@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    # Check existence first so a missing order is a 404, not a 400.
    if order_tracker.get_order_by_id(order_id) is None:
        return not_found(order_id)

    data = request.get_json(silent=True) or {}
    updated_order = order_tracker.update_order_status(order_id, data.get('new_status'))
    return jsonify(updated_order), 200


@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get('status')
    if status is None:
        return jsonify(order_tracker.list_all_orders()), 200
    return jsonify(order_tracker.list_orders_by_status(status)), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
