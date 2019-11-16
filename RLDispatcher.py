import sys
from abc import ABC, abstractmethod
import sqlite3
import datetime
from PIL import Image, ImageFont, ImageDraw
from PyQt5.QtCore import pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QWidget, QListWidget, QLineEdit, QPushButton, QApplication, QLabel, QTableWidget, \
    QTableWidgetItem, QDialog, QVBoxLayout, QDialogButtonBox, QComboBox


class DbInteractor():
    def __init__(self):
        self.conn = sqlite3.connect('SimpleTrain')
        self.cursor = self.conn.cursor()

    def get_wagons(self):
        self.cursor.execute("SELECT wagon_name FROM wagons")
        results = self.cursor.fetchall()
        return results

    def insert_wagons(self, wagon_name):
        self.cursor.execute("INSERT INTO wagons (wagon_name) VALUES ('" + wagon_name + "')")
        self.conn.commit()

    def update_wagons(self, old_wagon_name, new_wagon_name):
        self.cursor.execute(
            "UPDATE wagons SET wagon_name = '" + new_wagon_name + "' WHERE wagon_name = '" + old_wagon_name + "'")
        self.conn.commit()

    def delete_wagons(self, wagon_name):
        self.cursor.execute("DELETE FROM wagons WHERE wagon_name = '" + wagon_name + "'")
        self.conn.commit()

    def get_stations(self):
        self.cursor.execute("SELECT station_name, amount_of_tracks FROM stations")
        results = self.cursor.fetchall()
        return results

    def insert_station(self, station_name, amount_of_tracks):
        self.cursor.execute(
            "INSERT INTO stations (station_name, amount_of_tracks) VALUES ('" + station_name + "', '" + amount_of_tracks + "')")
        self.conn.commit()

    def update_stations(self, station_name, new_station_name, new_amount_of_tracks):
        self.cursor.execute(
            "UPDATE stations set station_name = '" + new_station_name + "', amount_of_tracks = '" + new_amount_of_tracks + "' WHERE station_name = '" + station_name + "'")
        self.conn.commit()

    def delete_station(self, station_name):
        self.cursor.execute("DELETE FROM stations WHERE station_name = '" + station_name + "' ")
        self.conn.commit()

    def get_locomotives(self):
        self.cursor.execute("SELECT loco_name, loco_number FROM locomotives")
        results = self.cursor.fetchall()
        return results

    def insert_locomotive(self, loco_name, loco_number):
        self.cursor.execute(
            "INSERT INTO locomotives (loco_name, loco_number) VALUES ('" + loco_name + "', '" + loco_number + "')")
        self.conn.commit()

    def update_locomotives(self, loco_number, new_name, new_number):
        self.cursor.execute(
            "UPDATE locomotives SET loco_name = '" + new_name + "', loco_number = '" + new_number + "' WHERE loco_number = '" + loco_number + "'")
        self.conn.commit()

    def delete_locomotives(self, loco_number):
        self.cursor.execute("DELETE FROM locomotives  WHERE loco_number = '" + loco_number + "'")
        self.conn.commit()


class ImageCreator():
    def __init__(self):
        self.image = Image.open("exampleb.png")
        self.font = ImageFont.truetype('arial.ttf', 10)
        self.draw = ImageDraw.Draw(self.image)
        self.default_path = 'C:\Program Files (x86)\Steam\steamapps\common\Rolling Line\Modding\quickMod\SHEETS DEMO\quickMod_texture.png'

    def draw_my_nums(self, list_of_actions):
        position_x = 26
        position_y = 148
        step = 35
        self.image = Image.open("exampleb.png")
        self.draw = ImageDraw.Draw(self.image)
        for action in list_of_actions:
            self.draw.text((position_x, position_y), action, font=self.font, fill=(0, 0, 0, 255))
            position_y += step
        self.image.save(self.default_path)
        self.image.close()


class YesNoConfirmation(QDialog):
    def __init__(self, parent=None):
        super(YesNoConfirmation, self).__init__(parent)
        self.setWindowTitle('Confirm Action')
        self.layout = QVBoxLayout()

        self.text = QLabel('Are you sure you want to delete?')
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.layout)

    @staticmethod
    def get_confirmation(parent=None):
        dialog = YesNoConfirmation(parent)
        result = dialog.exec_()
        return (result == QDialog.Accepted)


class InputDialogSingle(QDialog):
    def __init__(self, title, parent=None):
        super(InputDialogSingle, self).__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()

        self.input_field = QLineEdit()
        self.layout.addWidget(self.input_field)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.layout)

    def get_output(self):
        return self.input_field.text()

    @staticmethod
    def get_new_item(title, parent=None):
        dialog = InputDialogSingle(title, parent)
        result = dialog.exec_()
        output = dialog.get_output()
        return (output, result == QDialog.Accepted)


class InputDialogMultiple(QDialog):
    def __init__(self, input_label_names):
        super().__init__()
        self.input_labels = input_label_names  # list
        self.labels = []
        self.input_fields = []
        self.layout = QVBoxLayout()

        self.create_labels_and_fields()
        self.bind_to_layout()

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.layout)

    def on_click_return_inputs(self):
        result = []
        for input in self.input_fields:
            result.append(input.text())
        return result

    def on_click_close_input(self):
        self.close()

    def create_labels_and_fields(self):
        for i in range(len(self.input_labels)):
            label_name = 'label_{}'.format(i)
            lineEdit_name = 'lineEdit_{}'.format(i)
            label = QLabel()
            label.setObjectName(label_name)
            label.setText(str(self.input_labels[i]))
            edit = QLineEdit()
            edit.setObjectName(lineEdit_name)
            self.labels.append(label)
            self.input_fields.append(edit)

    def bind_to_layout(self):
        i = 0
        for label in self.labels:
            self.layout.addWidget(label)
            self.layout.addWidget(self.input_fields[i])
            i += 1

    @staticmethod
    def get_multiple_inputs(input_label_names):
        dialog = InputDialogMultiple(input_label_names)
        result = dialog.exec_()
        output = dialog.on_click_return_inputs()
        return (output)


class GenericTableWidget(QDialog):
    changed_value_signal = pyqtSignal()

    def __init__(self, db, mode):
        super().__init__()
        self.db = db
        self.input_labels_names = []
        self.data_for_table = self.get_data_from_db()
        self.default_column = 0
        self.title = ''
        self.table = 0
        self.columns = 0

    def set_up_ui(self, mode):
        self.layout = QVBoxLayout()
        self.setWindowTitle(self.title)

        if self.data_for_table == None:
            rows = 0
        else:
            rows = len(self.data_for_table)

        self.table = QTableWidget(rows, self.columns)
        if self.data_for_table is not None:
            self.populate_table(self.data_for_table, self.table)
        self.layout.addWidget(self.table)
        self.add_button = QPushButton('Add')
        self.rename_button = QPushButton('Rename')
        self.delete_button = QPushButton('Delete')
        self.select_button = QPushButton('Select')

        self.button_box = QDialogButtonBox()
        self.layout.addWidget(self.button_box)
        self.button_box.addButton(self.select_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.add_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.rename_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.delete_button, QDialogButtonBox.ActionRole)

        self.select_button.clicked.connect(self.on_click_select)
        self.add_button.clicked.connect(self.on_click_add)
        self.rename_button.clicked.connect(self.on_click_rename)
        self.delete_button.clicked.connect(self.on_click_delete)
        if mode == 'add':
            self.button_box.removeButton(self.select_button)

        self.setLayout(self.layout)

    def on_click_select(self):
        return self.get_selected_item_text(self.default_column)

    def populate_table(self, data, table):
        row = 0
        for item in data:
            column = 0
            for sub_item in item:
                table.setItem(row, column, QTableWidgetItem(sub_item))
                column += 1
            row += 1

    def add_new_items_totable(self, new_items, table):
        row_count = table.rowCount()
        table.insertRow(row_count)
        column = 0
        for item in new_items:
            table.setItem(row_count, column, QTableWidgetItem(item))
            column += 1

    def on_click_add(self):
        new_items = InputDialogMultiple.get_multiple_inputs(self.input_labels_names)
        self.add_new_items_totable(new_items, self.table)
        self.add_to_db(new_items)
        self.changed_value_signal.emit()

    @abstractmethod
    def add_to_db(self, items):
        pass

    @abstractmethod
    def rename_to_db(self, old_item, new_item):
        pass

    @abstractmethod
    def delete_to_db(self, item_to_delete):
        pass

    @abstractmethod
    def get_data_from_db(self):
        pass

    def on_click_rename(self):
        selected_item = self.get_selected_item_text(self.default_column)
        new_items = InputDialogMultiple.get_multiple_inputs(self.input_labels_names)
        self.rename_to_db(selected_item, new_items)
        column = 0
        for item in new_items:
            self.table.setItem(self.table.currentItem().row(), column, QTableWidgetItem(item))
            column += 1
        self.changed_value_signal.emit()

    def get_selected_item_text(self, column):
        row = self.table.currentItem().row()
        return self.table.item(row, column).text()

    def get_items(self):
        items = []
        for row in range(self.table.rowCount()):
            items.append(self.table.item(row, self.default_column).text())
        return items

    def on_click_delete(self):
        if YesNoConfirmation.get_confirmation() == True:
            selected_item = self.get_selected_item_text(self.default_column)
            row_to_remove = self.table.currentItem().row()
            self.delete_to_db(selected_item)
            self.table.removeRow(row_to_remove)
        self.changed_value_signal.emit()


class WagonWidget(GenericTableWidget):
    def __init__(self, db, mode):
        super().__init__(db, mode)

        self.title = "Wagons"
        self.input_labels_names = ['Wagon Name']
        self.default_column = 0
        self.columns = 1
        self.set_up_ui(mode)

    def add_to_db(self, items):
        wagon_name = items[0]
        self.db.insert_wagons(wagon_name)

    def delete_to_db(self, item_to_delete):
        self.db.delete_wagons(item_to_delete)

    def rename_to_db(self, old_item_signature, new_items):
        old_wagon_name = old_item_signature
        new_wagon_name = new_items[0]
        self.db.update_wagons(old_wagon_name, new_wagon_name)

    def get_data_from_db(self):
        return self.db.get_wagons()


class StationWidget(GenericTableWidget):
    def __init__(self, db, mode):
        super().__init__(db, mode)
        self.title = "Stations"
        self.input_labels_names = ['Station Name', 'Amount of Tracks']
        self.default_column = 0
        self.columns = 2
        self.set_up_ui(mode)

    def add_to_db(self, items):
        station_name = items[0]
        amount_of_tracks = items[1]
        self.db.insert_station(station_name, amount_of_tracks)

    def delete_to_db(self, item_to_delete):
        station_name = item_to_delete
        self.db.delete_station(station_name)

    def rename_to_db(self, old_item_signature, new_items):
        new_station_name = new_items[0]
        new_amount_of_tracks = new_items[1]
        old_station_name = old_item_signature
        self.db.update_stations(old_station_name, new_station_name, new_amount_of_tracks)

    def get_data_from_db(self):
        return self.db.get_stations()


class LocoWidget(GenericTableWidget):
    def __init__(self, db, mode):
        super().__init__(db, mode)
        self.title = "Locomotives"
        self.input_labels_names = ['Locomotive Name', 'Locomotive Number']
        self.default_column = 1
        self.columns = 2
        self.set_up_ui(mode)

    def add_to_db(self, items):
        loco_name = items[0]
        loco_number = items[1]
        self.db.insert_locomotive(loco_name, loco_number)

    def delete_to_db(self, item_to_delete):
        loco_number = item_to_delete
        self.db.delete_locomotives(loco_number)

    def rename_to_db(self, old_item_signature, new_items):
        loco_number = old_item_signature
        new_name = new_items[0]
        print(new_name)
        new_number = new_items[1]
        print(new_number)
        self.db.update_locomotives(loco_number, new_name, new_number)

    def get_data_from_db(self):
        return self.db.get_locomotives()

    def get_items(self):
        items = []
        loco_string = ""
        for row in range(self.table.rowCount()):
            loco_string = self.table.item(row, 0).text() + "-" + self.table.item(row, self.default_column).text()
            items.append(loco_string)
        return items


class MyListView(QListWidget):
    def __init__(self, data):
        super().__init__()
        self.insert_my_items(data)
        self.setDragEnabled(True)

    def insert_my_items(self, data):
        for item in data:
            self.insertItem(0, item)

    def update_values(self, data):
        self.clear()
        self.insert_my_items(data)

    def mouseMoveEvent(self, event):
        drag = QDrag(self)
        mimedata = QMimeData()
        current_item_test = self.currentItem().text()
        mimedata.setText(current_item_test)
        drag.setMimeData(mimedata)
        drag.exec_()


class DropInLabel(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setAcceptDrops(True)
        self.setText(text)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        self.setText(e.mimeData().text())


class ActionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setDirection(QVBoxLayout.LeftToRight)
        self.labels = []
        self.avaliable_actions = ['Pick action:', 'Pick up:', 'Travel to:', 'Leave cars at:']

        self.set_combobox()

        self.setLayout(self.layout)

    def set_combobox(self):
        self.combobox = QComboBox()
        for action in self.avaliable_actions:
            self.combobox.addItem(action)
        self.layout.addWidget(self.combobox)
        self.combobox.activated.connect(self.set_labels_by_combobox)

    def set_labels(self, label_text):
        if len(self.labels) != 0:
            self.purge_old_labels()
            self.update()
        for i in range(len(label_text)):
            label_name = 'label_{}'.format(i)
            label = DropInLabel(label_text[i])
            label.setObjectName(label_name)
            self.labels.append(label)
        for label in self.labels:
            self.layout.addWidget(label)
        self.update()

    def purge_old_labels(self):
        for i in reversed(range(self.layout.count())):
            if i != 0:
                widgetToRemove = self.layout.itemAt(i).widget()
                self.layout.removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
        self.labels.clear()
        self.layout.update()

    def set_labels_by_combobox(self):
        if self.combobox.currentText() == 'Pick up:':
            self.set_labels(['drop loco here', 'drop wagon here', 'drop station here'])
        elif self.combobox.currentText() == 'Travel to:':
            self.set_labels(['drop loco here', 'station from', 'station to'])
        elif self.combobox.currentText() == 'Leave cars at:':
            self.set_labels(['drop car here', 'drop station here'])

    def get_filler_text(self):
        filler_words = []
        if self.combobox.currentText() == 'Pick up:':
            filler_words = ['Locomotive number ', 'pick up wagons ', 'at station ']
        elif self.combobox.currentText() == 'Travel to:':
            filler_words = ['Locomotive number ', 'travel from station ', 'to station ']
        elif self.combobox.currentText() == 'Leave cars at:':
            filler_words = ['Leave wagons ', 'at station ']
        return filler_words

    def get_composed_string(self):
        composed_string = ""
        filler_text = self.get_filler_text()
        i = 0
        for label in self.labels:
            composed_string += filler_text[i]
            composed_string += label.text()
            composed_string += " "
            i += 1
        return composed_string


class ActionList(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.actions = []

        self.add_button = QPushButton('Add new action')
        self.layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_button_click)

        self.setLayout(self.layout)

    def add_new_action_row(self):
        i = len(self.actions)
        name = 'label_{}'.format(i)
        action_row = ActionWidget()
        action_row.setObjectName(name)
        self.actions.append(action_row)
        self.layout.addWidget(action_row)
        self.layout.update()

    def get_actions(self):
        composed_actions = []
        for action in self.actions:
            composed_actions.append(action.get_composed_string())
        return composed_actions

    def add_button_click(self):
        self.add_new_action_row()


class MainWindowMyApp(QWidget):
    def __init__(self,version, parent=None):
        super(MainWindowMyApp, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.db = DbInteractor()
        self.image_creator = ImageCreator()
        self.setWindowTitle(version)

        self.loco_window = LocoWidget(self.db, "add")
        self.loco_window.changed_value_signal.connect(self.on_child_close)
        self.station_window = StationWidget(self.db, "add")
        self.station_window.changed_value_signal.connect(self.on_child_close)
        self.wagon_window = WagonWidget(self.db, "add")
        self.wagon_window.changed_value_signal.connect(self.on_child_close)

        self.loco_button = QPushButton('Configure locomotives')
        self.wagon_button = QPushButton('Configure wagons')
        self.station_button = QPushButton('Configure station')

        self.loco_button.clicked.connect(self.clicked_loco)
        self.wagon_button.clicked.connect(self.clicked_wagons)
        self.station_button.clicked.connect(self.clicked_stations)

        self.layout.addWidget(self.loco_button)
        self.layout.addWidget(self.wagon_button)
        self.layout.addWidget(self.station_button)

        # test
        self.list_wagons_label = QLabel('Available wagons:')
        self.list_wagons = MyListView(self.wagon_window.get_items())
        self.layout.addWidget(self.list_wagons_label)
        self.layout.addWidget(self.list_wagons)

        self.list_locos_label = QLabel('Available locomotives:')
        self.list_locos = MyListView(self.loco_window.get_items())
        self.layout.addWidget(self.list_locos_label)
        self.layout.addWidget(self.list_locos)

        self.list_stations_label = QLabel('Available stations:')
        self.list_stations = MyListView(self.station_window.get_items())
        self.layout.addWidget(self.list_stations_label)
        self.layout.addWidget(self.list_stations)

        self.action_list = ActionList()
        self.layout.addWidget(self.action_list)

        self.print_button = QPushButton('Print Order')
        self.print_button.clicked.connect(self.clicked_print)
        self.layout.addWidget(self.print_button)

        self.setLayout(self.layout)

    def clicked_loco(self):
        self.loco_window.show()

    def clicked_stations(self):
        self.station_window.show()

    def clicked_wagons(self):
        self.wagon_window.show()

    def clicked_print(self):
        my_list_of_actions = self.action_list.get_actions()
        self.image_creator.draw_my_nums(my_list_of_actions)

    def on_child_close(self):
        self.list_stations.update_values(self.station_window.get_items())
        self.list_stations.update()
        self.list_locos.update_values(self.loco_window.get_items())
        self.list_locos.update()
        self.list_wagons.update_values(self.wagon_window.get_items())
        self.list_wagons.update()


if __name__ == '__main__':
    app = QApplication([])
    gui = MainWindowMyApp('RlDispatcher version 0.01')
    gui.show()
    app.exec_()
