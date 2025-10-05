"""Text2SQL engine (prototype)
- mock_gemini_to_sql: returns canned SQL for demo/testing
"""
def mock_gemini_to_sql(question: str) -> str:
    q = question.strip().lower()
    if 'total revenue' in q or 'revenue' in q:
        return 'SELECT c.category_name, SUM(od.unit_price * od.quantity) AS total_revenue FROM order_details od JOIN products p ON od.product_id = p.product_id JOIN categories c ON p.category_id = c.category_id GROUP BY c.category_name;'
    if 'customers' in q and 'all' in q:
        return 'SELECT customer_id, company_name, contact_name FROM customers LIMIT 100;'
    if 'orders' in q and 'count' in q:
        return 'SELECT COUNT(*) AS orders_count FROM orders;'
    # fallback
    return 'SELECT 1;'
