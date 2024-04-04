# Income Tracker

## Overview
The Income Tracker is a Python-based desktop application designed to help users manage and track their income in various currencies. Utilizing the PyQt5 framework, it offers a user-friendly graphical interface for adding, viewing, and deleting income records. The application also features currency conversion through `yahoo_fin` and the ability to export income data to a PDF file using `reportlab`.

## Features
- **User Authentication**: Simple login mechanism to protect access.
- **Income Management**: Add, view, and delete income records.
- **Multi-Currency Support**: Handles income in USD, TRY, and EUR, with easy extensibility to other currencies.
- **Exchange Rate Conversion**: Fetches current exchange rates for accurate income tracking in different currencies.
- **Data Persistence**: Income data is saved locally, ensuring no loss of data between sessions.
- **PDF Export**: Export your income records to a PDF file for easy sharing or printing.

## Installation

To run the Income Tracker, you will need Python installed on your system. The application depends on PyQt5, yahoo_fin, and reportlab packages. You can install these dependencies using pip:

```bash
pip3 install PyQt5 yahoo_fin reportlab

Usage
After launching the Income Tracker, you'll be greeted by the main window where you can start adding your income sources. Use the interface to add, view, or delete records as needed. Stock information can be viewed by navigating to the designated section within the application.

Default username/password admin/admin

Contributing
Contributions to the Income Tracker are welcome! If you have a suggestion to improve this application or want to report a bug, please feel free to open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

