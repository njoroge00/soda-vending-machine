import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QCheckBox, QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

DRINK_COST = 50
ACCEPTED_COINS = [10, 20, 40]
ACCEPTED_NOTES = [50, 100, 200, 500, 1000]
AVAILABLE_DRINKS = {
    "Cola": 10,
    "Sprite": 8,
    "Water": 15,
    "Juice": 12,
    "Fanta": 7,
    "Pepsi": 9
}


class VendingMachine(QWidget):
    def __init__(self):
        super().__init__()

        self.balance = 0
        self.selected_drinks = {drink: 0 for drink in AVAILABLE_DRINKS}
        self.dispensed_drinks = {drink: 0 for drink in AVAILABLE_DRINKS}
        self.available_quantities = AVAILABLE_DRINKS.copy()
        self.current_state = "Idle"  # Initialize the current state to Idle

        self.setWindowTitle("Soft Drink Vending Machine")
        self.layout = QVBoxLayout()

        # Add main icon image
        main_icon_label = QLabel()
        main_icon_pixmap = QPixmap("icons2/soft-drink1.png")
        main_icon_label.setPixmap(main_icon_pixmap)
        main_icon_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(main_icon_label)

        self.drink_images = {
            "Cola": "icons2/cola.png",
            "Sprite": "icons2/sprite.png",
            "Water": "icons2/water.png",
            "Juice": "icons2/juice.png",
            "Fanta": "icons2/fanta.png",
            "Pepsi": "icons2/pepsi.png"
        }

        self.drink_checkboxes = []
        for drink, image_path in self.drink_images.items():
            checkbox = QCheckBox(drink)
            image_label = QLabel()
            image_pixmap = QPixmap(image_path)
            image_label.setPixmap(image_pixmap)

            drink_layout = QHBoxLayout()
            drink_layout.addWidget(image_label)
            drink_layout.addWidget(checkbox)
            drink_layout.addStretch(1)

            main_layout = QHBoxLayout()
            main_layout.addLayout(drink_layout)
            main_layout.addStretch(1)

            self.layout.addLayout(main_layout)
            self.drink_checkboxes.append(checkbox)

        self.balance_label = QLabel("Balance: 0 shillings")
        self.layout.addWidget(self.balance_label)

        self.drink_label = QLabel()
        self.layout.addWidget(self.drink_label)

        self.state_label = QLabel("State: Idle")  # Label to display the current state
        self.layout.addWidget(self.state_label)

        self.select_drinks_label = QLabel("Select number of drinks:")
        self.layout.addWidget(self.select_drinks_label)

        self.drink_spinbox = QSpinBox()
        self.drink_spinbox.setMinimum(0)
        self.layout.addWidget(self.drink_spinbox)

        self.input_notes_label = QLabel("Input note amount(50, 100, 200, 500, 1000):")
        self.layout.addWidget(self.input_notes_label)

        self.note_spinbox = QSpinBox()
        self.note_spinbox.setMaximum(1000)
        self.layout.addWidget(self.note_spinbox)

        self.add_amount_button = QPushButton("Add Amount")
        self.add_amount_button.clicked.connect(self.insert_note)
        self.layout.addWidget(self.add_amount_button)

        self.coin_buttons = []
        for coin_value in ACCEPTED_COINS:
            coin_button = QPushButton(f"Insert {coin_value} shilling")
            coin_button.clicked.connect(lambda _, value=coin_value: self.insert_coin(value))
            self.coin_buttons.append(coin_button)
            self.layout.addWidget(coin_button)

        self.select_button = QPushButton("Dispense")
        self.select_button.clicked.connect(self.dispense_drinks)
        self.layout.addWidget(self.select_button)

        self.withdraw_button = QPushButton("Withdraw Balance")
        self.withdraw_button.clicked.connect(self.withdraw_balance)
        self.layout.addWidget(self.withdraw_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_machine)
        self.layout.addWidget(self.reset_button)

        self.setLayout(self.layout)

    def change_state(self, new_state):
        self.current_state = new_state
        self.state_label.setText(f"State: {new_state}")

    def insert_coin(self, coin_value):
        if self.current_state in ["Idle", "CoinsInserted"]:
            self.balance += coin_value
            self.balance_label.setText(f"Balance: {self.balance} shillings")
            self.change_state("CoinsInserted")
            if self.balance >= 50:
                self.change_state("Accept")

    def insert_note(self):
        if self.current_state in ["Idle"]:
            self.balance += self.note_spinbox.value()
            self.balance_label.setText(f"Balance: {self.balance} shillings")
            self.change_state("Accept")


    def update_drink_image(self, drink_name):
        # Load the appropriate image/icon for the selected drink
        image_path = self.drink_images.get(drink_name, "default.png")
        pixmap = QPixmap(image_path)
        self.drink_label.setPixmap(pixmap.scaledToWidth(200))


    def dispense_drinks(self):
        if self.current_state == "Accept":
            # Rest of the code remains unchanged
            selected_drinks = []
            drinks = [checkbox.text() for checkbox in self.drink_checkboxes if checkbox.isChecked()]
            for drink in drinks:
                quantity = self.drink_spinbox.value()
                selected_drinks.append((drink, quantity))

            if selected_drinks:
                total_cost = 0
                for drink, quantity in selected_drinks:
                    cost = DRINK_COST * quantity
                    total_cost += cost

                    self.selected_drinks[drink] += quantity
                    self.available_quantities[drink] -= quantity

                if self.balance >= total_cost:
                    self.balance -= total_cost
                    self.balance_label.setText(f"Balance: {self.balance} shillings")

                    self.drink_label.setText("Dispensing drinks:")
                    for drink, quantity in selected_drinks:
                        self.dispensed_drinks[drink] += quantity
                        self.drink_label.setText(
                            f"{self.drink_label.text()} {quantity} {drink},"
                        )
                    
                    self.update_ui()
                else:
                    QMessageBox.warning(
                        self,
                        "Insufficient Balance",
                        "You have insufficient balance to purchase the selected drinks.",
                        QMessageBox.Ok,
                    )

                if self.balance < 10:
                        self.change_state("Idle")
        else:
            QMessageBox.warning(
                self,
                "Invalid State",
                "The machine is not ready to dispense drinks.",
                QMessageBox.Ok,
            )

    def withdraw_balance(self):
        if self.current_state == "Accept":
            if self.balance > 0:
                QMessageBox.information(
                    self,
                    "Balance Withdrawal",
                    f"You have withdrawn {self.balance} shillings.",
                    QMessageBox.Ok,
                )
                self.balance = 0
                self.balance_label.setText("Balance: 0 shillings")
                self.change_state("Idle")
            else:
                QMessageBox.warning(
                    self,
                    "No Balance",
                    "You have no balance to withdraw.",
                    QMessageBox.Ok,
                )
        else:
            QMessageBox.warning(
                self,
                "Invalid State",
                "The machine is not ready to dispense drinks.",
                QMessageBox.Ok,
            )

    def reset_machine(self):
        self.balance = 0
        self.selected_drinks = {drink: 0 for drink in AVAILABLE_DRINKS}
        self.dispensed_drinks = {drink: 0 for drink in AVAILABLE_DRINKS}
        self.available_quantities = AVAILABLE_DRINKS.copy()

        self.balance_label.setText("Balance: 0 shillings")
        self.drink_label.setText("")
        self.drink_spinbox.setValue(0)
        self.note_spinbox.setValue(0)
        self.change_state("Idle")

        self.update_ui()

    def update_ui(self):
        for drink, checkbox in zip(AVAILABLE_DRINKS, self.drink_checkboxes):
            checkbox.setEnabled(self.available_quantities[drink] > 0)

        ####self.select_button.setEnabled(
            #any(checkbox.isChecked() for checkbox in self.drink_checkboxes)
            #and self.drink_spinbox.value() > 0
            #and self.balance >= 50

        self.withdraw_button.setEnabled(self.balance > 0)

        if self.current_state == "Idle":
            self.select_button.setEnabled(False)
            self.withdraw_button.setEnabled(False)

            self.reset_button.setFocus()

        self.state_label.setText(f"State: {self.current_state}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    vending_machine = VendingMachine()
    vending_machine.update_drink_image("Coke")  # Update the image for the initial drink
    vending_machine.show()
    sys.exit(app.exec())