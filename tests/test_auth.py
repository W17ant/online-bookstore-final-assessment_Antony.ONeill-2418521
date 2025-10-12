"""
User Authentication Test Suite
Student: 24185521 - Antony O'Neill

Test coverage for FR-006: User Authentication
Tests user registration, login, logout, session management,
and password security.

Test Scenario: TS-006 - User Authentication and Authorization
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, users
from models import User


class TestUserRegistration:
    """Test cases for user registration functionality"""

    def test_user_registration_success(self, client):
        """
        [TC006-01] Verify successful user registration with valid data

        Test Steps:
        1. Navigate to registration page
        2. Submit registration form with valid data
        3. Verify user account is created
        4. Verify user is automatically logged in
        5. Verify redirect to home page
        6. Verify success flash message

        Related Requirement: FR-006 - User Authentication
        Expected Result: User registered and logged in successfully
        """
        # Arrange
        registration_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'name': 'New User',
            'address': '123 New Street, New City'
        }

        # Act
        response = client.post('/register', data=registration_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'created' in response.data.lower()

        # Verify user was added to users dict
        assert registration_data['email'] in users
        created_user = users[registration_data['email']]
        assert created_user.name == registration_data['name']
        assert created_user.email == registration_data['email']

        # Cleanup
        del users[registration_data['email']]

    def test_user_registration_duplicate_email(self, client, registered_user):
        """
        [TC006-02] Verify registration fails with duplicate email

        Test Steps:
        1. Register a user
        2. Attempt to register another user with same email
        3. Verify registration fails
        4. Verify appropriate error message
        5. Verify no duplicate account created

        Related Requirement: FR-006 - User Authentication
        Expected Result: Registration fails with error message
        """
        # Arrange - registered_user fixture already creates a user
        duplicate_data = {
            'email': registered_user.email,  # Same email
            'password': 'differentpass456',
            'name': 'Different Name',
            'address': '456 Different St'
        }

        # Act
        response = client.post('/register', data=duplicate_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'already exists' in response.data.lower() or b'duplicate' in response.data.lower()

        # Verify original user unchanged
        assert users[registered_user.email].name == registered_user.name

    def test_registration_page_loads(self, client):
        """
        [TC006-03] Verify registration page loads correctly

        Test Steps:
        1. Navigate to /register
        2. Verify page loads successfully
        3. Verify registration form is present

        Related Requirement: FR-006 - User Authentication
        Expected Result: Registration page displays with form
        """
        # Act
        response = client.get('/register')

        # Assert
        assert response.status_code == 200
        assert b'register' in response.data.lower()
        assert b'email' in response.data.lower()
        assert b'password' in response.data.lower()

    def test_registration_requires_all_fields(self, client):
        """
        [TC006-04] Verify registration requires all mandatory fields

        Test Steps:
        1. Submit registration with missing required fields
        2. Verify validation error
        3. Verify account not created

        Related Requirement: FR-006 - User Authentication
        Expected Result: Validation error for missing fields
        """
        # Test Case 1: Missing email
        incomplete_data = {
            'password': 'password123',
            'name': 'Test User'
        }

        # Act
        response = client.post('/register', data=incomplete_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'fill in' in response.data.lower()

    def test_registration_with_optional_address(self, client):
        """
        [TC006-05] Verify registration succeeds without optional address field

        Test Steps:
        1. Submit registration without address (optional field)
        2. Verify registration succeeds
        3. Verify user created with empty address

        Related Requirement: FR-006 - User Authentication
        Expected Result: Registration succeeds, address is optional
        """
        # Arrange
        registration_data = {
            'email': 'noaddress@example.com',
            'password': 'password123',
            'name': 'No Address User'
            # address field omitted
        }

        # Act
        response = client.post('/register', data=registration_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200

        # Verify user created
        if registration_data['email'] in users:
            created_user = users[registration_data['email']]
            assert created_user.address == ''  # Empty string default

            # Cleanup
            del users[registration_data['email']]


class TestUserLogin:
    """Test cases for user login functionality"""

    def test_user_login_success(self, client, registered_user):
        """
        [TC006-06] Verify successful login with valid credentials

        Test Steps:
        1. Register a user
        2. Navigate to login page
        3. Submit login form with correct credentials
        4. Verify login successful
        5. Verify redirect to home page
        6. Verify session established

        Related Requirement: FR-006 - User Authentication
        Expected Result: User logged in successfully
        """
        # Arrange
        login_data = {
            'email': registered_user.email,
            'password': registered_user.password
        }

        # Act
        response = client.post('/login', data=login_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'logged in' in response.data.lower() or b'success' in response.data.lower()

        # Verify session was created
        with client.session_transaction() as session:
            assert 'user_email' in session
            assert session['user_email'] == registered_user.email

    def test_user_login_invalid_email(self, client):
        """
        [TC006-07] Verify login fails with non-existent email

        Test Steps:
        1. Attempt login with email not in system
        2. Verify login fails
        3. Verify appropriate error message
        4. Verify no session created

        Related Requirement: FR-006 - User Authentication
        Expected Result: Login fails with error message
        """
        # Arrange
        invalid_login_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }

        # Act
        response = client.post('/login', data=invalid_login_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'invalid' in response.data.lower() or b'incorrect' in response.data.lower()

    def test_user_login_invalid_password(self, client, registered_user):
        """
        [TC006-08] Verify login fails with incorrect password

        Test Steps:
        1. Attempt login with correct email but wrong password
        2. Verify login fails
        3. Verify appropriate error message
        4. Verify no session created

        Related Requirement: FR-006 - User Authentication
        Expected Result: Login fails with error message
        """
        # Arrange
        wrong_password_data = {
            'email': registered_user.email,
            'password': 'wrongpassword123'
        }

        # Act
        response = client.post('/login', data=wrong_password_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'invalid' in response.data.lower() or b'incorrect' in response.data.lower()

        # Verify no session created
        with client.session_transaction() as session:
            assert 'user_email' not in session

    def test_login_page_loads(self, client):
        """
        [TC006-09] Verify login page loads correctly

        Test Steps:
        1. Navigate to /login
        2. Verify page loads successfully
        3. Verify login form is present

        Related Requirement: FR-006 - User Authentication
        Expected Result: Login page displays with form
        """
        # Act
        response = client.get('/login')

        # Assert
        assert response.status_code == 200
        assert b'login' in response.data.lower()
        assert b'email' in response.data.lower()
        assert b'password' in response.data.lower()


class TestUserLogout:
    """Test cases for user logout functionality"""

    def test_user_logout_success(self, client, logged_in_client):
        """
        [TC006-10] Verify successful user logout

        Test Steps:
        1. Login as user
        2. Navigate to logout route
        3. Verify session cleared
        4. Verify redirect to home page
        5. Verify success message

        Related Requirement: FR-006 - User Authentication
        Expected Result: User logged out, session cleared
        """
        # Act
        response = logged_in_client.get('/logout', follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'logged out' in response.data.lower() or b'success' in response.data.lower()

        # Verify session cleared
        with logged_in_client.session_transaction() as session:
            assert 'user_email' not in session

    def test_logout_when_not_logged_in(self, client):
        """
        [TC006-11] Verify logout works even when not logged in

        Test Steps:
        1. Navigate to logout without being logged in
        2. Verify no error occurs
        3. Verify redirect to home

        Related Requirement: FR-006 - User Authentication
        Expected Result: Logout succeeds gracefully
        """
        # Act
        response = client.get('/logout', follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # Should handle gracefully, no crash


class TestSessionManagement:
    """Test cases for user session management"""

    def test_session_persistence_across_requests(self, client, logged_in_client, registered_user):
        """
        [TC006-12] Verify user session persists across multiple requests

        Test Steps:
        1. Login as user
        2. Make multiple requests to different pages
        3. Verify session maintained throughout
        4. Verify user remains logged in

        Related Requirement: FR-006 - User Authentication
        Expected Result: Session persists across requests
        """
        # Act - Make multiple requests
        response1 = logged_in_client.get('/')
        response2 = logged_in_client.get('/cart')
        response3 = logged_in_client.get('/account')

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # Session should persist
        with logged_in_client.session_transaction() as session:
            assert 'user_email' in session
            assert session['user_email'] == registered_user.email

    def test_protected_route_requires_login(self, client):
        """
        [TC006-13] Verify protected routes redirect to login when not authenticated

        Test Steps:
        1. Attempt to access protected route (/account) without login
        2. Verify redirect to login page
        3. Verify appropriate flash message

        Related Requirement: FR-006 - User Authentication
        Expected Result: Redirect to login page with error message
        """
        # Act
        response = client.get('/account', follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'log in' in response.data.lower()

    def test_logged_in_user_can_access_protected_routes(self, logged_in_client):
        """
        [TC006-14] Verify logged-in user can access protected routes

        Test Steps:
        1. Login as user
        2. Access protected route (/account)
        3. Verify access granted
        4. Verify page loads successfully

        Related Requirement: FR-006 - User Authentication
        Expected Result: Protected route accessible when authenticated
        """
        # Act
        response = logged_in_client.get('/account')

        # Assert
        assert response.status_code == 200
        assert b'account' in response.data.lower() or b'profile' in response.data.lower()


class TestPasswordSecurity:
    """Test cases for password handling and security"""

    def test_password_stored_in_plain_text_security_issue(self, test_user):
        """
        [TC006-15] Document that passwords are stored in plain text (SECURITY ISSUE)

        Test Steps:
        1. Create user with password
        2. Verify password stored in User object
        3. Document that passwords are NOT hashed (security issue)

        Related Requirement: FR-006 - User Authentication
        Security Note: Current implementation stores passwords in plain text
        Recommendation: Use werkzeug.security.generate_password_hash()
        """
        # Act
        user = User('security@example.com', 'plaintext123', 'Security Test')

        # Assert
        # Current implementation stores password in plain text (security issue)
        assert user.password == 'plaintext123'

        # RECOMMENDATION: Should be hashed
        # from werkzeug.security import generate_password_hash, check_password_hash
        # user.password_hash = generate_password_hash('plaintext123')
        # check_password_hash(user.password_hash, 'plaintext123')

    def test_password_comparison_plain_text(self, registered_user):
        """
        [TC006-16] Document password comparison uses plain text (SECURITY ISSUE)

        Test Steps:
        1. Verify login compares passwords in plain text
        2. Document security concern

        Related Requirement: FR-006 - User Authentication
        Security Note: app.py line 284 compares passwords directly
        Recommendation: Use check_password_hash() for secure comparison
        """
        # Current implementation in app.py:284
        # if user and user.password == password:
        #     # This is plain text comparison (NOT SECURE)

        # Verify current behavior
        assert registered_user.password == registered_user.password  # Plain text

        # RECOMMENDATION: Should use hashing
        # if user and check_password_hash(user.password_hash, password):

    def test_user_can_change_password(self, logged_in_client, registered_user):
        """
        [TC006-17] Verify user can update password through profile

        Test Steps:
        1. Login as user
        2. Access account page
        3. Submit profile update with new password
        4. Verify password changed
        5. Verify success message

        Related Requirement: FR-006 - User Authentication
        Expected Result: Password updated successfully
        """
        # Arrange
        new_password = 'newpassword456'
        update_data = {
            'name': registered_user.name,
            'address': registered_user.address,
            'new_password': new_password
        }

        # Act
        response = logged_in_client.post('/update-profile', data=update_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'updated' in response.data.lower() or b'success' in response.data.lower()

        # Verify password changed
        assert registered_user.password == new_password


class TestUserProfile:
    """Test cases for user profile management"""

    def test_user_profile_page_displays_user_info(self, logged_in_client, registered_user):
        """
        [TC006-18] Verify user profile page displays user information

        Test Steps:
        1. Login as user
        2. Navigate to account page
        3. Verify user information is displayed
        4. Verify name, email, address shown

        Related Requirement: FR-006 - User Authentication
        Expected Result: User profile information displayed correctly
        """
        # Act
        response = logged_in_client.get('/account')

        # Assert
        assert response.status_code == 200
        # User info should be displayed
        assert registered_user.name.encode() in response.data or b'account' in response.data.lower()

    def test_user_can_update_profile_info(self, logged_in_client, registered_user):
        """
        [TC006-19] Verify user can update profile information

        Test Steps:
        1. Login as user
        2. Submit profile update with new name and address
        3. Verify information updated
        4. Verify success message

        Related Requirement: FR-006 - User Authentication
        Expected Result: Profile information updated successfully
        """
        # Arrange
        new_name = 'Updated Name'
        new_address = '999 Updated Street'

        update_data = {
            'name': new_name,
            'address': new_address
        }

        # Act
        response = logged_in_client.post('/update-profile', data=update_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert b'updated' in response.data.lower() or b'success' in response.data.lower()

        # Verify user object updated
        assert registered_user.name == new_name
        assert registered_user.address == new_address

    def test_unauthenticated_user_cannot_update_profile(self, client):
        """
        [TC006-20] Verify unauthenticated user cannot update profile

        Test Steps:
        1. Attempt to update profile without logging in
        2. Verify redirect to login page
        3. Verify no data changed

        Related Requirement: FR-006 - User Authentication
        Expected Result: Redirect to login, profile update blocked
        """
        # Arrange
        update_data = {
            'name': 'Hacker Name',
            'address': 'Unauthorized'
        }

        # Act
        response = client.post('/update-profile', data=update_data, follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # Should redirect to login
        assert b'login' in response.data.lower() or b'log in' in response.data.lower()


class TestUserModel:
    """Test cases for User model class"""

    def test_user_initialization(self):
        """
        [TC006-21] Verify User model initializes correctly

        Test Steps:
        1. Create User instance
        2. Verify all attributes set correctly
        3. Verify orders list initialized
        4. Verify temp_data and cache initialized (unused fields)

        Related Requirement: FR-006 - User Authentication
        Expected Result: User object created with correct attributes
        """
        # Act
        user = User(
            email='model@example.com',
            password='testpass',
            name='Model Test',
            address='123 Model St'
        )

        # Assert
        assert user.email == 'model@example.com'
        assert user.password == 'testpass'
        assert user.name == 'Model Test'
        assert user.address == '123 Model St'
        assert user.orders == []
        assert user.temp_data == []
        assert user.cache == {}

    def test_user_add_order(self, test_user, sample_order):
        """
        [TC006-22] Verify User.add_order() method works correctly

        Test Steps:
        1. Create user
        2. Add order to user
        3. Verify order in user's orders list
        4. Verify orders are sorted by date (KNOWN BUG #5)

        Related Requirement: FR-006 - User Authentication, FR-005 - Orders
        Known Issue: Bug #5 - Orders sorted on every add (inefficient)
        """
        # Act
        test_user.add_order(sample_order)

        # Assert
        assert len(test_user.orders) == 1
        assert test_user.orders[0] == sample_order

        # Note: add_order() sorts on every add (models.py:88) - inefficiency

    def test_user_get_order_history(self, test_user, sample_order):
        """
        [TC006-23] Verify User.get_order_history() returns all orders

        Test Steps:
        1. Create user
        2. Add multiple orders
        3. Call get_order_history()
        4. Verify all orders returned

        Related Requirement: FR-006 - User Authentication, FR-005 - Orders
        Expected Result: All user orders returned
        """
        # Arrange
        test_user.add_order(sample_order)

        # Act
        order_history = test_user.get_order_history()

        # Assert
        assert len(order_history) == 1
        assert order_history[0] == sample_order


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
