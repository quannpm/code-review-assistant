# Java Code Conventions

## 1. Quy tắc đặt tên (Naming Conventions)

-   **Class**: Viết hoa chữ cái đầu của mỗi từ. Ví dụ: `CustomerOrder`,
    `StringBuilder`.
-   **Interface**: Tương tự class. Ví dụ: `Runnable`, `Serializable`.
-   **Method**: Chữ cái đầu thường, các từ sau viết hoa chữ cái đầu. Ví
    dụ: `calculateTotal()`, `toString()`.
-   **Biến (variable)**: Camel case, bắt đầu bằng chữ thường. Ví dụ:
    `userName`, `orderCount`.
-   **Hằng số (constant)**: Viết hoa toàn bộ, cách nhau bằng `_`. Ví dụ:
    `MAX_SIZE`, `PI`.
-   **Package**: Viết thường toàn bộ, ngắn gọn. Ví dụ:
    `com.example.project`.

## 2. Quy tắc định dạng (Formatting Conventions)

-   Thụt lề bằng **4 khoảng trắng** (không dùng tab).

-   Mỗi dòng code không quá **120 ký tự**.

-   Mở dấu ngoặc `{` cùng dòng với khai báo.

    ``` java
    if (condition) {
        // code
    } else {
        // code
    }
    ```

## 3. Quy tắc comment (Comment Conventions)

-   Dùng `//` cho comment ngắn.

-   Dùng `/* ... */` cho block comment.

-   Dùng `/** ... */` cho Javadoc:

    ``` java
    /**
     * Tính tổng 2 số nguyên.
     * @param a số thứ nhất
     * @param b số thứ hai
     * @return tổng a + b
     */
    public int sum(int a, int b) {
        return a + b;
    }
    ```

## 4. Quy tắc tổ chức code (Code Organization)

-   Thứ tự trong class:
    1.  Hằng số (constants)
    2.  Thuộc tính (fields)
    3.  Constructor
    4.  Public methods
    5.  Protected methods
    6.  Private methods
-   Mỗi class nằm trong **1 file riêng**, tên file trùng với tên class.

## 5. Một số quy tắc khác

-   Tránh dùng `magic numbers`, thay bằng hằng số có tên rõ ràng.
-   Luôn kiểm tra `null` trước khi sử dụng đối tượng.
-   Ưu tiên sử dụng `StringBuilder` thay cho phép cộng chuỗi trong vòng
    lặp.
