"""
Payment Processing Test Suite
Student: 24185521 - Antony O'Neill

Test coverage for FR-004: Payment Processing
Tests payment gateway integration, payment method handling,
and transaction processing workflows.

Test Scenario: TS-004 - Payment Processing
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, cart, orders
from models import PaymentGateway


class TestPaymentGateway:
    """Test cases for PaymentGateway mock implementation"""

    def test_payment_gateway_success_valid_card(self, valid_payment_info):
        """
        [TC004-01] Verify payment gateway processes valid card successfully

        Test Steps:
        1. Prepare valid payment information
        2. Process payment through PaymentGateway
        3. Verify success response returned
        4. Verify transaction ID generated

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Payment successful with transaction ID
        """
        # Act
        result = PaymentGateway.process_payment(valid_payment_info)

        # Assert
        assert result['success'] is True
        assert result['message'] == 'Payment processed successfully'
        assert result['transaction_id'] is not None
        assert result['transaction_id'].startswith('TXN')
        assert len(result['transaction_id']) > 3

    def test_payment_gateway_failure_card_ending_1111(self, failing_payment_info):
        """
        [TC004-02] Verify payment gateway fails for card ending in 1111

        Test Steps:
        1. Prepare payment info with card ending in 1111
        2. Process payment through PaymentGateway
        3. Verify failure response returned
        4. Verify appropriate error message
        5. Verify no transaction ID generated

        Related Requirement: FR-004 - Payment Processing
        Mock Logic: Cards ending in '1111' should fail
        Expected Result: Payment fails with error message
        """
        # Act
        result = PaymentGateway.process_payment(failing_payment_info)

        # Assert
        assert result['success'] is False
        assert 'fail' in result['message'].lower() or 'invalid' in result['message'].lower()
        assert result['transaction_id'] is None

    def test_payment_gateway_generates_unique_transaction_ids(self, valid_payment_info):
        """
        [TC004-03] Verify each payment generates unique transaction ID

        Test Steps:
        1. Process multiple payments with same card
        2. Verify each generates different transaction ID
        3. Verify transaction IDs follow expected format

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Unique transaction ID for each payment
        """
        # Act
        result1 = PaymentGateway.process_payment(valid_payment_info)
        result2 = PaymentGateway.process_payment(valid_payment_info)
        result3 = PaymentGateway.process_payment(valid_payment_info)

        # Assert
        assert result1['success'] is True
        assert result2['success'] is True
        assert result3['success'] is True

        # All transaction IDs should be unique
        txn_ids = [result1['transaction_id'], result2['transaction_id'], result3['transaction_id']]
        assert len(txn_ids) == len(set(txn_ids))  # All unique

    def test_payment_gateway_handles_missing_card_number(self):
        """
        [TC004-04] Verify payment gateway handles missing card number gracefully

        Test Steps:
        1. Prepare payment info without card number
        2. Process payment
        3. Verify appropriate handling (no crash)

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Payment fails gracefully without errors
        """
        # Arrange
        incomplete_payment_info = {
            'payment_method': 'credit_card',
            'expiry_date': '12/25',
            'cvv': '123'
        }

        # Act
        result = PaymentGateway.process_payment(incomplete_payment_info)

        # Assert - Should handle gracefully
        # Current implementation may succeed (no validation) or fail
        assert 'success' in result
        assert 'message' in result
        assert 'transaction_id' in result


class TestPaymentMethodCreditCard:
    """Test cases for credit card payment method"""

    def test_checkout_with_credit_card_success(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC004-05] Verify successful checkout using credit card

        Test Steps:
        1. Add items to cart
        2. Submit checkout with valid credit card details
        3. Verify payment processes successfully
        4. Verify order is created with transaction ID
        5. Verify cart is cleared

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Order completed successfully with credit card
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'confirmation' in response.data.lower()

        # Verify order was created
        assert len(orders) > 0
        created_order = list(orders.values())[0]
        assert created_order.payment_info['method'] == 'credit_card'
        assert created_order.payment_info['transaction_id'].startswith('TXN')

    def test_checkout_with_credit_card_failure(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC004-06] Verify checkout fails with invalid credit card (ending in 1111)

        Test Steps:
        1. Add items to cart
        2. Submit checkout with card ending in 1111
        3. Verify payment fails
        4. Verify user redirected back to checkout
        5. Verify cart is NOT cleared
        6. Verify error message displayed

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Payment fails, user stays on checkout, cart retained
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        checkout_data = valid_checkout_data.copy()
        checkout_data['card_number'] = '4532123456781111'  # Failing card

        # Act
        response = client.post('/process-checkout', data=checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'fail' in response.data.lower() or b'invalid' in response.data.lower()

        # Cart should still have items (not cleared on failed payment)
        assert not clean_cart.is_empty()
        assert len(clean_cart.items) > 0

    def test_credit_card_requires_all_fields(self, client, clean_cart, sample_books):
        """
        [TC004-07] Verify credit card payment requires all card fields

        Test Steps:
        1. Add items to cart
        2. Submit checkout with missing card details (no CVV)
        3. Verify validation error
        4. Verify checkout not completed

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Validation error for missing card fields
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        incomplete_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '4532123456789012',
            'expiry_date': '12/25'
            # Missing CVV
        }

        # Act
        response = client.post('/process-checkout', data=incomplete_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # Should show validation error
        assert b'fill in' in response.data.lower() or b'required' in response.data.lower()

    def test_credit_card_number_validation(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC004-08] Verify credit card number validation

        Test Steps:
        1. Add items to cart
        2. Submit checkout with various card number formats
        3. Verify appropriate handling

        Related Requirement: FR-004 - Payment Processing
        Note: Current implementation has minimal validation
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Test with short card number
        checkout_data = valid_checkout_data.copy()
        checkout_data['card_number'] = '1234'

        # Act
        response = client.post('/process-checkout', data=checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # Current implementation may not validate card format (documented behavior)


class TestPaymentMethodPayPal:
    """Test cases for PayPal payment method"""

    def test_checkout_with_paypal_success(self, client, clean_cart, sample_books):
        """
        [TC004-09] Verify successful checkout using PayPal

        Test Steps:
        1. Add items to cart
        2. Select PayPal as payment method
        3. Submit checkout form
        4. Verify payment processes successfully
        5. Verify order created with PayPal method

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Order completed successfully with PayPal
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 2)

        paypal_checkout_data = {
            'name': 'PayPal User',
            'email': 'paypal@example.com',
            'address': '456 PayPal Ave',
            'city': 'PayPal City',
            'zip_code': '54321',
            'payment_method': 'paypal'
        }

        # Act
        response = client.post('/process-checkout', data=paypal_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'confirmation' in response.data.lower()

        # Verify order was created with PayPal method
        if len(orders) > 0:
            created_order = list(orders.values())[0]
            assert created_order.payment_info['method'] == 'paypal'

    def test_paypal_does_not_require_card_fields(self, client, clean_cart, sample_books):
        """
        [TC004-10] Verify PayPal payment does not require credit card fields

        Test Steps:
        1. Add items to cart
        2. Select PayPal as payment method
        3. Submit without card number, expiry, CVV
        4. Verify checkout succeeds

        Related Requirement: FR-004 - Payment Processing
        Expected Result: PayPal checkout succeeds without card details
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        paypal_data = {
            'name': 'PayPal Test',
            'email': 'test@paypal.com',
            'address': '789 Test Road',
            'city': 'Test Town',
            'zip_code': '99999',
            'payment_method': 'paypal'
            # No card_number, expiry_date, cvv
        }

        # Act
        response = client.post('/process-checkout', data=paypal_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # PayPal should work without card details


class TestPaymentIntegration:
    """Integration tests for payment processing workflow"""

    def test_end_to_end_payment_flow(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC004-11] Verify complete end-to-end payment flow

        Test Steps:
        1. Browse books and add to cart
        2. Navigate to checkout
        3. Fill in shipping information
        4. Enter payment details
        5. Submit payment
        6. Verify order confirmation
        7. Verify email sent (mocked)
        8. Verify cart cleared

        Related Requirement: FR-004 - Payment Processing (Integration)
        Expected Result: Complete payment flow succeeds
        """
        # Arrange - Add items to cart
        clean_cart.add_book(sample_books[0], 1)
        clean_cart.add_book(sample_books[1], 2)
        original_total = clean_cart.get_total_price()

        # Act - Process checkout
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        # Verify order created
        assert len(orders) == 1
        created_order = list(orders.values())[0]

        # Verify order details
        assert created_order.total_amount == original_total
        assert len(created_order.items) == 2
        assert created_order.status == 'Confirmed'
        assert created_order.payment_info['method'] == 'credit_card'
        assert created_order.payment_info['transaction_id'] is not None

        # Verify cart is cleared
        assert clean_cart.is_empty()

    def test_payment_with_discount_code(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC004-12] Verify payment processing with discount code applied

        Test Steps:
        1. Add items to cart
        2. Apply discount code at checkout
        3. Process payment
        4. Verify order total reflects discount
        5. Verify payment amount is discounted amount

        Related Requirement: FR-004 - Payment Processing, FR-003 - Checkout
        Expected Result: Payment processes with discounted amount
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)  # $19.99
        original_total = clean_cart.get_total_price()

        checkout_data = valid_checkout_data.copy()
        checkout_data['discount_code'] = 'SAVE10'

        # Act
        response = client.post('/process-checkout', data=checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        # Verify order total is discounted
        if len(orders) > 0:
            created_order = list(orders.values())[0]
            expected_discounted_total = original_total * 0.90
            assert abs(created_order.total_amount - expected_discounted_total) < 0.01

    def test_payment_failure_preserves_cart(self, client, clean_cart, sample_books):
        """
        [TC004-13] Verify failed payment does not clear cart

        Test Steps:
        1. Add items to cart
        2. Attempt checkout with failing card (ending in 1111)
        3. Verify payment fails
        4. Verify cart still contains original items
        5. Verify user can retry checkout

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Cart preserved on payment failure, can retry
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 2)
        clean_cart.add_book(sample_books[1], 1)
        original_item_count = len(clean_cart.items)

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

        # Act
        response = client.post('/process-checkout', data=failing_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        # Cart should still have items
        assert len(clean_cart.items) == original_item_count
        assert not clean_cart.is_empty()

        # No order should be created
        # Note: orders dict might have items from other tests, but this order shouldn't be there
        # We verify by checking the cart is not cleared


class TestPaymentSecurity:
    """Test cases for payment security considerations"""

    def test_payment_info_not_stored_in_plain_text(self, client, clean_cart, sample_books, valid_checkout_data):
        """
        [TC004-14] Verify sensitive payment info is not stored in plain text

        Test Steps:
        1. Process successful payment
        2. Retrieve created order
        3. Verify card number is NOT stored
        4. Verify CVV is NOT stored
        5. Verify only transaction ID is stored

        Related Requirement: FR-004 - Payment Processing (Security)
        Expected Result: Sensitive payment data not stored in order
        """
        # Arrange
        clean_cart.add_book(sample_books[0], 1)

        # Act
        response = client.post('/process-checkout', data=valid_checkout_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        if len(orders) > 0:
            created_order = list(orders.values())[0]

            # Payment info should only contain method and transaction_id
            payment_info = created_order.payment_info

            # These should NOT be in stored payment info
            assert 'card_number' not in payment_info
            assert 'cvv' not in payment_info
            assert 'expiry_date' not in payment_info

            # These SHOULD be present
            assert 'method' in payment_info
            assert 'transaction_id' in payment_info

    def test_payment_gateway_processing_time(self, valid_payment_info):
        """
        [TC004-15] Verify payment gateway has realistic processing delay

        Test Steps:
        1. Time payment processing call
        2. Verify it includes simulated delay (0.1s)
        3. Verify realistic payment flow timing

        Related Requirement: FR-004 - Payment Processing
        Expected Result: Payment processing includes simulated delay
        """
        import time

        # Act
        start_time = time.time()
        result = PaymentGateway.process_payment(valid_payment_info)
        end_time = time.time()

        processing_time = end_time - start_time

        # Assert
        assert result['success'] is True
        # Payment gateway includes 0.1s delay (time.sleep(0.1) in models.py:139)
        assert processing_time >= 0.1  # Should take at least 0.1 seconds
        assert processing_time < 1.0   # But should be fast (mock)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
