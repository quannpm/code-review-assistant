"""
Test runner script để chạy các test cases cho Chat API
Sử dụng script này để test thực tế với mock data
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_java_hello_world_test():
    """Test case thực tế cho Java Hello World explanation"""
    
    print("=== Testing Java Hello World Code Explanation ===\n")
    
    # Đoạn code Java Hello World
    java_code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
    
    print("Input Java Code:")
    print(java_code)
    print("\n" + "="*50 + "\n")
    
    # Simulate expected AI response
    expected_response = """
**Giải thích đoạn code Java "Hello World":**

**1. Khai báo class:**
```java
public class HelloWorld
```
- `public`: Class có thể được truy cập từ bất kỳ đâu
- `class`: Từ khóa khai báo class trong Java
- `HelloWorld`: Tên class (phải trùng với tên file HelloWorld.java)

**2. Method main:**
```java
public static void main(String[] args)
```
- `public`: Method có thể được gọi từ bên ngoài
- `static`: Method thuộc về class, không cần tạo object
- `void`: Method không trả về giá trị
- `main`: Tên method - điểm bắt đầu chương trình Java
- `String[] args`: Mảng tham số command line

**3. In ra màn hình:**
```java
System.out.println("Hello, World!");
```
- `System.out`: Object để xuất dữ liệu ra console
- `println()`: Method in ra và xuống dòng
- `"Hello, World!"`: Chuỗi sẽ được in ra

**Output khi chạy:**
```
Hello, World!
```

**Ý nghĩa:** Đây là chương trình Java đơn giản nhất, thường dùng để học lập trình Java cơ bản.
"""
    
    print("Expected AI Response:")
    print(expected_response)
    print("\n" + "="*50 + "\n")
    
    return {
        "test_name": "Java Hello World Explanation",
        "input_code": java_code,
        "expected_response": expected_response,
        "test_type": "code_explanation",
        "language": "java"
    }

def run_java_quick_action_test():
    """Test case cho Java quick action (thêm comments)"""
    
    print("=== Testing Java Quick Action (Add Comments) ===\n")
    
    # Code Java không có comment
    input_code = """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
    
    public double divide(double a, double b) {
        if (b != 0) {
            return a / b;
        }
        return 0;
    }
}
"""
    
    print("Input Java Code (without comments):")
    print(input_code)
    print("\n" + "="*50 + "\n")
    
    # Expected output với comments
    expected_output = """
/**
 * Calculator class provides basic arithmetic operations
 * @author AI Assistant
 * @version 1.0
 */
public class Calculator {
    
    /**
     * Adds two integers
     * @param a first integer operand
     * @param b second integer operand
     * @return sum of a and b
     */
    public int add(int a, int b) {
        return a + b;
    }
    
    /**
     * Subtracts second integer from first integer
     * @param a first integer operand (minuend)
     * @param b second integer operand (subtrahend)
     * @return difference of a and b
     */
    public int subtract(int a, int b) {
        return a - b;
    }
    
    /**
     * Divides first double by second double
     * @param a dividend (number to be divided)
     * @param b divisor (number to divide by)
     * @return quotient of a divided by b, or 0 if b is zero
     */
    public double divide(double a, double b) {
        // Check for division by zero to prevent runtime error
        if (b != 0) {
            return a / b;
        }
        // Return 0 as default value for division by zero
        return 0;
    }
}
"""
    
    print("Expected AI Response (with comments added):")
    print(expected_output)
    print("\n" + "="*50 + "\n")
    
    return {
        "test_name": "Java Quick Action - Add Comments",
        "input_code": input_code,
        "expected_response": expected_output,
        "test_type": "quick_action",
        "action": "add_comments",
        "language": "java"
    }

def run_java_debug_test():
    """Test case cho Java debug action"""
    
    print("=== Testing Java Debug Action ===\n")
    
    # Code Java có lỗi
    buggy_code = """
public class BuggyCode {
    public static void main(String[] args) {
        int[] numbers = {1, 2, 3, 4, 5};
        
        // Bug: Array index out of bounds
        for (int i = 0; i <= numbers.length; i++) {
            System.out.println(numbers[i]);
        }
        
        // Bug: Potential division by zero
        int result = divide(10, 0);
        System.out.println("Result: " + result);
    }
    
    public static int divide(int a, int b) {
        return a / b;  // No check for b == 0
    }
}
"""
    
    print("Input Java Code (with bugs):")
    print(buggy_code)
    print("\n" + "="*50 + "\n")
    
    expected_debug_response = """
**Phát hiện các lỗi trong code Java:**

**1. Array Index Out of Bounds (Line 6):**
```java
// FAIL: i <= numbers.length
for (int i = 0; i <= numbers.length; i++) {
    System.out.println(numbers[i]);
}

// PASS: i < numbers.length
for (int i = 0; i < numbers.length; i++) {
    System.out.println(numbers[i]);
}
```
**Giải thích:** Array có index từ 0 đến length-1, dùng `<=` sẽ gây lỗi khi truy cập index = length.

**2. Division by Zero (Line 11-16):**
```java
// FAIL: Không kiểm tra chia cho 0
public static int divide(int a, int b) {
    return a / b;
}

// PASS: Thêm kiểm tra
public static int divide(int a, int b) {
    if (b == 0) {
        System.out.println("Error: Division by zero!");
        return 0; // hoặc throw exception
    }
    return a / b;
}
```

**Code đã sửa:**
```java
public class FixedCode {
    public static void main(String[] args) {
        int[] numbers = {1, 2, 3, 4, 5};
        
        // Fixed: Array iteration
        for (int i = 0; i < numbers.length; i++) {
            System.out.println(numbers[i]);
        }
        
        // Fixed: Safe division
        int result = divide(10, 0);
        System.out.println("Result: " + result);
    }
    
    public static int divide(int a, int b) {
        if (b == 0) {
            System.out.println("Error: Cannot divide by zero!");
            return 0;
        }
        return a / b;
    }
}
```
"""
    
    print("Expected AI Debug Response:")
    print(expected_debug_response)
    print("\n" + "="*50 + "\n")
    
    return {
        "test_name": "Java Debug Action",
        "input_code": buggy_code,
        "expected_response": expected_debug_response,
        "test_type": "quick_action",
        "action": "debug",
        "language": "java"
    }

def run_all_java_tests():
    """Chạy tất cả test cases cho Java"""
    
    print("Running All Java Test Cases for Chat API\n")
    print("="*60)
    
    test_results = []
    
    # Test 1: Hello World Explanation
    test_results.append(run_java_hello_world_test())
    
    # Test 2: Quick Action - Add Comments
    test_results.append(run_java_quick_action_test())
    
    # Test 3: Debug Action
    test_results.append(run_java_debug_test())
    
    # Summary
    print("Test Summary:")
    print("="*60)
    for i, test in enumerate(test_results, 1):
        print(f"{i}. {test['test_name']}")
        print(f"   Language: {test['language']}")
        print(f"   Type: {test['test_type']}")
        if 'action' in test:
            print(f"   Action: {test['action']}")
        print()
    
    print(f"Total test cases prepared: {len(test_results)}")
    print("\n" + "="*60)
    print("These test cases can be used to verify:")
    print("1. Code explanation functionality")
    print("2. Quick actions (comment, debug)")
    print("3. Java language support")
    print("4. Response quality and format")
    
    return test_results

if __name__ == "__main__":
    # Chạy tất cả test cases
    results = run_all_java_tests()
