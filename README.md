# About
This is a software product for automating the work of a cashier in a store.

![pic1](https://i.imgur.com/ax3W8Gz.png)

To test the program you can use barcodes stored in the sqlite3 database file “shop.db”. 
You can use ID “1” and password “1234” for authorization. Other passwords and IDs are also specified in the database file.

![pic2](https://i.imgur.com/HPkyy8v.png)

Currently, you can add items by entering a barcode, delete items, change their quantity, and there is also an option to clear the entire list. After successful transaction of the purchase, the cash receipt is displayed in the command line, and the employee is ready to serve the next customer.

The ability to delete items and change the number of items in those items anywhere, not just the last ones, should be added. Also, we should add printing a PDF file of the cash receipt instead of displaying it in the console.

Among the bugs that should be fixed first of all is the lack of protection against the situation when several items in the database contain the same barcodes and store ID at the same time. In such a case, the result of the program operation is unpredictable and will most likely lead to an error.