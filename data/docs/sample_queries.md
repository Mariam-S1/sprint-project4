# Sample Queries and SQL Examples

These examples illustrate how natural language questions can be translated into SQL queries, providing valuable training data for the model.

1.  **Question:** What are the total sales for each product in 1997?
    **SQL:**
    ```sql
    SELECT
      p.ProductName,
      SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS TotalSales
    FROM "Order Details" AS od
    JOIN Products AS p
      ON od.ProductID = p.ProductID
    JOIN Orders AS o
      ON od.OrderID = o.OrderID
    WHERE
      STRFTIME('%Y', o.OrderDate) = '1997'
    GROUP BY
      p.ProductName
    ORDER BY
      TotalSales DESC;
    ```

2.  **Question:** Show me all customers from Germany.
    **SQL:**
    ```sql
    SELECT
      CompanyName,
      ContactName,
      City
    FROM Customers
    WHERE
      Country = 'Germany';
    ```

3.  **Question:** How many orders were placed in Q2 of 1997?
    **SQL:**
    ```sql
    SELECT
      COUNT(OrderID) AS NumberOfOrders
    FROM Orders
    WHERE
      STRFTIME('%Y', OrderDate) = '1997' AND STRFTIME('%m', OrderDate) BETWEEN '04' AND '06';
    ```

4.  **Question:** What is the total revenue per employee?
    **SQL:**
    ```sql
    SELECT
      e.FirstName,
      e.LastName,
      SUM(od.UnitPrice * od.Quantity) AS TotalRevenue
    FROM Orders AS o
    JOIN "Order Details" AS od
      ON o.OrderID = od.OrderID
    JOIN Employees AS e
      ON o.EmployeeID = e.EmployeeID
    GROUP BY
      e.EmployeeID;
    ```
