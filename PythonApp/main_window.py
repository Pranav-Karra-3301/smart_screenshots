from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import QThread
from sidebar import Sidebar
from search_page import SearchPage
from preferences_page import PreferencesPage
from api_key_page import APIKeyPage
from directories_page import DirectoriesPage
from scripts.rename_files_base64 import FileProcessor

class ProcessingThread(QThread):
    def __init__(self, file_processor, directory):
        super().__init__()
        self.file_processor = file_processor
        self.directory = directory

    def run(self):
        self.file_processor.process_and_rename(self.directory)

class MainWindow(QMainWindow):
    def __init__(self, index_manager):
        super().__init__()
        self.index_manager = index_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Organizer")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        self.search_page = SearchPage(self.index_manager)
        self.preferences_page = PreferencesPage()
        self.api_key_page = APIKeyPage()
        self.directories_page = DirectoriesPage(self.index_manager)

        self.content_stack.addWidget(self.search_page)
        self.content_stack.addWidget(self.directories_page)
        self.content_stack.addWidget(self.preferences_page)
        self.content_stack.addWidget(self.api_key_page)

        layout.addWidget(self.content_stack)

        # Connect sidebar navigation to content pages
        self.sidebar.currentRowChanged.connect(self.display_page)
        self.directories_page.process_directory_signal.connect(self.process_directory)

    def display_page(self, index):
        self.content_stack.setCurrentIndex(index)

    def process_directory(self, directory):
        self.directories_page.start_processing(directory)
        
        self.file_processor = FileProcessor()
        self.file_processor.progress_update.connect(self.directories_page.update_progress)
        self.processing_thread = ProcessingThread(self.file_processor, directory)
        self.processing_thread.start()