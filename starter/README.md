# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## Reflection

- Wrote multiple tests and still missed a bug: `add_order` never checked for
  an empty order ID. Every test I'd written passed a valid one. Tests only cover
  what you think to ask.
- Found this late: `add_order` returned nothing while `update_order_status`
  returned the order. No test caught it because none used the return value — it
  only surfaced when POST needed the new order.
- `OrderTracker` raises `ValueError` for everything, so I couldn't tell a
  duplicate from bad input. I check for duplicates in the route before calling,
  so conflicts come back 409 and the rest 400.
- The route names rely on convention. `POST /api/orders` never says "create" —
  you just have to know. And `/orders/<id>/status` is an action, not a thing.
- Next I'd move to SQLite, add a `DELETE` route, and generate IDs server-side —
  that alone kills the empty-ID bug. The storage class is swappable, so
  `OrderTracker` wouldn't change.