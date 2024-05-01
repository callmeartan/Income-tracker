# Income Tracker

## Overview
The Income Tracker is a Python-based desktop application designed to help users manage and track their income in various currencies. Utilizing the PyQt5 framework, it offers a user-friendly graphical interface for adding, viewing, and deleting income records. The application also features currency conversion through `yahoo_fin` and the ability to export income data to both PDF and XML formats using `reportlab` and `xml.etree.ElementTree` respectively.

## Features
- **User Authentication**: Simple login mechanism to protect access to the application.
- **Income Management**: Add, view, and delete income records seamlessly.
- **Multi-Currency Support**: Handles income in USD, TRY, and EUR, with easy extensibility to other currencies.
- **Exchange Rate Conversion**: Fetches current exchange rates for accurate income tracking in different currencies.
- **Data Persistence**: Income data is saved locally, ensuring no loss of data between sessions.
- **PDF and XML Export**: Export your income records to PDF or XML files for easy sharing or further processing.

## Installation

To run the Income Tracker, you will need Python installed on your system. The application depends on PyQt5, yahoo_fin, and reportlab packages. You can install these dependencies using pip:

```bash
pip3 install PyQt5 yahoo_fin reportlab

Usage
Launching the Application: After installing the dependencies, launch the Income Tracker by executing the Python script IncomeTracker.py.
Login: Upon launching, you'll be prompted to log in. Use the default credentials: admin/admin. You can change these later in the User Settings.
Main Window: Once logged in, you'll be greeted by the main window. Here, you can start managing your income by adding, viewing, or deleting records.
Adding Income: To add a new income record, click on the "Add Income" button. Enter the currency, amount, date, and optional description, then click "Submit".
Viewing Income: Click on the "Transactions" button to view all income records. You can delete individual records from this view.
Exporting Data: To export your income records, click on either "Export to PDF" or "Export to XML". Choose the file destination and format, then click "Save".
Logging Out: You can log out of the application by clicking on the "Exit" button.
Default username/password admin/admin

Contributing
Contributions to the Income Tracker are welcome! If you have a suggestion to improve this application or want to report a bug, please feel free to open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

