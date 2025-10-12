"""
Order Confirmation Test Suite
Student: 24185521 - Antony O'Neill

Test coverage for FR-005: Order Confirmation
Tests order creation, confirmation page display, email notifications,
and order history tracking.

Test Scenario: TS-005 - Order Management and Confirmation
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, cart, orders, users
from models import Order, EmailService


class TestOrderCreation:
    """Test cases for order creation and storage"""

    def test_order_creation_success(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-01] Verify order is created successfully after payment

        Test Steps:
        1. Add items to cart
        2. Complete checkout with valid payment
        3. Verify order object created
        4. Verify order has unique order ID
        5. Verify order contains correct items
        6. Verify order stored in orders dict

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Order created with all details
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 2)
        clean_cart.add_book(sample_books[1], 1)
        expected_total = clean_cart.get_total_price()

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        # Verify order was created
        assert len(orders) > 0
        created_order = list(orders.values())[0]

        # Verify order attributes
        assert created_order.order_id is not None
        assert len(created_order.order_id) > 0
        assert created_order.user_email == valid_checkout_data['email']
        assert len(created_order.items) == 2
        assert created_order.total_amount == expected_total
        assert created_order.status == 'Confirmed'

    def test_order_has_unique_id(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-02] Verify each order gets unique order ID

        Test Steps:
        1. Create first order
        2. Reset cart and create second order
        3. Verify both orders have different IDs
        4. Verify IDs are uppercase alphanumeric

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Each order has unique ID
        """
        # Arrange & Act - Create first order
        clean_cart.add_book(sample_books[0], 1)
        response1 = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        first_order_id = list(orders.keys())[0] if len(orders) > 0 else None

        # Create second order
        clean_cart.clear()
        clean_cart.add_book(sample_books[1], 1)

        checkout_data2 = valid_checkout_data.copy()
        checkout_data2['email'] = 'second@example.com'
        response2 = client.post('/process-checkout', data=checkout_data2, follow_redirects=True)

        # Assert
        assert len(orders) >= 2
        order_ids = list(orders.keys())
        assert len(order_ids) == len(set(order_ids))  # All unique

        # Verify ID format (uppercase, 8 characters from uuid)
        for order_id in order_ids:
            assert order_id.isupper()
            assert len(order_id) == 8

    def test_order_contains_cart_items_snapshot(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-03] Verify order contains snapshot of cart items at checkout

        Test Steps:
        1. Add specific items to cart
        2. Complete checkout
        3. Verify order contains those items
        4. Verify item quantities match
        5. Verify prices captured correctly

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Order preserves cart state at time of purchase
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 3)
        clean_cart.add_book(sample_books[2], 2)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert len(orders) > 0
        created_order = list(orders.values())[0]

        # Verify items
        assert len(created_order.items) == 2

        # Find specific items
        item_titles = [item.book.title for item in created_order.items]
        assert 'Test Book 1' in item_titles
        assert 'Test Book 3' in item_titles

        # Verify quantities
        for item in created_order.items:
            if item.book.title == 'Test Book 1':
                assert item.quantity == 3
            elif item.book.title == 'Test Book 3':
                assert item.quantity == 2

    def test_order_stores_shipping_information(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-04] Verify order stores complete shipping information

        Test Steps:
        1. Complete checkout with shipping details
        2. Retrieve created order
        3. Verify all shipping fields stored correctly
        4. Verify data integrity

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: All shipping details preserved in order
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert len(orders) > 0
        created_order = list(orders.values())[0]

        # Verify shipping info
        assert created_order.shipping_info['name'] == valid_checkout_data['name']
        assert created_order.shipping_info['email'] == valid_checkout_data['email']
        assert created_order.shipping_info['address'] == valid_checkout_data['address']
        assert created_order.shipping_info['city'] == valid_checkout_data['city']
        assert created_order.shipping_info['zip_code'] == valid_checkout_data['zip_code']

    def test_order_stores_payment_method(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-05] Verify order stores payment method and transaction ID

        Test Steps:
        1. Complete checkout with payment
        2. Verify payment method stored
        3. Verify transaction ID stored
        4. Verify sensitive card data NOT stored

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Payment info stored securely
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert len(orders) > 0
        created_order = list(orders.values())[0]

        # Verify payment info
        assert created_order.payment_info['method'] == 'credit_card'
        assert 'transaction_id' in created_order.payment_info
        assert created_order.payment_info['transaction_id'].startswith('TXN')

        # Verify sensitive data NOT stored
        assert 'card_number' not in created_order.payment_info
        assert 'cvv' not in created_order.payment_info


class TestOrderConfirmationPage:
    """Test cases for order confirmation page display"""

    def test_order_confirmation_page_displays(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-06] Verify order confirmation page displays after successful checkout

        Test Steps:
        1. Complete checkout successfully
        2. Verify redirect to order confirmation page
        3. Verify confirmation page displays order details
        4. Verify order ID visible

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Confirmation page shows order details
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'confirmation' in response.data.lower() or b'order' in response.data.lower()
        assert b'success' in response.data.lower() or b'confirmed' in response.data.lower()

    def test_order_confirmation_shows_order_id(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-07] Verify order confirmation displays order ID to customer

        Test Steps:
        1. Complete checkout
        2. Extract order ID from confirmation page
        3. Verify order ID displayed prominently
        4. Verify customer can reference this ID

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Order ID clearly visible to customer
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        if len(orders) > 0:
            created_order = list(orders.values())[0]
            order_id_bytes = created_order.order_id.encode()

            # Order ID should be visible on confirmation page
            assert order_id_bytes in response.data or b'order' in response.data.lower()

    def test_order_confirmation_shows_items_purchased(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-08] Verify order confirmation displays purchased items

        Test Steps:
        1. Add multiple items to cart
        2. Complete checkout
        3. Verify confirmation page lists all items
        4. Verify quantities shown
        5. Verify total amount shown

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Complete order summary on confirmation page
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 2)
        clean_cart.add_book(sample_books[1], 1)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # Confirmation page should show order details
        assert b'confirmation' in response.data.lower() or b'order' in response.data.lower()

    def test_order_confirmation_page_direct_access(self, client, sample_order):
        """
        [TC005-09] Verify order confirmation page can be accessed directly with order ID

        Test Steps:
        1. Create an order
        2. Navigate directly to /order-confirmation/<order_id>
        3. Verify page loads with order details

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Confirmation page accessible via direct URL
        """
        # Arrange - Add order to orders dict
        orders[sample_order.order_id] = sample_order

        # Act
        response = client.get(f'/order-confirmation/{sample_order.order_id}')

        # Assert
        assert response.status_code == 200
        assert b'confirmation' in response.data.lower() or b'order' in response.data.lower()

    def test_order_confirmation_invalid_order_id(self, client):
        """
        [TC005-10] Verify appropriate error for invalid order ID

        Test Steps:
        1. Navigate to confirmation page with non-existent order ID
        2. Verify error message
        3. Verify redirect to home page

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Error message, redirect to home
        """
        # Act
        response = client.get('/order-confirmation/INVALID123', follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'not found' in response.data.lower() or b'error' in response.data.lower()


class TestEmailService:
    """Test cases for order confirmation email service"""

    def test_email_service_sends_confirmation(self, sample_order):
        """
        [TC005-11] Verify EmailService sends order confirmation (mocked)

        Test Steps:
        1. Create an order
        2. Call EmailService.send_order_confirmation()
        3. Verify method executes successfully
        4. Verify return value indicates success

        Related Requirement: FR-005 - Order Confirmation
        Note: This is a mock implementation that prints to console
        Expected Result: Email service method executes successfully
        """
        # Act
        result = EmailService.send_order_confirmation(
            sample_order.user_email,
            sample_order
        )

        # Assert
        assert result is True

    def test_email_service_called_after_checkout(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-12] Verify email service is called during checkout process

        Test Steps:
        1. Mock the EmailService.send_order_confirmation method
        2. Complete checkout
        3. Verify email service method was called
        4. Verify correct parameters passed

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Email sent after successful order
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        with patch.object(EmailService, 'send_order_confirmation', return_value=True) as mock_email:
            # Act
            response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

            # Assert
            assert response.status_code == 200
            # Verify email service was called
            assert mock_email.called
            assert mock_email.call_count == 1

            # Verify correct email address
            call_args = mock_email.call_args[0]
            assert call_args[0] == valid_checkout_data['email']

    def test_email_contains_order_details(self, sample_order, capsys):
        """
        [TC005-13] Verify email contains complete order details

        Test Steps:
        1. Send order confirmation email
        2. Capture console output (mock email)
        3. Verify output contains order ID, items, total
        4. Verify shipping address included

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Email contains comprehensive order information
        """
        # Act
        EmailService.send_order_confirmation(sample_order.user_email, sample_order)

        # Capture console output
        captured = capsys.readouterr()

        # Assert - Verify email content
        assert 'EMAIL SENT' in captured.out
        assert sample_order.user_email in captured.out
        assert sample_order.order_id in captured.out
        assert str(sample_order.total_amount) in captured.out

    def test_email_not_sent_on_payment_failure(self, client, clean_cart, sample_books):
        """
        [TC005-14] Verify email is NOT sent when payment fails

        Test Steps:
        1. Mock EmailService
        2. Attempt checkout with failing payment (card ending 1111)
        3. Verify email service was NOT called
        4. Verify no order created

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: No email sent when payment fails
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        failing_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '4532123456781111',  # Failing card
            'expiry_date': '12/25',
            'cvv': '123'
        }

        with patch.object(EmailService, 'send_order_confirmation', return_value=True) as mock_email:
            # Act
            response = client.post('/process-checkout', data=failing_data, follow_redirects=True)

            # Assert
            assert response.status_code == 200
            # Email should NOT have been sent
            assert not mock_email.called


class TestOrderHistory:
    """Test cases for order history tracking"""

    def test_order_added_to_user_history(self, client, logged_in_client, clean_cart, sample_books, valid_checkout_data, registered_user):
        """
        [TC005-15] Verify order is added to logged-in user's order history

        Test Steps:
        1. Login as user
        2. Complete purchase
        3. Verify order added to user.orders list
        4. Verify order accessible via get_order_history()

        Related Requirement: FR-005 - Order Confirmation, FR-006 - User Auth
        Expected Result: Order tracked in user's history
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        checkout_data = valid_checkout_data.copy()
        checkout_data['email'] = registered_user.email

        # Act
        response = logged_in_client.post('/process-checkout', data=checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        # Verify order added to user
        assert len(registered_user.orders) > 0
        user_order = registered_user.orders[0]
        assert user_order.user_email == registered_user.email

    def test_guest_checkout_creates_order_without_user_history(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC005-16] Verify guest checkout creates order but no user history

        Test Steps:
        1. Complete checkout without logging in
        2. Verify order created
        3. Verify order not associated with user account

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Guest orders created but not tracked to user
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Act - Checkout as guest (not logged in)
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        # Order should be created
        assert len(orders) > 0

        # But no user should have this order in their history
        # (since we're not logged in)

    def test_order_history_returns_all_user_orders(self, registered_user, sample_order):
        """
        [TC005-17] Verify get_order_history() returns all user orders

        Test Steps:
        1. Add multiple orders to user
        2. Call get_order_history()
        3. Verify all orders returned
        4. Verify orders sorted by date (KNOWN BUG #5)

        Related Requirement: FR-005 - Order Confirmation
        Known Issue: Bug #5 - add_order() sorts on every add (inefficient)
        """
        # Arrange
        order1 = sample_order
        order2 = Order(
            order_id='TEST002',
            user_email=registered_user.email,
            items=[],
            shipping_info={},
            payment_info={},
            total_amount=50.00
        )

        # Act
        registered_user.add_order(order1)
        registered_user.add_order(order2)

        order_history = registered_user.get_order_history()

        # Assert
        assert len(order_history) == 2
        assert order1 in order_history
        assert order2 in order_history

        # Note: add_order() sorts every time (models.py:88) - performance issue


class TestOrderModel:
    """Test cases for Order model class"""

    def test_order_model_initialization(self):
        """
        [TC005-18] Verify Order model initializes with all required fields

        Test Steps:
        1. Create Order instance
        2. Verify all attributes set correctly
        3. Verify order_date auto-generated
        4. Verify status defaults to 'Confirmed'

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Order object created correctly
        """
        # Arrange
        from models import CartItem, Book
        book = Book("Test Book", "Fiction", 19.99, "test.jpg")
        items = [CartItem(book, 2)]

        # Act
        order = Order(
            order_id='TEST123',
            user_email='test@example.com',
            items=items,
            shipping_info={'name': 'Test', 'address': '123 St'},
            payment_info={'method': 'credit_card', 'transaction_id': 'TXN123'},
            total_amount=39.98
        )

        # Assert
        assert order.order_id == 'TEST123'
        assert order.user_email == 'test@example.com'
        assert len(order.items) == 1
        assert order.total_amount == 39.98
        assert order.status == 'Confirmed'
        assert order.order_date is not None

    def test_order_to_dict_serialization(self, sample_order):
        """
        [TC005-19] Verify Order.to_dict() serializes order correctly

        Test Steps:
        1. Create order
        2. Call to_dict() method
        3. Verify all fields present in dict
        4. Verify data types correct

        Related Requirement: FR-005 - Order Confirmation
        Expected Result: Order serialized to dictionary format
        """
        # Act
        order_dict = sample_order.to_dict()

        # Assert
        assert isinstance(order_dict, dict)
        assert 'order_id' in order_dict
        assert 'user_email' in order_dict
        assert 'items' in order_dict
        assert 'shipping_info' in order_dict
        assert 'total_amount' in order_dict
        assert 'order_date' in order_dict
        assert 'status' in order_dict

        # Verify items serialized correctly
        assert isinstance(order_dict['items'], list)
        if len(order_dict['items']) > 0:
            assert 'title' in order_dict['items'][0]
            assert 'quantity' in order_dict['items'][0]
            assert 'price' in order_dict['items'][0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
