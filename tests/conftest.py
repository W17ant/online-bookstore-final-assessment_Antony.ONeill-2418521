"""
Shared pytest fixtures for all test modules
Student: 24185521 - Antony O'Neill

This module provides reusable fixtures for testing the Online Bookstore application.
Following pytest best practices for fixture organization and scope management.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, users, orders, cart, BOOKS
from models import Book, Cart, User, Order


@pytest.fixture
def client():
    """
    Create a test client for the Flask application.

    Yields:
        FlaskClient: A test client that can make requests to the app

    Related to: All test scenarios requiring HTTP endpoint testing
    """
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


@pytest.fixture
def clean_cart():
    """
    Provides a clean cart instance and ensures cleanup after test.

    Yields:
        Cart: An empty cart instance

    Related to: TC002 (Shopping Cart Functionality)
    """
    cart.clear()
    yield cart
    cart.clear()


@pytest.fixture
def sample_books():
    """
    Provides sample book instances for testing.

    Returns:
        list[Book]: List of test book objects

    Related to: TC001 (Book Catalog), TC002 (Shopping Cart)
    """
    return [
        Book("Test Book 1", "Fiction", 19.99, "test1.jpg"),
        Book("Test Book 2", "Science", 29.99, "test2.jpg"),
        Book("Test Book 3", "History", 39.99, "test3.jpg")
    ]


@pytest.fixture
def populated_cart(sample_books):
    """
    Provides a cart with sample items already added.

    Args:
        sample_books: Fixture providing test books

    Returns:
        Cart: A cart with pre-populated items

    Related to: TC002 (Shopping Cart), TC003 (Checkout)
    """
    test_cart = Cart()
    test_cart.add_book(sample_books[0], 2)
    test_cart.add_book(sample_books[1], 1)
    return test_cart


@pytest.fixture
def test_user():
    """
    Creates a test user account for authentication testing.

    Returns:
        User: A test user object

    Related to: TC006 (User Authentication)
    """
    return User(
        email="test@example.com",
        password="testpass123",
        name="Test User",
        address="123 Test Street, Test City, TC 12345"
    )


@pytest.fixture
def registered_user(test_user):
    """
    Registers a user in the global users dict and cleans up after test.

    Args:
        test_user: Fixture providing test user

    Yields:
        User: A registered user object

    Related to: TC006 (User Authentication)
    """
    users[test_user.email] = test_user
    yield test_user
    # Cleanup
    if test_user.email in users:
        del users[test_user.email]


@pytest.fixture
def logged_in_client(client, registered_user):
    """
    Provides an authenticated test client with active session.

    Args:
        client: Flask test client fixture
        registered_user: Registered user fixture

    Yields:
        FlaskClient: Authenticated test client

    Related to: TC006 (User Authentication), TC005 (Order Management)
    """
    with client.session_transaction() as session:
        session['user_email'] = registered_user.email
    yield client


@pytest.fixture
def sample_order(sample_books):
    """
    Creates a sample order for testing order functionality.

    Args:
        sample_books: Fixture providing test books

    Returns:
        Order: A sample order object

    Related to: TC005 (Order Confirmation)
    """
    from models import CartItem
    items = [
        CartItem(sample_books[0], 2),
        CartItem(sample_books[1], 1)
    ]

    shipping_info = {
        'name': 'Test User',
        'email': 'test@example.com',
        'address': '123 Test St',
        'city': 'Test City',
        'zip_code': '12345'
    }

    payment_info = {
        'method': 'credit_card',
        'transaction_id': 'TXN123456'
    }

    return Order(
        order_id='TEST001',
        user_email='test@example.com',
        items=items,
        shipping_info=shipping_info,
        payment_info=payment_info,
        total_amount=69.97
    )


@pytest.fixture
def valid_checkout_data():
    """
    Provides valid checkout form data for testing.

    Returns:
        dict: Complete valid checkout form data

    Related to: TC003 (Checkout Process), TC004 (Payment Processing)
    """
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'address': '456 Main Street',
        'city': 'Springfield',
        'zip_code': '54321',
        'payment_method': 'credit_card',
        'card_number': '4532123456789012',
        'expiry_date': '12/25',
        'cvv': '123'
    }


@pytest.fixture
def valid_payment_info():
    """
    Provides valid payment information for payment gateway testing.

    Returns:
        dict: Valid payment information

    Related to: TC004 (Payment Processing)
    """
    return {
        'payment_method': 'credit_card',
        'card_number': '4532123456789012',
        'expiry_date': '12/25',
        'cvv': '123'
    }


@pytest.fixture
def failing_payment_info():
    """
    Provides payment information that triggers payment failure (card ending in 1111).

    Returns:
        dict: Payment info that will fail

    Related to: TC004 (Payment Processing)
    """
    return {
        'payment_method': 'credit_card',
        'card_number': '4532123456781111',
        'expiry_date': '12/25',
        'cvv': '123'
    }


@pytest.fixture(autouse=True)
def cleanup_orders():
    """
    Automatically cleans up orders dict after each test.
    This prevents test pollution across test modules.

    Yields:
        None

    Note: autouse=True means this runs automatically for all tests
    """
    yield
    orders.clear()


@pytest.fixture
def app_context():
    """
    Provides Flask application context for tests that need it.

    Yields:
        Flask app context
    """
    with app.app_context():
        yield
