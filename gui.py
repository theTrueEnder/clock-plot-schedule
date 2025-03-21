import json
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLabel,
                             QColorDialog, QComboBox, QFileDialog, QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from scheduler_sheet import SheetScheduler
from scheduler_clock_plot import SchedulePlotter

CONFIG_FILE = "config-files/config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='UTF-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"workdays": [], "prev_week_night": False, "next_week_night": False, "colors": {}}

def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='UTF-8') as f:
        json.dump(data, f, indent=4)

class WorkScheduleApp(QWidget):
    def __init__(self):
        super().__init__()

        self.config = load_config()

        main_layout = QVBoxLayout()

        # Workdays and Colors Section (Side by Side)
        workdays_colors_layout = QHBoxLayout()

        # Workdays Section
        workdays_layout = QVBoxLayout()
        lbl = QLabel("<h3>Select Workdays:</h3>")
        lbl.setAlignment(Qt.AlignmentFlag.AlignBottom)
        workdays_layout.addWidget(lbl)
        self.prev_week_night = QCheckBox("< Prev Saturday")
        workdays_layout.addWidget(self.prev_week_night)
        self.days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.day_checkboxes = {day: QCheckBox(day) for day in self.days}
        for day, checkbox in self.day_checkboxes.items():
            workdays_layout.addWidget(checkbox)

        workdays_colors_layout.addLayout(workdays_layout)

        # Previous/Next Week Night Checkboxes
        self.next_week_night = QCheckBox("> Next Sunday")
        workdays_layout.addWidget(self.next_week_night)
        workdays_layout.addStretch()


        # Colors Section
        colors_layout = QVBoxLayout()
        colors_layout.addWidget(QLabel("<h3>Select Colors:</h3>"))
        self.color_selectors = {}

        # Color Pickers - Top Justified
        for category in ["awake", "asleep", "commute", "work"]:
            btn = QPushButton(f"Select {category.capitalize()} Color")
            btn.clicked.connect(lambda _, c=category: self.select_color(c))
            self.color_selectors[category] = btn
            colors_layout.addWidget(btn)

        # Spacer to Push File Picker to Bottom
        colors_layout.addStretch()

        # File Picker - Bottom Justified
        verticalSpacer = QSpacerItem(10, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        colors_layout.addItem(verticalSpacer)
        colors_layout.addWidget(QLabel("<h3>Select Config File:</h3>"))
        self.file_label = QLabel("Config File: <code>config-files/config.json</code>")
        colors_layout.addWidget(self.file_label)

        file_btn = QPushButton("Select Config File")
        file_btn.clicked.connect(self.select_config_file)
        colors_layout.addWidget(file_btn)

        workdays_colors_layout.addLayout(colors_layout)        
        main_layout.addLayout(workdays_colors_layout)
        main_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        

        

        # Save Button
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background-color: green; color: white;")
        save_btn.clicked.connect(self.save_settings)
        main_layout.addWidget(save_btn)

        verticalSpacer = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(verticalSpacer)
        
        # Clock Plot and Schedule Sheet Section (Side by Side)
        plot_schedule_layout = QHBoxLayout()




        # Generate Clock Plot Section
        clock_plot_layout = QVBoxLayout()
        clock_plot_layout.addWidget(QLabel("<h3>Generate Clock Plot:</h3>"))
        self.clock_plot_dropdown = QComboBox()
        
        self.titles = [schedule['title'] for schedule in self.config['schedule_patterns']]
        self.clock_plot_dropdown.addItems(self.titles)
        clock_plot_layout.addWidget(self.clock_plot_dropdown)

        self.clock_plot_save_image = QCheckBox("Save Results (PNG)")
        self.clock_plot_save_image.setChecked(True)
        clock_plot_layout.addWidget(self.clock_plot_save_image)

        clock_plot_btn = QPushButton("Run")
        clock_plot_btn.clicked.connect(self.run_clock_plot)
        clock_plot_layout.addWidget(clock_plot_btn)

        plot_schedule_layout.addLayout(clock_plot_layout)

        # Generate Schedule Sheet Section
        schedule_sheet_layout = QVBoxLayout()
        schedule_sheet_layout.addWidget(QLabel("<h3>Generate Schedule Sheet:</h3>"))
        
        
        self.schedule_sheet_save_image = QCheckBox("Save Results (PNG, CSV)")
        self.schedule_sheet_save_image.setChecked(True)
        schedule_sheet_layout.addWidget(self.schedule_sheet_save_image)
        

        schedule_sheet_btn = QPushButton("Run")
        schedule_sheet_btn.clicked.connect(self.run_schedule_sheet)
        schedule_sheet_layout.addWidget(schedule_sheet_btn)
        schedule_sheet_layout.addStretch()

        plot_schedule_layout.addLayout(schedule_sheet_layout)

        main_layout.addLayout(plot_schedule_layout)
        main_layout.addItem(verticalSpacer)

        # Exit Button
        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet("background-color: red; color: white;")
        exit_btn.clicked.connect(self.close)
        main_layout.addWidget(exit_btn)

        self.setLayout(main_layout)
        self.load_settings()


    def select_config_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Config File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            global CONFIG_FILE
            CONFIG_FILE = file_path
            # TODO
            # loc = max(file_path.index('/'), file_path.index('\\'))
            # short_file_path = file_path[loc+1:]
            short_file_path = file_path
            self.file_label.setText(f"Config File: <code>{short_file_path}</code>")
            self.config = load_config()
            self.load_settings()

    def load_settings(self):
        for day, checkbox in self.day_checkboxes.items():
            checkbox.setChecked(day in self.config.get("workdays", []))

        self.prev_week_night.setChecked(self.config.get("prev_week_night", False))
        self.next_week_night.setChecked(self.config.get("next_week_night", False))

        for category, color in self.config.get("colors", {}).items():
            if category in self.color_selectors:
                self.set_button_color(self.color_selectors[category], QColor(color))

    def save_settings(self):
        self.config["workdays"] = [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]
        self.config["prev_week_night"] = self.prev_week_night.isChecked()
        self.config["next_week_night"] = self.next_week_night.isChecked()
        self.config["colors"] = {category: self.color_selectors[category].palette().button().color().name() for category in self.color_selectors}
        self.config["colors"].update({"empty": "#FFFFFF"})
        save_config(self.config)

    def select_color(self, category):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_button_color(self.color_selectors[category], color)

    def set_button_color(self, button, color):
        button.setStyleSheet(f"background-color: {color.name()};")

    def run_clock_plot(self):
        option = self.clock_plot_dropdown.currentText()
        save_image = self.clock_plot_save_image.isChecked()
        print(f"Running Clock Plot: {option}, Save Image: {save_image}")
        scheduler = SchedulePlotter(save_image)
        scheduler.load_schedule_data(file_path=CONFIG_FILE)
        scheduler.plot_one_schedule(option)

    def run_schedule_sheet(self):
        save_image = self.schedule_sheet_save_image.isChecked()
        print(f"Running Schedule Sheet, Save Image: {save_image}")
        scheduler = SheetScheduler(CONFIG_FILE)
        scheduler.plot_schedule()
        if save_image:
            scheduler.save_to_csv()
            scheduler.save_to_png()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WorkScheduleApp()
    window.setWindowTitle("Night Shift Schedule Helper")
    window.show()
    sys.exit(app.exec())
