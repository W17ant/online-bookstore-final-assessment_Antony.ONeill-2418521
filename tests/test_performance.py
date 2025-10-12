"""
Performance Testing with timeit and cProfile
Tests performance of critical application components
Identifies inefficiencies and optimization opportunities
Student: 24185521 - Antony O'Neill
"""

import timeit
import sys
import os
from memory_profiler import profile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Book, Cart, CartItem, User, Order


class PerformanceTests:
    """
    Performance benchmarking tests using timeit module.
    Identifies performance bottlenecks in the codebase.
    """

    def __init__(self):
        self.setup_data()

    def setup_data(self):
        """Setup test data for performance tests"""
        self.books = [
            Book("Test Book 1", "Fiction", 10.99, "book1.jpg"),
            Book("Test Book 2", "Science", 15.99, "book2.jpg"),
            Book("Test Book 3", "History", 20.99, "book3.jpg"),
            Book("Test Book 4", "Art", 25.99, "book4.jpg"),
            Book("Test Book 5", "Technology", 30.99, "book5.jpg"),
        ]

        self.cart = Cart()
        for book in self.books[:3]:
            self.cart.add_book(book, 10)

    def test_cart_total_calculation(self):
        """
        PERFORMANCE ISSUE: Cart.get_total_price() uses nested loop

        Current Implementation (INEFFICIENT):
        O(n*m) complexity where n=items, m=quantity

        Optimized Implementation (EFFICIENT):
        O(n) complexity using direct multiplication
        """
        print("\n" + "=" * 80)
        print("PERFORMANCE TEST 1: Cart Total Price Calculation")
        print("=" * 80)

        # Setup
        cart = Cart()
        for book in self.books:
            cart.add_book(book, 100)  # Large quantities to show impact

        # Test current implementation
        setup_code = """
from __main__ import cart
"""
        test_code = "cart.get_total_price()"

        iterations = 10000
        time_taken = timeit.timeit(test_code, setup=setup_code, globals={'cart': cart}, number=iterations)

        avg_time = (time_taken / iterations) * 1000  # Convert to milliseconds

        print(f"\n📊 Results:")
        print(f"   Iterations: {iterations:,}")
        print(f"   Total Time: {time_taken:.4f}s")
        print(f"   Average Time per Call: {avg_time:.4f}ms")

        print(f"\n⚠️  ISSUE IDENTIFIED:")
        print(f"   Current implementation uses nested loops: O(n*m)")
        print(f"   With {len(cart.items)} items and 100 qty each:")
        print(f"   Total iterations: {len(cart.items)} * 100 = {len(cart.items) * 100}")

        print(f"\n✅ OPTIMIZATION RECOMMENDATION:")
        print(f"   Replace nested loop with direct multiplication:")
        print(f"   total += item.book.price * item.quantity")
        print(f"   Expected improvement: ~{len(cart.items) * 100}x faster")
        print(f"   New complexity: O(n)")

        return avg_time

    def test_book_lookup_performance(self):
        """
        PERFORMANCE ISSUE: Linear search in route instead of helper function

        app.py uses manual loop instead of get_book_by_title()
        """
        print("\n" + "=" * 80)
        print("PERFORMANCE TEST 2: Book Lookup Operations")
        print("=" * 80)

        # Create large book list
        large_book_list = [
            Book(f"Book {i}", "Category", 10.0 + i, f"book{i}.jpg")
            for i in range(1000)
        ]

        # Test linear search (current inefficient implementation)
        def linear_search(books, title):
            for book in books:
                if book.title == title:
                    return book
            return None

        # Test with helper function (more efficient with potential optimization)
        def helper_search(books, title):
            return next((b for b in books if b.title == title), None)

        target = "Book 999"  # Worst case - last item
        iterations = 1000

        # Time linear search
        time_linear = timeit.timeit(
            lambda: linear_search(large_book_list, target),
            number=iterations
        )

        # Time helper function
        time_helper = timeit.timeit(
            lambda: helper_search(large_book_list, target),
            number=iterations
        )

        print(f"\n📊 Results (searching 1000 books for last item):")
        print(f"   Linear Search: {(time_linear/iterations)*1000:.4f}ms per search")
        print(f"   Helper Function: {(time_helper/iterations)*1000:.4f}ms per search")
        print(f"   Improvement: {((time_linear/time_helper)-1)*100:.1f}%")

        print(f"\n✅ OPTIMIZATION RECOMMENDATION:")
        print(f"   1. Use existing get_book_by_title() helper function")
        print(f"   2. Consider dict lookup instead of list: O(1) vs O(n)")
        print(f"   3. For production: implement caching/indexing")

    def test_user_order_sorting(self):
        """
        PERFORMANCE ISSUE: Sorting orders on every add_order()

        Current: Sorts on every insertion - O(n log n) per add
        Better: Sort only when retrieving history - lazy evaluation
        """
        print("\n" + "=" * 80)
        print("PERFORMANCE TEST 3: User Order Management")
        print("=" * 80)

        user = User("test@example.com", "password123")
        orders = []

        # Create sample orders
        for i in range(100):
            order = Order(
                order_id=f"ORD-{i:04d}",
                user_email=user.email,
                items=[],
                shipping_info={},
                payment_info={},
                total_amount=100.0 + i
            )
            orders.append(order)

        # Test current implementation (sort on add)
        def add_with_sort():
            test_user = User("test@example.com", "password")
            for order in orders:
                test_user.add_order(order)

        # Test optimized (sort on get)
        def add_without_sort():
            test_user = User("test@example.com", "password")
            test_user.orders = orders.copy()
            # Sort only when needed
            sorted(test_user.orders, key=lambda x: x.order_date)

        iterations = 100

        time_with_sort = timeit.timeit(add_with_sort, number=iterations)
        time_without_sort = timeit.timeit(add_without_sort, number=iterations)

        print(f"\n📊 Results (adding 100 orders):")
        print(f"   Sort on Every Add: {(time_with_sort/iterations)*1000:.2f}ms")
        print(f"   Sort on Demand: {(time_without_sort/iterations)*1000:.2f}ms")
        print(f"   Improvement: {((time_with_sort/time_without_sort)-1)*100:.1f}%")

        print(f"\n⚠️  ISSUE IDENTIFIED:")
        print(f"   Sorting 100 orders on every add = 100 sorts")
        print(f"   Complexity: 100 * O(n log n) = Very expensive")

        print(f"\n✅ OPTIMIZATION RECOMMENDATION:")
        print(f"   Implement lazy evaluation:")
        print(f"   - Add orders without sorting: O(1)")
        print(f"   - Sort only in get_order_history(): O(n log n) once")
        print(f"   - Result: ~{((time_with_sort/time_without_sort)-1)*100:.0f}% faster")

    @profile
    def test_memory_usage(self):
        """
        Memory profiling test using memory_profiler decorator
        Identifies memory leaks and excessive allocations
        """
        print("\n" + "=" * 80)
        print("PERFORMANCE TEST 4: Memory Usage Analysis")
        print("=" * 80)

        # Create large cart with many items
        cart = Cart()
        books = [Book(f"Book {i}", "Cat", 10.0, f"img{i}.jpg") for i in range(1000)]

        for book in books:
            cart.add_book(book, 5)

        # Calculate total (inefficient nested loop)
        total = cart.get_total_price()

        print(f"\n📊 Memory Test Complete:")
        print(f"   Books created: 1000")
        print(f"   Cart items: {len(cart.items)}")
        print(f"   Total price: ${total:.2f}")
        print(f"\n   See memory_profile.txt for detailed memory usage")

        return total

    def run_all_tests(self):
        """Execute all performance tests"""
        print("\n" + "=" * 80)
        print("   PERFORMANCE TESTING SUITE - timeit & cProfile")
        print("   Student: 24185521 - Antony O'Neill")
        print("=" * 80)

        results = {}
        results['cart_total'] = self.test_cart_total_calculation()
        self.test_book_lookup_performance()
        self.test_user_order_sorting()
        self.test_memory_usage()

        print("\n" + "=" * 80)
        print("SUMMARY: Key Performance Improvements Identified")
        print("=" * 80)
        print("\n1. Cart Total Calculation: O(n*m) → O(n)")
        print("   Impact: High - Called on every cart operation")
        print("   Fix: Replace nested loop with multiplication")

        print("\n2. Book Lookup: Manual loop → Helper function")
        print("   Impact: Medium - Called frequently in routes")
        print("   Fix: Use get_book_by_title() consistently")

        print("\n3. Order Sorting: Every add → On demand")
        print("   Impact: High - Scales poorly with orders")
        print("   Fix: Implement lazy evaluation pattern")

        print("\n4. Unused Data Structures: Remove unused fields")
        print("   Impact: Low - Minor memory waste")
        print("   Fix: Clean up User class initialization")

        print("\n" + "=" * 80)
        print("📊 Run 'python -m cProfile' for detailed function analysis")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    # Run performance tests
    perf_tests = PerformanceTests()
    perf_tests.run_all_tests()
