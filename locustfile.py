"""
Locust Load Testing Script for Online Bookstore
Student: 24185521 - Antony O'Neill

Tests performance of optimized functionality:
1. Cart total calculation (O(n*m) → O(n) optimization)
2. Order history retrieval (eager → lazy sorting optimization)
3. Overall application performance under load

Usage:
    # Install locust first
    pip install locust

    # Run Flask app in one terminal
    python app.py

    # Run Locust in another terminal
    locust -f locustfile.py

    # Open browser to http://localhost:8089
    # Set: Users=50, Spawn rate=5, Host=http://localhost:5000
"""

from locust import HttpUser, task, between
import random


class BookstoreUser(HttpUser):
    """
    Simulates a user browsing and shopping on the bookstore.

    This load test focuses on endpoints that use the optimized functions:
    - Cart operations (tests optimized get_total_price)
    - Checkout process (tests optimized discount code handling)
    - Order history (tests optimized lazy sorting)
    """

    # Wait 1-3 seconds between tasks (realistic user behavior)
    wait_time = between(1, 3)

    # Sample data
    books = ["The Great Gatsby", "1984", "I Ching", "Moby Dick"]

    def on_start(self):
        """
        Called when a simulated user starts.
        Register and login to test authenticated features.
        """
        # Register a unique user for this load test
        user_id = random.randint(1000, 9999)
        self.email = f"loadtest{user_id}@example.com"
        self.password = "TestPass123!"

        # Register
        self.client.post("/register", data={
            "email": self.email,
            "password": self.password,
            "name": f"Load Test User {user_id}"
        })

        # Login
        self.client.post("/login", data={
            "email": self.email,
            "password": self.password
        })

    @task(5)
    def browse_books(self):
        """
        Task 1: Browse the book catalog (Weight: 5)
        Most common user action - high frequency
        """
        self.client.get("/", name="Browse Home Page")

    @task(3)
    def add_to_cart(self):
        """
        Task 2: Add books to cart (Weight: 3)
        TESTS OPTIMIZATION: Cart.get_total_price() is called

        This tests the O(n*m) → O(n) optimization.
        With high quantities, the difference is dramatic.
        """
        book = random.choice(self.books)
        quantity = random.randint(1, 10)  # Test with varying quantities

        with self.client.post("/add-to-cart",
                             data={"title": book, "quantity": quantity},
                             catch_response=True,
                             name="Add to Cart (Optimized)") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(2)
    def view_cart(self):
        """
        Task 3: View shopping cart (Weight: 2)
        TESTS OPTIMIZATION: Calls get_total_price() on page load
        """
        self.client.get("/cart", name="View Cart (Tests Total Calc)")

    @task(1)
    def update_cart(self):
        """
        Task 4: Update cart quantities (Weight: 1)
        TESTS OPTIMIZATION: Tests quantity validation fix (Bug #1)
        Also triggers get_total_price() recalculation
        """
        book = random.choice(self.books)
        new_quantity = random.randint(1, 20)  # Test with larger quantities

        self.client.post("/update-cart",
                        data={"title": book, "quantity": new_quantity},
                        name="Update Cart (Validation + Total)")

    @task(1)
    def checkout_flow(self):
        """
        Task 5: Complete checkout process (Weight: 1)
        TESTS OPTIMIZATIONS:
        - Cart total calculation (multiple calls)
        - Discount code case-insensitivity (Bug #3 fix)
        - Order sorting (lazy evaluation)
        """
        # First, make sure cart has items
        book = random.choice(self.books)
        self.client.post("/add-to-cart", data={"title": book, "quantity": 2})

        # View checkout page (triggers cart total)
        self.client.get("/checkout", name="Checkout Page")

        # Test discount codes (case-insensitive fix)
        discount = random.choice(["SAVE10", "save10", "WELCOME20", ""])

        # Complete checkout
        with self.client.post("/process-checkout",
                             data={
                                 "name": "Load Test User",
                                 "email": self.email,
                                 "address": "123 Test Street",
                                 "city": "Test City",
                                 "zip_code": "12345",
                                 "payment_method": "credit_card",
                                 "card_number": "4532123456789012",
                                 "expiry_date": "12/25",
                                 "cvv": "123",
                                 "discount_code": discount
                             },
                             catch_response=True,
                             name="Process Checkout (Full Flow)") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Checkout failed: {response.status_code}")

    @task(1)
    def view_account(self):
        """
        Task 6: View account/order history (Weight: 1)
        TESTS OPTIMIZATION: Lazy order sorting (get_order_history)

        This is where the eager→lazy sorting optimization shows impact.
        """
        self.client.get("/account", name="View Account (Lazy Sorting)")


class StressTestUser(HttpUser):
    """
    Aggressive user for stress testing optimizations.

    This user adds many items with high quantities to stress-test
    the cart total calculation optimization (O(n*m) vs O(n)).
    """

    wait_time = between(0.5, 1.5)  # Faster actions for stress testing

    books = ["The Great Gatsby", "1984", "I Ching", "Moby Dick"]

    @task(1)
    def stress_cart_operations(self):
        """
        Stress test: Add multiple items with high quantities

        Before optimization: O(n*m) = O(4*100) = 400 iterations
        After optimization: O(n) = O(4) = 4 iterations

        100x performance improvement!
        """
        # Add all books with high quantities
        for book in self.books:
            self.client.post("/add-to-cart",
                           data={"title": book, "quantity": 50},
                           name="Stress: High Qty Add")

        # View cart (triggers get_total_price with 4 items × 50 qty = 200 total items)
        self.client.get("/cart", name="Stress: View Large Cart")

        # Update quantities (more stress)
        for book in self.books:
            self.client.post("/update-cart",
                           data={"title": book, "quantity": 100},
                           name="Stress: Update to 100 Qty")


# Run directly for quick test
if __name__ == "__main__":
    import subprocess
    print("=" * 80)
    print("LOCUST LOAD TESTING - Online Bookstore Performance")
    print("Student: 24185521 - Antony O'Neill")
    print("=" * 80)
    print("\n📋 Instructions:")
    print("1. Ensure Flask app is running: python app.py")
    print("2. Run Locust: locust -f locustfile.py")
    print("3. Open: http://localhost:8089")
    print("4. Configure:")
    print("   - Number of users: 50")
    print("   - Spawn rate: 5 users/sec")
    print("   - Host: http://localhost:5000")
    print("5. Click 'Start Swarming' and watch the charts!")
    print("\n📸 Screenshot These Metrics:")
    print("   - Requests per second (RPS)")
    print("   - Response time percentiles (50th, 95th, 99th)")
    print("   - Total request count")
    print("   - Failure rate")
    print("\n🎯 Focus on 'Cart' and 'Checkout' endpoints")
    print("   These use the optimized O(n) cart total calculation!")
    print("=" * 80)
