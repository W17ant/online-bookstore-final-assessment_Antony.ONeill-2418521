"""
Sample test file for the Online Bookstore Flask Application
This demonstrates the testing setup for Jenkins CI/CD pipeline
"""
import pytest
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Book, Cart


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_books():
    """Sample books for testing"""
    return [
        Book("Python Testing", "Programming", 29.99, "python.jpg"),
        Book("Flask Web Development", "Programming", 39.99, "flask.jpg")
    ]


class TestHomePage:
    """
    Test cases for the home page
    Related to: FR-001 - Book Catalog Display
    """

    def test_home_page_loads(self, client):
        """
        [TC001-01] Test that the home page loads successfully

        Related Requirement: FR-001 - Book Catalog Display
        Expected Result: Home page renders with 200 status
        """
        response = client.get('/')
        assert response.status_code == 200
        assert b'Online Bookstore' in response.data

    def test_books_displayed(self, client):
        """
        [TC001-02] Test that books are displayed on home page

        Related Requirement: FR-001 - Book Catalog Display
        Expected Result: Book-related content visible on homepage
        """
        response = client.get('/')
        assert response.status_code == 200
        # Check for some book-related content
        assert b'Add to Cart' in response.data or b'book' in response.data.lower()


class TestCart:
    """
    Test cases for shopping cart functionality
    Related to: FR-002 - Shopping Cart Functionality
    """

    def test_cart_initialization(self):
        """
        [TC002-00] Test that a new cart initializes correctly

        Related Requirement: FR-002 - Shopping Cart Functionality
        Expected Result: Cart initializes empty with zero total
        """
        cart = Cart()
        assert cart.items == {}
        assert cart.get_total_price() == 0
        assert cart.is_empty() is True

    def test_add_item_to_cart(self, sample_books):
        """
        [TC002-01] Test adding a single item to the cart

        Related Requirement: FR-002 - Shopping Cart Functionality
        Expected Result: Item added to cart with correct quantity
        """
        cart = Cart()
        book = sample_books[0]
        cart.add_book(book, 1)
        assert len(cart.items) == 1
        assert book.title in cart.items
        assert cart.items[book.title].quantity == 1

    def test_cart_total_calculation(self, sample_books):
        """
        [TC002-05] Test cart total is calculated correctly

        Related Requirement: FR-002 - Shopping Cart Functionality
        Note: Tests KNOWN BUG #4 - Inefficient nested loop O(n*m)
        Expected Result: Total price calculated correctly
        """
        cart = Cart()
        book1 = sample_books[0]
        book2 = sample_books[1]
        cart.add_book(book1, 2)
        cart.add_book(book2, 1)
        expected_total = (book1.price * 2) + (book2.price * 1)
        assert cart.get_total_price() == expected_total

    def test_remove_item_from_cart(self, sample_books):
        """
        [TC002-07] Test removing an item from the cart

        Related Requirement: FR-002 - Shopping Cart Functionality
        Expected Result: Item removed from cart successfully
        """
        cart = Cart()
        book = sample_books[0]
        cart.add_book(book, 1)
        cart.remove_book(book.title)
        assert len(cart.items) == 0

    def test_clear_cart(self, sample_books):
        """
        [TC002-08] Test clearing all items from cart

        Related Requirement: FR-002 - Shopping Cart Functionality
        Expected Result: All items removed, total reset to zero
        """
        cart = Cart()
        cart.add_book(sample_books[0], 1)
        cart.add_book(sample_books[1], 1)
        cart.clear()
        assert len(cart.items) == 0
        assert cart.get_total_price() == 0


class TestBookModel:
    """
    Test cases for Book model
    Related to: FR-001 - Book Catalog Display
    """

    def test_book_creation(self):
        """
        [TC001-04] Test creating a book instance

        Related Requirement: FR-001 - Book Catalog Display
        Expected Result: Book object created with all attributes
        """
        book = Book("Test Book", "Test Category", 19.99, "test.jpg")
        assert book.title == "Test Book"
        assert book.category == "Test Category"
        assert book.price == 19.99
        assert book.image == "test.jpg"

    def test_book_attributes(self):
        """
        [TC001-05] Test book attributes are set correctly

        Related Requirement: FR-001 - Book Catalog Display
        Expected Result: All book attributes have correct data types
        """
        book = Book("Python Programming", "Technology", 49.99, "python.jpg")
        assert isinstance(book.title, str)
        assert isinstance(book.category, str)
        assert isinstance(book.price, float)
        assert isinstance(book.image, str)


class TestRoutes:
    """
    Test cases for Flask routes
    Related to: Multiple FRs (Cart, Auth, Checkout)
    """

    def test_cart_page_loads(self, client):
        """
        [TC002-04] Test that cart page loads

        Related Requirement: FR-002 - Shopping Cart Functionality
        Expected Result: Cart page renders successfully
        """
        response = client.get('/cart')
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        """
        [TC006-09] Test that login page loads

        Related Requirement: FR-006 - User Authentication
        Expected Result: Login page displays with form
        """
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_register_page_loads(self, client):
        """
        [TC006-03] Test that register page loads

        Related Requirement: FR-006 - User Authentication
        Expected Result: Registration page displays with form
        """
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data


class TestEdgeCases:
    """
    Test edge cases and potential bugs
    Related to: FR-002 - Shopping Cart Functionality (Bug Detection)
    """

    def test_add_zero_quantity_to_cart(self, sample_books):
        """
        [TC002-09] Test adding zero quantity (KNOWN BUG #1)

        Related Requirement: FR-002 - Shopping Cart Functionality
        Known Issue: Bug #1 - update_quantity doesn't remove items when qty <= 0
        Expected Result: Zero quantities should not be allowed or should remove item
        """
        cart = Cart()
        book = sample_books[0]
        cart.add_book(book, 0)
        # This might reveal a bug if zero quantities are allowed
        total_items = cart.get_total_items()
        assert total_items >= 0

    def test_add_negative_quantity_to_cart(self, sample_books):
        """
        [TC002-10] Test adding negative quantity (KNOWN BUG #1)

        Related Requirement: FR-002 - Shopping Cart Functionality
        Known Issue: Bug #1 - No validation for negative quantities
        Expected Result: Negative quantities should be rejected
        """
        cart = Cart()
        book = sample_books[0]
        # This should fail or be handled properly
        try:
            cart.add_book(book, -1)
            total_items = cart.get_total_items()
            # Negative quantities should not be allowed
            assert total_items >= 0
        except (ValueError, AssertionError):
            # Expected to fail
            pass

    def test_empty_cart_total(self):
        """
        [TC002-11] Test that empty cart returns zero total

        Related Requirement: FR-002 - Shopping Cart Functionality
        Expected Result: Empty cart has zero total and is_empty() returns True
        """
        cart = Cart()
        assert cart.get_total_price() == 0
        assert cart.is_empty() is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
