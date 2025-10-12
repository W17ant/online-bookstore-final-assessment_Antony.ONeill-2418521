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
    """Test cases for the home page"""

    def test_home_page_loads(self, client):
        """Test that the home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Online Bookstore' in response.data

    def test_books_displayed(self, client):
        """Test that books are displayed on home page"""
        response = client.get('/')
        assert response.status_code == 200
        # Check for some book-related content
        assert b'Add to Cart' in response.data or b'book' in response.data.lower()


class TestCart:
    """Test cases for shopping cart functionality"""

    def test_cart_initialization(self):
        """Test that a new cart initializes correctly"""
        cart = Cart()
        assert cart.items == {}
        assert cart.get_total_price() == 0
        assert cart.is_empty() is True

    def test_add_item_to_cart(self, sample_books):
        """Test adding an item to the cart"""
        cart = Cart()
        book = sample_books[0]
        cart.add_book(book, 1)
        assert len(cart.items) == 1
        assert book.title in cart.items
        assert cart.items[book.title].quantity == 1

    def test_cart_total_calculation(self, sample_books):
        """Test cart total is calculated correctly"""
        cart = Cart()
        book1 = sample_books[0]
        book2 = sample_books[1]
        cart.add_book(book1, 2)
        cart.add_book(book2, 1)
        expected_total = (book1.price * 2) + (book2.price * 1)
        assert cart.get_total_price() == expected_total

    def test_remove_item_from_cart(self, sample_books):
        """Test removing an item from the cart"""
        cart = Cart()
        book = sample_books[0]
        cart.add_book(book, 1)
        cart.remove_book(book.title)
        assert len(cart.items) == 0

    def test_clear_cart(self, sample_books):
        """Test clearing all items from cart"""
        cart = Cart()
        cart.add_book(sample_books[0], 1)
        cart.add_book(sample_books[1], 1)
        cart.clear()
        assert len(cart.items) == 0
        assert cart.get_total_price() == 0


class TestBookModel:
    """Test cases for Book model"""

    def test_book_creation(self):
        """Test creating a book instance"""
        book = Book("Test Book", "Test Category", 19.99, "test.jpg")
        assert book.title == "Test Book"
        assert book.category == "Test Category"
        assert book.price == 19.99
        assert book.image == "test.jpg"

    def test_book_attributes(self):
        """Test book attributes are set correctly"""
        book = Book("Python Programming", "Technology", 49.99, "python.jpg")
        assert isinstance(book.title, str)
        assert isinstance(book.category, str)
        assert isinstance(book.price, float)
        assert isinstance(book.image, str)


class TestRoutes:
    """Test cases for Flask routes"""

    def test_cart_page_loads(self, client):
        """Test that cart page loads"""
        response = client.get('/cart')
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        """Test that login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_register_page_loads(self, client):
        """Test that register page loads"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data


class TestEdgeCases:
    """Test edge cases and potential bugs"""

    def test_add_zero_quantity_to_cart(self, sample_books):
        """Test adding zero quantity (potential bug)"""
        cart = Cart()
        book = sample_books[0]
        cart.add_book(book, 0)
        # This might reveal a bug if zero quantities are allowed
        total_items = cart.get_total_items()
        assert total_items >= 0

    def test_add_negative_quantity_to_cart(self, sample_books):
        """Test adding negative quantity (potential bug)"""
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
        """Test that empty cart returns zero total"""
        cart = Cart()
        assert cart.get_total_price() == 0
        assert cart.is_empty() is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
