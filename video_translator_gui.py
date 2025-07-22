#!/usr/bin/env python3
"""
Video Translator GUI Application

A modern PyQt6-based graphical user interface for the video translation tool.
Includes all features from the command-line version with an intuitive interface.
"""

import sys
import os
import threading
from pathlib import Path
from typing import Optional
import traceback

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTextEdit, QProgressBar, QFileDialog, QGroupBox, QCheckBox,
    QTabWidget, QGridLayout, QFrame, QScrollArea, QSplitter,
    QMessageBox, QSystemTrayIcon, QMenu, QSlider, QSpacerItem, QSizePolicy,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSettings, QSize, QUrl
)
from PyQt6.QtGui import (
    QFont, QPixmap, QIcon, QAction, QDesktopServices, QDragEnterEvent, 
    QDropEvent, QPalette, QColor, QLinearGradient, QBrush
)

from main import VideoTranslator


class WorkerThread(QThread):
    """Worker thread for video translation to prevent UI freezing."""
    
    progress_update = pyqtSignal(str)  # Status message
    progress_percentage = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(str)  # Output file path
    error = pyqtSignal(str)  # Error message
    
    def __init__(self, translator_params):
        super().__init__()
        self.translator_params = translator_params
        self.translator = None
        
    def run(self):
        """Execute the translation in a separate thread."""
        try:
            self.progress_update.emit("Initializing...")
            self.progress_percentage.emit(5)
            
            api_key = self.translator_params.get('api_key')
            elevenlabs_api_key = self.translator_params.get('elevenlabs_api_key')
            tts_provider = self.translator_params.get('tts_provider')
            
            def progress_callback(message):
                self.progress_update.emit(message)
                # Approximate percentage based on step
                steps = ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5', 'Step 6', 'Generating subtitles', 'Step 7']
                for i, step in enumerate(steps):
                    if step in message:
                        self.progress_percentage.emit(10 + (i * 12))
                        break
            
            self.translator = VideoTranslator(
                api_key=api_key,
                elevenlabs_api_key=elevenlabs_api_key if tts_provider == 'elevenlabs' else None,
                progress_callback=progress_callback
            )
            
            del self.translator_params['api_key']
            if 'elevenlabs_api_key' in self.translator_params and tts_provider != 'elevenlabs':
                del self.translator_params['elevenlabs_api_key']
            
            output_path = self.translator.translate_video(**self.translator_params)
            
            self.progress_percentage.emit(100)
            self.finished.emit(output_path)
        except Exception as e:
            self.error.emit(str(e))


class ModernButton(QPushButton):
    """Custom modern-styled button."""
    
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.primary = primary
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_style()
        
    def apply_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #5CBF60, stop:1 #4CAF50);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #45a049, stop:1 #3d8b40);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #f8f9fa, stop:1 #e9ecef);
                    color: black;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #e9ecef, stop:1 #dee2e6);
                    border: 1px solid #adb5bd;
                    color: black;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #dee2e6, stop:1 #ced4da);
                    color: black;
                }
                QPushButton:disabled {
                    background: #f8f9fa;
                    color: #999999;
                    border: 1px solid #dee2e6;
                }
            """)


class VideoTranslatorGUI(QMainWindow):
    """Main GUI application for video translation."""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('VideoTranslator', 'Settings')
        self.worker_thread = None
        self.current_input_source = None
        
        self.init_ui()
        self.load_settings()
        self.setup_drag_drop()
        
        # Connect radio buttons to update voices
        self.openai_radio.toggled.connect(self.update_voice_list)
        self.elevenlabs_radio.toggled.connect(self.update_voice_list)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🎬 Video Translator - AI-Powered Translation")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Apply modern styling
        self.apply_modern_style()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Input and Settings
        left_panel = self.create_left_panel()
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(left_panel)
        splitter.addWidget(left_scroll)
        
        # Right panel - Progress and Output
        right_panel = self.create_right_panel()
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(right_panel)
        splitter.addWidget(right_scroll)
        
        # Set splitter proportions
        splitter.setSizes([500, 700])
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready to translate videos...")
        
        # Menu bar
        self.create_menu_bar()
        
    def apply_modern_style(self):
        """Apply modern styling to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #f8f9fa, stop:1 #e9ecef);
                color: black;
            }
            QWidget {
                color: black;
            }
            QLabel {
                color: black;
                font-weight: normal;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
                background: white;
                color: black;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 14px;
                background: white;
                color: black;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #4CAF50;
                color: black;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
            QComboBox::drop-down {
                border: none;
                color: black;
            }
            QComboBox::down-arrow {
                color: black;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: black;
                selection-background-color: #e3f2fd;
                selection-color: black;
            }
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                color: black;
            }
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background: #f8f9fa;
                color: black;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 6px;
            }
            QCheckBox {
                font-size: 14px;
                spacing: 8px;
                color: black;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #4CAF50;
                border: 2px solid #4CAF50;
            }
            QSlider::groove:horizontal {
                border: 1px solid #dee2e6;
                height: 8px;
                background: #f8f9fa;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #45a049;
                width: 18px;
                border-radius: 9px;
                margin: -5px 0px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 4px;
            }
            QMenuBar {
                background: #f8f9fa;
                color: black;
                border-bottom: 1px solid #dee2e6;
            }
            QMenuBar::item {
                background: transparent;
                color: black;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background: #e9ecef;
                color: black;
            }
            QMenu {
                background: white;
                color: black;
                border: 1px solid #dee2e6;
            }
            QMenu::item {
                background: transparent;
                color: black;
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background: #e3f2fd;
                color: black;
            }
            QStatusBar {
                background: #f8f9fa;
                color: black;
                border-top: 1px solid #dee2e6;
            }
            QScrollBar:vertical {
                background: #f8f9fa;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #dee2e6;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #adb5bd;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
            }
        """)
        
    def create_left_panel(self):
        """Create the left panel with input controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Input Source Group
        input_group = QGroupBox("📥 Input Source")
        input_layout = QVBoxLayout(input_group)
        
        # Input field with browse button
        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter YouTube URL or select video file...")
        self.input_field.textChanged.connect(self.on_input_changed)
        self.input_field.setToolTip("Enter a YouTube URL or local video path")
        
        self.browse_button = ModernButton("📁 Browse")
        self.browse_button.clicked.connect(self.browse_input_file)
        
        input_row.addWidget(self.input_field, 4)
        input_row.addWidget(self.browse_button, 1)
        input_layout.addLayout(input_row)
        
        # Drag & Drop label
        drag_label = QLabel("💡 Tip: You can drag & drop video files here")
        drag_label.setStyleSheet("color: black; font-style: italic; padding: 5px;")
        drag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(drag_label)
        
        layout.addWidget(input_group)
        
        # Output Settings Group
        output_group = QGroupBox("📤 Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        # Output directory
        output_row = QHBoxLayout()
        self.output_field = QLineEdit()
        self.output_field.setPlaceholderText("Auto-generated filename (optional)")
        
        self.output_browse_button = ModernButton("📁")
        self.output_browse_button.clicked.connect(self.browse_output_file)
        
        output_row.addWidget(QLabel("Output:"))
        output_row.addWidget(self.output_field, 4)
        output_row.addWidget(self.output_browse_button)
        output_layout.addLayout(output_row)
        
        # Language selection
        lang_row = QHBoxLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Hindi", "Spanish", "French", "German", "Italian", "Portuguese",
            "Russian", "Japanese", "Korean", "Chinese", "Arabic", "Turkish"
        ])
        self.language_combo.setToolTip("Select target translation language")
        
        lang_row.addWidget(QLabel("Language:"))
        lang_row.addWidget(self.language_combo)
        output_layout.addLayout(lang_row)
        
        # Voice selection
        voice_row = QHBoxLayout()
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        ])
        self.voice_combo.setCurrentText("shimmer")
        self.voice_combo.setToolTip("Select voice for text-to-speech")
        
        voice_row.addWidget(QLabel("Voice:"))
        voice_row.addWidget(self.voice_combo)
        output_layout.addLayout(voice_row)

        # TTS Provider selection
        tts_row = QHBoxLayout()
        self.tts_group = QButtonGroup()
        self.openai_radio = QRadioButton("OpenAI")
        self.elevenlabs_radio = QRadioButton("ElevenLabs")
        self.tts_group.addButton(self.openai_radio)
        self.tts_group.addButton(self.elevenlabs_radio)
        self.openai_radio.setChecked(True)
        tts_row.addWidget(QLabel("TTS Provider:"))
        tts_row.addWidget(self.openai_radio)
        tts_row.addWidget(self.elevenlabs_radio)
        output_layout.addLayout(tts_row)
        
        # Add subtitle checkbox in Output Settings
        subtitle_check = QCheckBox("Generate subtitles")
        output_layout.addWidget(subtitle_check)
        self.subtitle_check = subtitle_check
        
        layout.addWidget(output_group)
        
        # Audio Mixing Group
        audio_group = QGroupBox("🎵 Audio Mixing")
        audio_layout = QVBoxLayout(audio_group)
        
        # Mix with background checkbox
        self.mix_background_check = QCheckBox("Mix with original background music")
        self.mix_background_check.setChecked(False)
        self.mix_background_check.toggled.connect(self.on_mix_background_toggled)
        self.mix_background_check.setToolTip("Mix translated audio with original background")
        
        # Volume controls
        self.volume_widget = QWidget()
        volume_layout = QGridLayout(self.volume_widget)
        
        # Background volume
        volume_layout.addWidget(QLabel("Background Volume:"), 0, 0)
        self.background_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.background_volume_slider.setRange(0, 100)
        self.background_volume_slider.setValue(30)
        self.background_volume_slider.valueChanged.connect(self.update_background_volume_label)
        
        self.background_volume_label = QLabel("30%")
        self.background_volume_label.setMinimumWidth(40)
        
        volume_layout.addWidget(self.background_volume_slider, 0, 1)
        volume_layout.addWidget(self.background_volume_label, 0, 2)
        
        # Speech volume
        volume_layout.addWidget(QLabel("Speech Volume:"), 1, 0)
        self.speech_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.speech_volume_slider.setRange(0, 200)
        self.speech_volume_slider.setValue(100)
        self.speech_volume_slider.valueChanged.connect(self.update_speech_volume_label)
        
        self.speech_volume_label = QLabel("100%")
        self.speech_volume_label.setMinimumWidth(40)
        
        volume_layout.addWidget(self.speech_volume_slider, 1, 1)
        volume_layout.addWidget(self.speech_volume_label, 1, 2)
        
        audio_layout.addWidget(self.volume_widget)
        self.volume_widget.setEnabled(False)
        
        layout.addWidget(audio_group)
        
        # Advanced Settings Group
        advanced_group = QGroupBox("⚙️ Advanced Settings")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # API Key
        api_row = QHBoxLayout()
        self.api_key_field = QLineEdit()
        self.api_key_field.setPlaceholderText("OpenAI API Key (optional if set in environment)")
        self.api_key_field.setEchoMode(QLineEdit.EchoMode.Password)
        
        api_row.addWidget(QLabel("OpenAI Key:"))
        api_row.addWidget(self.api_key_field)
        advanced_layout.addLayout(api_row)

        # ElevenLabs API Key
        el_api_row = QHBoxLayout()
        self.elevenlabs_key_field = QLineEdit()
        self.elevenlabs_key_field.setPlaceholderText("ElevenLabs API Key (required for ElevenLabs)")
        self.elevenlabs_key_field.setEchoMode(QLineEdit.EchoMode.Password)
        
        el_api_row.addWidget(QLabel("ElevenLabs Key:"))
        el_api_row.addWidget(self.elevenlabs_key_field)
        advanced_layout.addLayout(el_api_row)
        
        # Keep temp files
        self.keep_temp_check = QCheckBox("Keep temporary files for debugging")
        advanced_layout.addWidget(self.keep_temp_check)
        
        # YouTube download directory
        youtube_row = QHBoxLayout()
        self.youtube_dir_field = QLineEdit()
        self.youtube_dir_field.setPlaceholderText("YouTube download directory (optional)")
        
        self.youtube_dir_browse = ModernButton("📁")
        self.youtube_dir_browse.clicked.connect(self.browse_youtube_dir)
        
        youtube_row.addWidget(QLabel("YouTube Dir:"))
        youtube_row.addWidget(self.youtube_dir_field)
        youtube_row.addWidget(self.youtube_dir_browse)
        advanced_layout.addLayout(youtube_row)
        
        layout.addWidget(advanced_group)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Start Translation Button
        self.translate_button = ModernButton("🚀 Start Translation", primary=True)
        self.translate_button.clicked.connect(self.start_translation)
        layout.addWidget(self.translate_button)
        
        return panel
        
    def create_right_panel(self):
        """Create the right panel with progress and output."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Progress Group
        progress_group = QGroupBox("📊 Translation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar { height: 25px; }")
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start translation...")
        self.status_label.setStyleSheet("font-size: 14px; color: black; padding: 5px;")
        progress_layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = ModernButton("⏹️ Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_translation)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        
        progress_layout.addLayout(button_layout)
        
        layout.addWidget(progress_group)
        
        # Output Group
        output_group = QGroupBox("📝 Translation Log")
        output_layout = QVBoxLayout(output_group)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        output_layout.addWidget(self.log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        self.clear_log_button = ModernButton("🗑️ Clear Log")
        self.clear_log_button.clicked.connect(self.clear_log)
        
        self.save_log_button = ModernButton("💾 Save Log")
        self.save_log_button.clicked.connect(self.save_log)
        
        log_controls.addWidget(self.clear_log_button)
        log_controls.addWidget(self.save_log_button)
        log_controls.addStretch()
        
        output_layout.addLayout(log_controls)
        
        layout.addWidget(output_group)
        
        # Results Group
        results_group = QGroupBox("🎉 Results")
        results_layout = QVBoxLayout(results_group)
        
        # Output file info
        self.output_info_label = QLabel("No output file yet...")
        self.output_info_label.setStyleSheet("font-size: 14px; color: black; padding: 10px;")
        results_layout.addWidget(self.output_info_label)
        
        # Result buttons
        result_buttons = QHBoxLayout()
        
        self.open_output_button = ModernButton("📁 Open Output Folder")
        self.open_output_button.setEnabled(False)
        self.open_output_button.clicked.connect(self.open_output_folder)
        
        self.play_output_button = ModernButton("▶️ Play Video")
        self.play_output_button.setEnabled(False)
        self.play_output_button.clicked.connect(self.play_output_video)
        
        result_buttons.addWidget(self.open_output_button)
        result_buttons.addWidget(self.play_output_button)
        result_buttons.addStretch()
        
        results_layout.addLayout(result_buttons)
        
        layout.addWidget(results_group)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        return panel
        
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open Video File', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.browse_input_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality."""
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.flv', '.wmv']
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    self.input_field.setText(file)
                    self.current_input_source = file
                    self.log_message(f"📁 Dropped video file: {file}")
                    break
                    
    def on_input_changed(self):
        """Handle input field changes."""
        text = self.input_field.text().strip()
        self.current_input_source = text
        
        # Enable/disable translate button
        self.translate_button.setEnabled(bool(text))
        
        # Update status
        if text:
            if self.is_youtube_url(text):
                self.status_label.setText("📺 YouTube URL detected")
            else:
                self.status_label.setText("📁 Local file selected")
        else:
            self.status_label.setText("Ready to start translation...")
            
    def is_youtube_url(self, url: str) -> bool:
        """Check if the input is a YouTube URL."""
        youtube_patterns = [
            'youtube.com/watch', 'youtu.be/', 'youtube.com/embed/',
            'youtube.com/shorts/', 'm.youtube.com/watch'
        ]
        return any(pattern in url.lower() for pattern in youtube_patterns)
        
    def on_mix_background_toggled(self, checked):
        """Handle mix background checkbox toggle."""
        self.volume_widget.setEnabled(checked)
        
    def update_background_volume_label(self, value):
        """Update background volume label."""
        self.background_volume_label.setText(f"{value}%")
        
    def update_speech_volume_label(self, value):
        """Update speech volume label."""
        self.speech_volume_label.setText(f"{value}%")
        
    def browse_input_file(self):
        """Browse for input video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.webm *.m4v *.flv *.wmv);;All Files (*)"
        )
        if file_path:
            self.input_field.setText(file_path)
            self.current_input_source = file_path
            
    def browse_output_file(self):
        """Browse for output video file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Video As", "",
            "Video Files (*.mp4);;All Files (*)"
        )
        if file_path:
            self.output_field.setText(file_path)
            
    def browse_youtube_dir(self):
        """Browse for YouTube download directory."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select YouTube Download Directory")
        if dir_path:
            self.youtube_dir_field.setText(dir_path)
            
    def start_translation(self):
        """Start the video translation process."""
        if not self.current_input_source:
            QMessageBox.warning(self, "Warning", "Please select a video file or enter a YouTube URL.")
            return

        if self.elevenlabs_radio.isChecked():
            tts_provider = "elevenlabs"
            if not self.elevenlabs_key_field.text().strip():
                QMessageBox.warning(self, "Warning", "ElevenLabs API key is required.")
                return
        else:
            tts_provider = "openai"

        # Prepare parameters
        params = {
            'input_source': self.current_input_source,
            'output_video': self.output_field.text().strip() or None,
            'target_language': self.language_combo.currentText(),
            'voice': self.voice_combo.currentText(),
            'keep_temp_files': self.keep_temp_check.isChecked(),
            'youtube_download_dir': self.youtube_dir_field.text().strip() or None,
            'mix_with_background': self.mix_background_check.isChecked(),
            'background_volume': self.background_volume_slider.value() / 100.0,
            'speech_volume': self.speech_volume_slider.value() / 100.0,
            'api_key': self.api_key_field.text().strip() or None,
            'tts_provider': tts_provider,
            'elevenlabs_api_key': self.elevenlabs_key_field.text().strip() or None,
            'generate_subtitles': self.subtitle_check.isChecked()
        }
        
        # Disable controls
        self.translate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.clear_log()
        
        # Start worker thread
        self.worker_thread = WorkerThread(params)
        self.worker_thread.progress_update.connect(self.update_progress_text)
        self.worker_thread.progress_percentage.connect(self.update_progress_bar)
        self.worker_thread.finished.connect(self.on_translation_finished)
        self.worker_thread.error.connect(self.on_translation_error)
        self.worker_thread.start()
        
        self.log_message("🚀 Translation started...")
        
    def cancel_translation(self):
        """Cancel the current translation."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            
        self.translate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Translation cancelled.")
        self.log_message("⏹️ Translation cancelled by user.")
        
    def update_progress_text(self, message):
        """Update progress text."""
        self.status_label.setText(message)
        self.log_message(message)
        
    def update_progress_bar(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
        
    def on_translation_finished(self, output_path):
        """Handle translation completion."""
        self.translate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ Translation completed successfully!")
        
        # Update output info
        self.output_info_label.setText(f"📁 Output: {output_path}")
        self.open_output_button.setEnabled(True)
        self.play_output_button.setEnabled(True)
        self.current_output_path = output_path
        
        self.log_message(f"🎉 Translation completed! Output saved to: {output_path}")
        
        # Show completion message
        QMessageBox.information(self, "Success", f"Translation completed successfully!\n\nOutput saved to:\n{output_path}")
        
    def on_translation_error(self, error_msg):
        """Handle translation error."""
        self.translate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("❌ Translation failed.")
        
        self.log_message(f"❌ Error: {error_msg}")
        
        # Show error message
        QMessageBox.critical(self, "Error", f"Translation failed:\n\n{error_msg}")
        
    def open_output_folder(self):
        """Open the output folder."""
        if hasattr(self, 'current_output_path') and self.current_output_path:
            folder_path = Path(self.current_output_path).parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
            
    def play_output_video(self):
        """Play the output video."""
        if hasattr(self, 'current_output_path') and self.current_output_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_output_path))
            
    def log_message(self, message):
        """Add a message to the log."""
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()
        
    def clear_log(self):
        """Clear the log."""
        self.log_text.clear()
        
    def save_log(self):
        """Save the log to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Log", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            self.log_message(f"📄 Log saved to: {file_path}")
            
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
            "🎬 Video Translator\n\n"
            "AI-powered video translation tool using OpenAI APIs.\n\n"
            "Features:\n"
            "• YouTube video support\n"
            "• Multiple languages\n"
            "• Background music preservation\n"
            "• Modern GUI interface\n\n"
            "Built with PyQt6 and OpenAI APIs.")
        
    def load_settings(self):
        """Load settings from QSettings."""
        # Load last used values
        self.language_combo.setCurrentText(self.settings.value('language', 'Hindi'))
        self.voice_combo.setCurrentText(self.settings.value('voice', 'shimmer'))
        self.mix_background_check.setChecked(self.settings.value('mix_background', False, type=bool))
        self.background_volume_slider.setValue(self.settings.value('background_volume', 30, type=int))
        self.speech_volume_slider.setValue(self.settings.value('speech_volume', 100, type=int))
        self.keep_temp_check.setChecked(self.settings.value('keep_temp', False, type=bool))
        
        # Update labels
        self.update_background_volume_label(self.background_volume_slider.value())
        self.update_speech_volume_label(self.speech_volume_slider.value())
        self.on_mix_background_toggled(self.mix_background_check.isChecked())
        
        # Load API keys
        self.api_key_field.setText(self.settings.value('openai_api_key', ''))
        self.elevenlabs_key_field.setText(self.settings.value('elevenlabs_api_key', ''))
        
    def save_settings(self):
        """Save settings to QSettings."""
        self.settings.setValue('language', self.language_combo.currentText())
        self.settings.setValue('voice', self.voice_combo.currentText())
        self.settings.setValue('mix_background', self.mix_background_check.isChecked())
        self.settings.setValue('background_volume', self.background_volume_slider.value())
        self.settings.setValue('speech_volume', self.speech_volume_slider.value())
        self.settings.setValue('keep_temp', self.keep_temp_check.isChecked())
        
        # Save API keys
        self.settings.setValue('openai_api_key', self.api_key_field.text())
        self.settings.setValue('elevenlabs_api_key', self.elevenlabs_key_field.text())
        
    def closeEvent(self, event):
        """Handle close event."""
        # Save settings
        self.save_settings()
        
        # Cancel running translation
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(self, "Confirm Exit", 
                "Translation is in progress. Do you want to cancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.worker_thread.terminate()
                self.worker_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def update_voice_list(self):
        if self.openai_radio.isChecked():
            voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            default_voice = "shimmer"
        else:
            voices = ["Rachel", "Adam", "Charlie", "Daniel", "Bella", "Nicole"]
            default_voice = "Rachel"
        
        self.voice_combo.clear()
        self.voice_combo.addItems(voices)
        self.voice_combo.setCurrentText(default_voice)


def main():
    """Main function to run the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Video Translator")
    app.setOrganizationName("VideoTranslator")
    
    # Set application icon (if available)
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass
    
    # Set light theme
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(248, 249, 250))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(248, 249, 250))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(248, 249, 250))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # Create and show main window
    window = VideoTranslatorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 