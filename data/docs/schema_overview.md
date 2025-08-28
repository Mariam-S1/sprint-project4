# Northwind Database Schema Overview

The Northwind database contains information about a fictional company that sells food products. It's structured to track Customers, Orders, OrderDetails, Products, Suppliers, Employees, Shippers, Categories.

## Table Relationships

* **Customers** and **Orders**: A `CustomerID` links a customer to their orders. A single customer can have many orders (one-to-many relationship).
* **Employees** and **Orders**: An `EmployeeID` links an order to the employee who took it. One employee can take many orders (one-to-many relationship).
* **Orders** and **Order Details**: An `OrderID` links an order to its line items. An order can have multiple line items, one for each product (one-to-many relationship).
* **Products** and **Order Details**: A `ProductID` links an order line item to the product being sold. One product can appear in many orders (one-to-many relationship).
* **Products** and **Suppliers**: A `SupplierID` links a product to its supplier. One supplier can provide many products (one-to-many relationship).
* **Products** and **Categories**: A `CategoryID` links a product to its category. One category can contain many products (one-to-many relationship).
