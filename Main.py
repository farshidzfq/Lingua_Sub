import sys
import time
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QFileDialog, QComboBox, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from googletrans import Translator
from langdetect import detect, DetectorFactory

# برای نتایج پایدار در تشخیص زبان
DetectorFactory.seed = 0

# تنظیمات لاگ
logging.basicConfig(filename='translator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SubtitleTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Layouts
        mainLayout = QVBoxLayout()
        formLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        progressLayout = QVBoxLayout()

        # Widgets
        self.inputFileEdit = QLineEdit()
        self.outputFileEdit = QLineEdit()
        self.destLangCombo = QComboBox()
        self.progressBar = QProgressBar()
        self.progressLabel = QLabel('Processing: 0/0 lines')

        # Configure Widgets
        self.inputFileEdit.setPlaceholderText("Select SRT file...")
        self.outputFileEdit.setPlaceholderText("Output file path...")
        self.destLangCombo.addItems(["English", "Farsi", "Deutsch"])

        browseInputBtn = QPushButton("Browse...")
        browseOutputBtn = QPushButton("Save As...")
        translateBtn = QPushButton("Translate")

        # Set Font
        font = QFont("Arial", 12)
        self.setFont(font)
        self.inputFileEdit.setFont(font)
        self.outputFileEdit.setFont(font)
        self.destLangCombo.setFont(font)
        self.progressLabel.setFont(font)
        self.progressBar.setFont(font)
        browseInputBtn.setFont(font)
        browseOutputBtn.setFont(font)
        translateBtn.setFont(font)

        # Set Icons
        browseInputBtn.setIcon(QIcon(QPixmap("icons/open.png")))
        browseOutputBtn.setIcon(QIcon(QPixmap("icons/save.png")))
        translateBtn.setIcon(QIcon(QPixmap("icons/translate.png")))

        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #333;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-weight: bold;
                color: #4A4A4A;
                margin-bottom: 5px;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
                background-color: #fafafa;
                margin-bottom: 10px;
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
                background-color: #fafafa;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 8px;
                cursor: pointer;
                margin: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 8px;
                background-color: #f3f3f3;
                height: 25px;
                margin-top: 10px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 8px;
            }
        """)

        # Layout Setup
        formLayout.addWidget(QLabel("Select SRT file:"))
        formLayout.addWidget(self.inputFileEdit)
        formLayout.addWidget(browseInputBtn)

        formLayout.addWidget(QLabel("Output file path:"))
        formLayout.addWidget(self.outputFileEdit)
        formLayout.addWidget(browseOutputBtn)

        formLayout.addWidget(QLabel("Select destination language:"))
        formLayout.addWidget(self.destLangCombo)

        buttonLayout.addWidget(translateBtn)

        progressLayout.addWidget(self.progressBar)
        progressLayout.addWidget(self.progressLabel)

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addLayout(progressLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle('Subtitle Translator')
        self.setWindowIcon(QIcon(QPixmap("icons/app_icon.png")))  # Set the application icon

        # Connect buttons
        browseInputBtn.clicked.connect(self.select_input_file)
        browseOutputBtn.clicked.connect(self.select_output_path)
        translateBtn.clicked.connect(self.start_translation)
        
    def select_input_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select SRT File", "", "SRT Files (*.srt);;All Files (*)", options=options)
        if file_path:
            self.inputFileEdit.setText(file_path)
    
    def select_output_path(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "SRT Files (*.srt);;All Files (*)", options=options)
        if file_path:
            self.outputFileEdit.setText(file_path)

    def start_translation(self):
        input_file = self.inputFileEdit.text()
        output_file = self.outputFileEdit.text()
        dest_lang = self.destLangCombo.currentText()

        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select an input file.")
            return
        
        if not output_file:
            QMessageBox.warning(self, "Warning", "Please select an output file path.")
            return

        dest_lang_code = 'en' if dest_lang == 'English' else 'fa' if dest_lang == 'Farsi' else 'de'
        
        try:
            lines = self.read_srt(input_file)
            translated_lines = self.translate_subtitles(lines, dest_lang_code)
            self.save_srt(output_file, translated_lines)
            QMessageBox.information(self, "Success", f"Translation completed successfully and saved to {output_file}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def read_srt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return lines

    def detect_language(self, text):
        try:
            lang = detect(text)
            return lang
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Language detection failed: {str(e)}")
            return 'en'  # پیش‌فرض به انگلیسی برمی‌گردد در صورت بروز خطا

    def translate_subtitles(self, lines, dest_lang):
        translator = Translator()
        translated_lines = []
        src_lang = self.detect_language(' '.join([line for line in lines if not line.strip().isdigit() and '-->' not in line]))

        max_retries = 3
        retry_delay = 5  # ثانیه
        request_timeout = 10  # ثانیه

        total_lines = len(lines)
        self.progressBar.setMaximum(total_lines)

        for idx, line in enumerate(lines):
            if line.strip().isdigit() or '-->' in line or line.strip() == '':
                translated_lines.append(line)
            else:
                success = False
                for attempt in range(max_retries):
                    try:
                        start_time = time.time()
                        translation = translator.translate(line, src=src_lang, dest=dest_lang, timeout=request_timeout)
                        duration = time.time() - start_time
                        logging.info(f"Translation successful in {duration:.2f} seconds for line: {line.strip()}")
                        translated_lines.append(translation.text + '\n')
                        success = True
                        break
                    except Exception as e:
                        logging.error(f"Attempt {attempt+1} failed: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                        else:
                            translated_lines.append(line)
                            logging.error(f"Final attempt failed for line: {line.strip()}")
            # Update progress bar
            self.progressBar.setValue(idx + 1)
            self.progressLabel.setText(f'Processing: {idx + 1}/{total_lines} lines')
            QApplication.processEvents()
        return translated_lines

    def save_srt(self, file_path, lines):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SubtitleTranslator()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())
