import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QTextEdit, QWidget, QVBoxLayout,\
    QMessageBox, QHBoxLayout, QDateEdit, QFileDialog,QScrollArea,QFrame
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QShortcut
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QKeySequence
from datetime import datetime
from yahoo_fin import stock_info
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xml.etree.ElementTree as ET


class UserCredentials:
    def __init__(self):
        self.credentials = self.load_credentials()

    def load_credentials(self):
        try:
            with open("credentials.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"username": "admin", "password": "admin"}

    def save_credentials(self):
        with open("credentials.json", "w") as file:
            json.dump(self.credentials, file, indent=4)

    def validate_login(self, username, password):
        return username == self.credentials["username"] and password == self.credentials["password"]

    def update_credentials(self, username, password):
        self.credentials = {"username": username, "password": password}
        self.save_credentials()


def export_to_pdf(data, filename='export.pdf'):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    for i, record in enumerate(data):
        y_position = height - 30 * (i + 1)
        record_str = f"Date: {record['date']}, Amount: {record['amount']} {record['currency']}"
        c.drawString(72, y_position, record_str)
    c.save()


def export_to_xml(data, filename='export.xml'):
    root = ET.Element("IncomeData")
    for currency, incomes in data.daily_income.items():
        for income in incomes:
            income_element = ET.SubElement(root, "Income")
            ET.SubElement(income_element, "Currency").text = currency
            ET.SubElement(income_element, "Amount").text = income['amount']
            ET.SubElement(income_element, "Date").text = income['date']
            ET.SubElement(income_element, "Description").text = income.get('description', '')

    tree = ET.ElementTree(root)
    tree.write(filename, xml_declaration=True, encoding='utf-8', method="xml")


class BalanceDialog(QDialog):
    def __init__(self, total_income):
        super().__init__()
        self.setWindowTitle("Balance")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()
        for currency, total_amount in total_income.items():
            label = QLabel(f"{currency}: {total_amount}")
            layout.addWidget(label)
        self.setLayout(layout)


class IncomeData:
    def __init__(self):
        self.daily_income = {'USD': [], 'TRY': [], 'EUR': []}
        self.exchange_rate = self.fetch_exchange_rate()
        self.load_income_data()

    def fetch_exchange_rate(self):
        try:
            exchange_rate = stock_info.get_live_price("USDTRY=X")
            return exchange_rate
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to fetch exchange rate: {str(e)}")
            return None

    def add_income(self, currency, amount, date, description=""):
        self.daily_income[currency].append({'amount': amount, 'date': date, 'description': description})
        self.save_income_data()

    def get_total_income(self):
        total_income = {}
        for currency, incomes in self.daily_income.items():
            total_amount = sum(float(income_entry['amount']) for income_entry in incomes)
            total_income[currency] = total_amount
        return total_income

    def load_income_data(self):
        try:
            with open("Incomes.json", "r") as file:
                self.daily_income = json.load(file)
                for currency, incomes in self.daily_income.items():
                    for income in incomes:
                        income.setdefault('description', '')
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            QMessageBox.critical(None, "Error", "Failed to load income data. The file contains invalid JSON.")

    def save_income_data(self):
        with open("Incomes.json", "w") as file:
            json.dump(self.daily_income, file, indent=4)


class IncomeTracker(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.user_credentials = UserCredentials()
        self.setWindowTitle("Income Tracker")
        self.setFixedSize(QSize(650, 650))
        self.setStyleSheet("background-color: #222831; color: #EEEEEE;")
        self.setup_login_page()

    def get_date(self):
        now = datetime.now()
        return now.strftime("%A, %Y-%m-%d")

    def setup_login_page(self):
        login_frame = QWidget()
        login_layout = QVBoxLayout()
        login_frame.setLayout(login_layout)

        login_label = QLabel("Welcome to Income Tracker")
        login_label.setAlignment(Qt.AlignCenter)
        login_label.setStyleSheet("font-size: 24px; color: #76ABAE;")
        login_layout.addWidget(login_label)

        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter your username")
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter your password")
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.add_form_field(login_layout, "Username:", self.username_entry)
        self.add_form_field(login_layout, "Password:", self.password_entry)

        self.login_status_message = QLabel("")  # Dynamic feedback message
        self.login_status_message.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(self.login_status_message)

        login_button = self.create_button("Login", self.login, is_default=True)
        login_layout.addWidget(login_button)

        login_shortcut = QShortcut(QKeySequence("Return"), self)
        login_shortcut.activated.connect(self.login)

        login_layout.addStretch(1)

        self.setCentralWidget(login_frame)

    def add_form_field(self, layout, label_text, widget):
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #EEEEEE;")
        layout.addWidget(label)
        layout.addWidget(widget)

    def create_button(self, text, clicked_func, is_default=False):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton { font-size: 16px; background-color: #76ABAE; color: #222831; }
            QPushButton:hover { background-color: #88cccc; }
        """)
        button.clicked.connect(clicked_func)
        if is_default:
            button.setDefault(True)
        return button

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        if self.user_credentials.validate_login(username, password):
            self.setup_main_menu()
        else:
            self.login_status_message.setText("<font color='red'>Invalid username or password.</font>")

    def setup_user_settings(self):
        self.setWindowTitle("User Settings")

        settings_frame = QWidget()
        settings_layout = QVBoxLayout()
        settings_frame.setLayout(settings_layout)

        # Username
        new_username_entry = QLineEdit()
        new_username_entry.setPlaceholderText("New username")
        self.add_form_field(settings_layout, "New Username:", new_username_entry)

        # Password
        new_password_entry = QLineEdit()
        new_password_entry.setPlaceholderText("New password")
        new_password_entry.setEchoMode(QLineEdit.Password)
        self.add_form_field(settings_layout, "New Password:", new_password_entry)

        update_button = self.create_button("Update Credentials",
                                           lambda: self.update_credentials(new_username_entry.text(),
                                                                           new_password_entry.text()))
        settings_layout.addWidget(update_button)

        back_button = self.create_button("Back to Menu", self.setup_main_menu)
        settings_layout.addWidget(back_button)

        self.setCentralWidget(settings_frame)

    def update_credentials(self, username, password):
        if username and password:  # Simple validation
            self.user_credentials.update_credentials(username, password)
            QMessageBox.information(self, "Success", "Credentials updated successfully.")
            self.setup_login_page()
        else:
            QMessageBox.critical(self, "Error", "Username and password cannot be empty.")

    def setup_main_menu(self):
        main_menu_frame = QWidget()
        main_menu_layout = QVBoxLayout()
        main_menu_frame.setLayout(main_menu_layout)

        welcome_label = QLabel("Welcome to the Income Tracker!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; color: #76ABAE;")
        main_menu_layout.addWidget(welcome_label)

        date_label = QLabel("Today is: " + self.get_date())
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("font-size: 16px; color: #EEEEEE;")
        main_menu_layout.addWidget(date_label)

        if self.data.exchange_rate is not None:
            exchange_label = QLabel(f"USD to TRY Exchange Rate: {self.data.exchange_rate:.2f}")
            exchange_label.setAlignment(Qt.AlignCenter)
            exchange_label.setStyleSheet("font-size: 16px; color: #EEEEEE;")
            main_menu_layout.addWidget(exchange_label)

        button_texts = ["Add Income", "Add Expense", "Transactions", "Balance", "Export to PDF", "Export to XML", "User Settings",
                        "Exit"]
        for text in button_texts:
            method_name = f'action_{text.replace(" ", "_").lower()}'
            if text == "User Settings":
                method_name = 'setup_user_settings'
            button = self.create_button(text, getattr(self, method_name))
            main_menu_layout.addWidget(button)

        self.setCentralWidget(main_menu_frame)

    def delete_income(self, currency, index):
        try:
            del self.data.daily_income[currency][index]
            self.data.save_income_data()  # Save changes to the file
            self.action_transactions()  # Refresh the display
            QMessageBox.information(self, "Success", "Income deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete income: {str(e)}")

    def action_export_to_pdf(self):
        data_for_pdf = self.get_financial_data_for_pdf()
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'PDF files (*.pdf)')
        if filename:
            export_to_pdf(data_for_pdf, filename)

    def action_export_to_xml(self):
        data_for_xml = self.get_financial_data_for_xml()
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'XML files (*.xml)')
        if filename:
            export_to_xml(data_for_xml, filename)

    def get_financial_data_for_pdf(self):
        data = []
        for currency, incomes in self.data.daily_income.items():
            for income in incomes:
                income_with_currency = {**income, 'currency': currency}
                data.append(income_with_currency)
        return data

    def get_financial_data_for_xml(self):
        return self.data

    def action_add_income(self):
        self.setWindowTitle("Add Income")

        add_income_frame = QWidget()
        add_income_layout = QVBoxLayout()
        add_income_frame.setLayout(add_income_layout)

        # Currency
        currency_layout = QHBoxLayout()
        currency_label = QLabel("Currency:")
        self.currency_input = QLineEdit()
        currency_layout.addWidget(currency_label)
        currency_layout.addWidget(self.currency_input)

        # Amount
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)

        # Date
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)

        # Description
        description_layout = QHBoxLayout()
        description_label = QLabel("Description:")
        self.description_input = QLineEdit()
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_input)

        # Submit button
        submit_button = self.create_button("Submit", self.submit_income)

        add_income_layout.addLayout(currency_layout)
        add_income_layout.addLayout(amount_layout)
        add_income_layout.addLayout(date_layout)
        add_income_layout.addLayout(description_layout)  # Add description layout
        add_income_layout.addWidget(submit_button)

        back_button = self.create_button("Back to Menu", self.setup_main_menu)
        add_income_layout.addWidget(back_button)

        self.setCentralWidget(add_income_frame)

    def submit_income(self):
        currency = self.currency_input.text().upper()
        amount = self.amount_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")
        description = self.description_input.text()  # Get description input

        if currency in ["USD", "TRY", "EUR"] and amount.replace('.', '', 1).isdigit():
            self.data.add_income(currency, amount, date, description)  # Pass description to add_income
            QMessageBox.information(self, "Success", "Income added successfully.")
            self.setup_main_menu()
        else:
            QMessageBox.critical(self, "Error", "Invalid input. Please check the currency and amount.")

    def action_add_expense(self):
        self.setWindowTitle("Add Expense")

        add_expense_frame = QWidget()
        add_expense_layout = QVBoxLayout()
        add_expense_frame.setLayout(add_expense_layout)

        # Currency
        currency_layout = QHBoxLayout()
        currency_label = QLabel("Currency:")
        self.expense_currency_input = QLineEdit()
        currency_layout.addWidget(currency_label)
        currency_layout.addWidget(self.expense_currency_input)

        # Amount
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        self.expense_amount_input = QLineEdit()
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.expense_amount_input)

        # Date
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.expense_date_input = QDateEdit()
        self.expense_date_input.setDate(QDate.currentDate())
        self.expense_date_input.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.expense_date_input)
        # Description
        description_layout = QHBoxLayout()
        description_label = QLabel("Description:")
        self.expense_description_input = QLineEdit()
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.expense_description_input)

        # Submit button
        submit_button = self.create_button("Submit", self.submit_expense)

        add_expense_layout.addLayout(currency_layout)
        add_expense_layout.addLayout(amount_layout)
        add_expense_layout.addLayout(date_layout)
        add_expense_layout.addLayout(description_layout)  # Add description layout
        add_expense_layout.addWidget(submit_button)

        back_button = self.create_button("Back to Menu", self.setup_main_menu)
        add_expense_layout.addWidget(back_button)

        self.setCentralWidget(add_expense_frame)

    def submit_expense(self):
        currency = self.expense_currency_input.text().upper()
        amount = self.expense_amount_input.text()
        date = self.expense_date_input.date().toString("yyyy-MM-dd")
        description = self.expense_description_input.text()  # Get description input

        if currency in ["USD", "TRY", "EUR"] and amount.replace('.', '', 1).isdigit():
            # Pass description to add_income, use "-" before amount to denote expense
            self.data.add_income(currency, "-" + amount, date, description)
            QMessageBox.information(self, "Success", "Expense added successfully.")
            self.setup_main_menu()
        else:
            QMessageBox.critical(self, "Error", "Invalid input. Please check the currency and amount.")

    def action_transactions(self):
        self.setWindowTitle("Transactions")

        display_frame = QWidget()
        display_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #333;")  # Dark background for the scroll area
        scroll_widget = QWidget()
        scroll_widget.setLayout(display_layout)
        scroll_area.setWidget(scroll_widget)

        # Adjusted styles for better contrast
        for currency, incomes in self.data.daily_income.items():
            currency_label = QLabel(f"{currency} Transactions:")
            currency_label.setStyleSheet(
                "font-weight: bold; font-size: 18px; color: #FAFAFA;")  # Light font color for currency label
            display_layout.addWidget(currency_label)

            for index, income in enumerate(incomes):
                income_layout = QHBoxLayout()
                income_info = f"Date: {income['date']}, Amount: {income['amount']}"
                if 'description' in income:
                    income_info += f", Description: {income['description']}"
                income_label = QLabel(income_info)
                income_label.setStyleSheet(
                    "font-size: 16px; padding: 5px; color: #EEE;")  # Ensuring text is easily readable

                # Create and style the delete button
                delete_button = QPushButton("Delete")
                delete_button.setStyleSheet(
                    "font-size: 14px; padding: 5px; background-color: #FF6347; color: white;")
                delete_button.setFixedSize(80, 30)  # Set a fixed size for the delete button
                delete_button.clicked.connect(lambda checked, a=currency, b=index: self.delete_income(a, b))

                income_layout.addWidget(income_label)
                income_layout.addWidget(delete_button)

                frame = QFrame()
                frame.setLayout(income_layout)
                frame.setStyleSheet(
                    "background-color: #444; border-radius: 5px; padding: 5px;")
                display_layout.addWidget(frame)

        # Add reset button
        reset_button = self.create_button("Reset Transactions", self.reset_transactions)
        display_layout.addWidget(reset_button)

        back_button = self.create_button("Back to Menu", self.setup_main_menu)
        display_layout.addWidget(back_button)

        self.setCentralWidget(scroll_area)

    def reset_transactions(self):
        # Display confirmation dialog
        confirmation = QMessageBox.question(self, "Confirmation",
                                            "Are you sure you want to reset all transactions and balance?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            # Clear all transactions
            self.data.daily_income = {'USD': [], 'TRY': [], 'EUR': []}
            self.data.save_income_data()

            # Show message to indicate reset
            QMessageBox.information(self, "Success", "Transactions and balance reset successfully.")

            # Refresh the display
            self.action_transactions()

    def action_balance(self):
        total_income = self.data.get_total_income()
        balance_dialog = BalanceDialog(total_income)
        balance_dialog.exec_()

    def action_exit(self):
        self.close()

    def closeEvent(self, event: QCloseEvent):
        self.data.save_income_data()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("style.qss", "r") as stylefile:
        app.setStyleSheet(stylefile.read())
    income_data = IncomeData()
    tracker = IncomeTracker(income_data)
    tracker.show()
    sys.exit(app.exec_())
