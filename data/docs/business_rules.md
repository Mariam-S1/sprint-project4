# Business Rules and Definitions

This document outlines key business rules and calculations essential for interpreting user queries and generating correct SQL.

## Revenue Calculation

**Revenue** is calculated by summing the total price of all sold items. The formula is:
`(UnitPrice * Quantity * (1 - Discount))`
The discount is a decimal value (e.g., 0.1 for 10% off).

## Date & Time Handling

* Dates are stored in the `YYYY-MM-DD` format.
* To filter by a specific year, use `STRFTIME('%Y', OrderDate)`.
* To filter by quarter, you must use `STRFTIME('%m', OrderDate)` to check for months within that quarter.
    * Q1: months `01` to `03`
    * Q2: months `04` to `06`
    * Q3: months `07` to `09`
    * Q4: months `10` to `12`

### Late Orders
- Late = ShippedDate > RequiredDate.


### Discontinued Products
- **Products.Discontinued = 1** → Product is inactive.
## Data Ambiguity

* "Last year" is an ambiguous term. If the user asks for "last year's sales" without specifying a year, the agent should ask for clarification, such as "Do you mean sales from 1997 or 1998?"
