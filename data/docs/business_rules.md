# Business Rules

- **Revenue** is always calculated as `UnitPrice * Quantity` from OrderDetails.  
- Dates use SQLite `strftime` for filtering (`'%Y'` for year, `'%m'` for month).  
- `OrderDate` is the main column for time-based queries.  
- Category and Product names are in `Categories` and `Products` tables, respectively.  

