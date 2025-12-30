"""
ui_utils.py - Gestionnaire d'interface utilisateur amélioré
Version refactorisée pour meilleure qualité de code et performance
"""

import os
import json
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any, Callable

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout,
    QPushButton, QMessageBox, QWidget, QListWidget, QTabWidget,
    QGroupBox, QApplication, QFrame, QSpinBox, QCheckBox,
    QLineEdit, QTabBar, QSizePolicy, QGraphicsDropShadowEffect,
    QTableWidget, QHeaderView, QComboBox
)
from PyQt6.QtGui import (
    QIcon, QColor, QPixmap, QMouseEvent
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, pyqtSignal, QObject
)
import PyQt6

# Configuration du chemin racine
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from config import Settings
    from utils.validation_utils import ValidationUtils
except ImportError as e:
    raise ImportError(f"❌ Erreur d'importation: {e}")


class CustomTextDialog(QDialog):
    """Dialogue personnalisé pour la modification de texte"""
    
    def __init__(self, parent=None, texte_initial=""):
        super().__init__(parent)
        self.setWindowTitle("Update Text")
        self.setMinimumSize(500, 350)
        self._setup_ui(texte_initial)
        self._apply_styles()
    
    def _setup_ui(self, texte_initial: str):
        """Configure l'interface du dialogue"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Label d'instruction
        label = QLabel("📝 Please enter your text below:")
        layout.addWidget(label)
        
        # Zone de texte
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(texte_initial)
        layout.addWidget(self.text_edit)
        
        # Boutons Annuler / Enregistrer
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.btn_ok = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _apply_styles(self):
        """Applique les styles CSS au dialogue"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                font-family: "Times", "Times New Roman", serif;
                font-size: 14px;
                color: #2d2d2d;
                font-weight: 500;
                margin-bottom: 10px;
            }
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 10px;
                font-family: "Times", "Times New Roman", serif;
                background-color: #fafafa;
                font-size: 12pt;
                padding: 5px;
            }
            QTextEdit:focus {
                border: 2px solid #0078d7;
                background-color: #ffffff;
            }
            QPushButton {
                font-family: "Times", "Times New Roman", serif;
                padding: 8px 16px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton#btn_ok {
                background-color: #0078d7;
                border: none;
                color: white;
            }
            QPushButton#btn_ok:hover {
                background-color: #005a9e;
            }
            QPushButton#btn_cancel {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                color: #333333;
            }
            QPushButton#btn_cancel:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # IDs pour styles séparés
        self.btn_ok.setObjectName("btn_ok")
        self.btn_cancel.setObjectName("btn_cancel")
    
    def get_text(self) -> str:
        """Retourne le texte saisi"""
        return self.text_edit.toPlainText().strip()


class UIStyles:
    """Classe utilitaire pour les styles CSS réutilisables"""
    
    # Couleurs principales
    PRIMARY_COLOR = "#669bbc"
    SECONDARY_COLOR = "#ffffff"
    ERROR_COLOR = "#d32f2f"
    WARNING_COLOR = "#ed6c02"
    SUCCESS_COLOR = "#2e7d32"
    INFO_COLOR = "#0288d1"
    
    # Styles réutilisables
    @staticmethod
    def get_label_style(color: str = "#669bbc", size: int = 16) -> str:
        return f"""
            QLabel {{
                color: {color};
                font-size: {size}px;
                border: none;
                border-radius: 4px;
                text-align: center;
                background-color: transparent;
                font-family: "Times", "Times New Roman", serif;
                margin-left: 10px;
            }}
        """
    
    @staticmethod
    def get_spinbox_style(arrow_path: str, border_color: str = "#669bbc") -> str:
        return f"""
            QSpinBox {{
                padding: 2px; 
                border: 1px solid {border_color}; 
                color: {"white" if border_color == "white" else "black"};
            }}
            QSpinBox::down-button {{
                image: url("{arrow_path}");
                width: 13px;
                height: 13px;
                padding: 2px;  
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }}
            QSpinBox::up-button {{
                image: url("{arrow_path}");
                width: 13px;
                height: 13px;
                padding: 2px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }}
        """
    
    @staticmethod
    def get_combobox_style(arrow_path: str) -> str:
        return f"""
            QComboBox::down-arrow {{
                image: url("{arrow_path}");
                width: 13px;
                height: 13px;
                border: none;
                background-color: white;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
                outline: none;
            }}
            
            QComboBox QAbstractItemView {{
                min-width: 90px; 
                border: none; 
                background: white;
                selection-background-color: #669bbc;
                selection-color: white;
                padding: 3px; 
                margin: 0px;  
                alignment: center; 
            }}
            QComboBox {{
                padding-left: 10px; 
                font-size: 12px;
                font-family: "Times", "Times New Roman", serif;
                border: 1px solid #669bbc; 
                outline: none; 
            }}
            QComboBox QAbstractItemView::item {{
                padding: 5px; 
                font-size: 12px;
                color: #333;
                border: none; 
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: #669bbc;
                color: white;
                border-radius: 3px;
            }}
            QComboBox:focus {{
                border: 1px solid #669bbc; 
            }}
        """
    
    @staticmethod
    def get_messagebox_style(message_type: str) -> Dict[str, str]:
        """Retourne les styles pour un QMessageBox selon le type"""
        colors = {
            "critical": {
                "accent": "#d32f2f",
                "start": "#d32f2f",
                "end": "#b71c1c",
                "bg": "#ffebee"
            },
            "warning": {
                "accent": "#ed6c02",
                "start": "#ed6c02",
                "end": "#e65100",
                "bg": "#fff3e0"
            },
            "info": {
                "accent": "#0288d1",
                "start": "#0288d1",
                "end": "#01579b",
                "bg": "#e1f5fe"
            },
            "success": {
                "accent": "#2e7d32",
                "start": "#2e7d32",
                "end": "#1b5e20",
                "bg": "#e8f5e9"
            }
        }
        
        c = colors.get(message_type, colors["info"])
        
        return {
            "colors": c,
            "stylesheet": f"""
                QMessageBox {{
                    background-color: {c['bg']};
                    color: #263238;
                    font-family: 'Segoe UI', 'Roboto', sans-serif;
                    font-size: 14px;
                    padding: 20px;
                    min-width: 480px;
                    border-radius: 12px;
                }}
                QMessageBox QLabel#qt_msgbox_label {{
                    padding: 15px;
                    border-radius: 10px;
                    background: {c['bg']};
                }}
                QMessageBox QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {c['start']}, stop:1 {c['end']});
                    color: #fff;
                    font-weight: 600;
                    border-radius: 8px;
                    padding: 10px 25px;
                    min-width: 100px;
                }}
                QMessageBox QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {UIManager.lighten_color(c['start'], 12)}, stop:1 {UIManager.lighten_color(c['end'], 12)});
                }}
                QMessageBox QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {UIManager.darken_color(c['start'], 12)}, stop:1 {UIManager.darken_color(c['end'], 12)});
                    padding: 11px 26px 9px 26px;
                }}
            """
        }


class UIManager:
    """Gestionnaire principal de l'interface utilisateur"""
    
    @staticmethod
    def darken_color(hex_color: str, percent: int) -> str:
        """Assombrit une couleur HEX"""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            factor = 1 - percent / 100
            r = max(0, min(255, int(r * factor)))
            g = max(0, min(255, int(g * factor)))
            b = max(0, min(255, int(b * factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color
    
    @staticmethod
    def lighten_color(hex_color: str, percent: int) -> str:
        """Éclaircit une couleur HEX"""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            r = min(255, int(r + (255 - r) * percent / 100))
            g = min(255, int(g + (255 - g) * percent / 100))
            b = min(255, int(b + (255 - b) * percent / 100))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color
    
    @staticmethod
    def set_custom_colored_tab(tab_widget: QTabWidget, index: int, 
                               completed_count: int, not_completed_count: int):
        """
        Personnalise un onglet pour afficher le nombre d'emails complétés et non complétés
        """
        html_text = (
            f'<div style="text-align:center;margin:0;padding:0;">'
            f'<span style="font-family:\'Segoe UI\', sans-serif; font-size:14px;">Result ('
            f'<span style="color:#008000;">{completed_count} completed</span> / '
            f'<span style="color:#d90429;">{not_completed_count} not completed</span>)</span>'
            f'</div>'
        )
        
        # Supprimer le texte par défaut
        tab_widget.setTabText(index, "")
        
        # Créer le label avec HTML
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(html_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Wrapper pour centrer le label
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(label)
        
        # Supprimer les boutons existants
        tab_bar = tab_widget.tabBar()
        tab_bar.setTabButton(index, QTabBar.ButtonPosition.LeftSide, None)
        tab_bar.setTabButton(index, QTabBar.ButtonPosition.RightSide, None)
        
        # Ajouter le wrapper comme contenu de l'onglet
        tab_bar.setTabButton(index, QTabBar.ButtonPosition.LeftSide, wrapper)
    
    @staticmethod
    def read_result_update_list(window: QWidget):
        """
        Lit les résultats d'emails et met à jour l'interface
        """
        if not ValidationUtils.path_exists(Settings.RESULT_FILE_PATH):
            UIManager.show_critical_message(
                window,
                "Information",
                "No emails have been processed yet.\nPlease check the filters or new data.",
                message_type="info"
            )
            return
        
        errors_dict = defaultdict(list)
        all_emails = []
        
        try:
            # Lire et parser le fichier de résultats
            with open(Settings.RESULT_FILE_PATH, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                UIManager.show_critical_message(
                    window, "Warning", "No results available.", message_type="warning"
                )
                return
            
            completed_count = 0
            not_completed_count = 0
            
            # Traiter chaque ligne
            for line in lines:
                parts = line.split(":")
                if len(parts) != 4:
                    continue
                
                _, _, email, status = [p.strip() for p in parts]
                all_emails.append(email)
                errors_dict[status].append(email)
                
                if status == "completed":
                    completed_count += 1
                else:
                    not_completed_count += 1
            
            errors_dict["all"] = all_emails
            
            # Mettre à jour l'onglet principal
            interface_tab_widget = window.findChild(QTabWidget, "interface_2")
            if interface_tab_widget:
                for i in range(interface_tab_widget.count()):
                    if interface_tab_widget.tabText(i).startswith("Result"):
                        UIManager.set_custom_colored_tab(
                            interface_tab_widget, i, completed_count, not_completed_count
                        )
                        break
            
            # Mettre à jour les onglets secondaires
            result_tab_widget = window.findChild(QTabWidget, "tabWidgetResult")
            if not result_tab_widget:
                return
            
            for status in Settings.STATUS_LIST:
                tab_widget = result_tab_widget.findChild(QWidget, status)
                if not tab_widget:
                    continue
                
                list_widgets = tab_widget.findChildren(QListWidget)
                if not list_widgets:
                    continue
                
                list_widget = list_widgets[0]
                list_widget.clear()
                emails = errors_dict.get(status, [])
                
                if emails:
                    list_widget.addItems(emails)
                    list_widget.scrollToBottom()
                    
                    # Supprimer le message "no data" si présent
                    message_label = tab_widget.findChild(QLabel, "no_data_message")
                    if message_label:
                        message_label.deleteLater()
                else:
                    list_widget.addItem("⚠ No email data available for this category currently.")
                    list_widget.show()
        
        except Exception as e:
            UIManager.show_critical_message(
                window, "Error", f"An error occurred while displaying results: {e}"
            )
    
    @staticmethod
    def show_critical_message(parent: QWidget, title: str, message: str, 
                              message_type: str = "critical") -> int:
        """
        Affiche un message stylé selon le type
        """
        dialog = QMessageBox(parent)
        
        # Obtenir les styles pour le type de message
        styles = UIStyles.get_messagebox_style(message_type)
        colors = styles["colors"]
        
        # Définir l'icône appropriée
        icon_map = {
            "critical": QMessageBox.Icon.Critical,
            "warning": QMessageBox.Icon.Warning,
            "info": QMessageBox.Icon.Information,
            "success": QMessageBox.Icon.Information
        }
        dialog.setIcon(icon_map.get(message_type, QMessageBox.Icon.Information))
        
        # Définir le titre et le message
        dialog.setWindowTitle(title)
        dialog.setText(
            f"<h2 style='margin:0; font-weight:700; color:{colors['accent']};'>{title}</h2>"
            f"<p style='margin:0px; color:#37474f; line-height:1.5;'>{message}</p>"
        )
        
        # Ajouter une ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 12)
        dialog.setGraphicsEffect(shadow)
        
        # Appliquer les styles
        dialog.setStyleSheet(styles["stylesheet"])
        
        # Centrer la boîte de dialogue
        if parent:
            dialog.move(parent.frameGeometry().center() - dialog.rect().center())
        
        return dialog.exec()
    
    @staticmethod
    def update_logs_display(log_entry: str, log_layout: QVBoxLayout):
        """
        Ajoute une nouvelle ligne de log dans la zone de log
        """
        log_label = QLabel(log_entry)
        log_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                background-color: transparent;
                font-family: "Times", "Times New Roman", serif;
                padding: 2px;
            }
        """)
        log_layout.addWidget(log_label)
    
    @staticmethod
    def update_actions_color_handle_last_button(scenario_layout: QVBoxLayout, 
                                               go_to_previous_state: Callable):
        """
        Met à jour dynamiquement le style des widgets dans le layout du scénario
        """
        total_widgets = scenario_layout.count()
        
        for i in range(total_widgets):
            widget = scenario_layout.itemAt(i).widget()
            if not widget:
                continue
            
            is_last_widget = (i == total_widgets - 1)
            UIManager._style_scenario_widget(widget, is_last_widget, go_to_previous_state)
    
    @staticmethod
    def _style_scenario_widget(widget: QWidget, is_last: bool, go_to_previous_state: Callable):
        """Applique les styles à un widget de scénario"""
        if is_last:
            # Styles pour le dernier widget
            widget.setStyleSheet("background-color: #669bbc; border-radius: 8px;")
            UIManager._apply_last_widget_styles(widget, go_to_previous_state)
        else:
            # Styles pour les widgets intermédiaires
            widget.setStyleSheet("background-color: #ffffff; border: 1px solid #b2cddd; border-radius: 8px;")
            UIManager._apply_intermediate_widget_styles(widget)
        
        # Appliquer des styles spécifiques aux types de widgets
        UIManager._style_child_widgets(widget, is_last)
    
    @staticmethod
    def _apply_last_widget_styles(widget: QWidget, go_to_previous_state: Callable):
        """Applique les styles spécifiques au dernier widget"""
        # Style des labels
        for label in widget.findChildren(QLabel):
            if label.text().startswith("Random"):
                label.setStyleSheet(UIStyles.get_label_style("white", 9))
            else:
                label.setStyleSheet(UIStyles.get_label_style("white", 16))
        
        # Bouton de retour
        buttons = widget.findChildren(QPushButton)
        if buttons:
            last_button = buttons[0]
            last_button.setVisible(True)
            last_button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            try:
                last_button.clicked.disconnect()
            except TypeError:
                pass
            
            last_button.clicked.connect(go_to_previous_state)
    
    @staticmethod
    def _apply_intermediate_widget_styles(widget: QWidget):
        """Applique les styles aux widgets intermédiaires"""
        # Style des labels
        labels = widget.findChildren(QLabel)
        for idx, label in enumerate(labels):
            if label.text().startswith("Random"):
                label.setStyleSheet(UIStyles.get_label_style("#669bbc", 9))
            elif idx == 0:
                label.setStyleSheet(UIStyles.get_label_style("#669bbc", 16))
            else:
                label.setStyleSheet(UIStyles.get_label_style("#669bbc", 14))
        
        # Cacher le dernier bouton
        buttons = widget.findChildren(QPushButton)
        if buttons:
            buttons[-1].setVisible(False)
    
    @staticmethod
    def _style_child_widgets(widget: QWidget, is_last: bool):
        """Applique les styles aux widgets enfants"""
        # QSpinBox
        spin_boxes = widget.findChildren(QSpinBox)
        if spin_boxes:
            arrow_path = Settings.ARROW_DOWN_W_PATH if is_last else Settings.ARROW_DOWN_PATH
            border_color = "white" if is_last else "#669bbc"
            
            if ValidationUtils.path_exists(arrow_path):
                style = UIStyles.get_spinbox_style(arrow_path, border_color)
                spin_boxes[0].setStyleSheet(style)
        
        # QCheckBox
        checkboxes = widget.findChildren(QCheckBox)
        if checkboxes:
            checkbox = checkboxes[0]
            if checkbox.isChecked():
                additional_style = """
                    QCheckBox::indicator:checked  {
                        background-color: #669bbc;
                        border: 2px solid #ffffff;
                    }
                """
            else:
                additional_style = """
                    QCheckBox::indicator {
                        color: gray;
                        background-color: #e0e0e0; 
                        border: 1px solid #cccccc;
                    }
                """
            
            current_style = checkbox.styleSheet()
            new_style = f"{current_style} {additional_style}" if current_style else additional_style
            checkbox.setStyleSheet(new_style)
        
        # QComboBox
        comboboxes = widget.findChildren(PyQt6.QtWidgets.QComboBox)
        if comboboxes and Settings.DOWN_EXISTS:
            combobox = comboboxes[0]
            old_style = combobox.styleSheet()
            new_style = UIStyles.get_combobox_style(Settings.ARROW_DOWN_PATH)
            combobox.setStyleSheet(f"{old_style} {new_style}")
        
        # QTextEdit - gestion des clics
        textedits = widget.findChildren(QTextEdit)
        for idx, textedit in enumerate(textedits):
            textedit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            textedit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            def create_handler(te, index):
                def handler(event):
                    UIManager._handle_textedit_click(te, index)
                    return QTextEdit.mousePressEvent(te, event)
                return handler
            
            textedit.mousePressEvent = create_handler(textedit, idx)
        
        # QLineEdit - validation
        UIManager._setup_lineedit_validators(widget)
    
    @staticmethod
    def _handle_textedit_click(textedit: QTextEdit, index: int):
        """Gère le clic sur un QTextEdit"""
        dialog = CustomTextDialog(textedit, texte_initial=textedit.toPlainText())
        if dialog.exec():
            new_text = dialog.get_text()
            textedit.setPlainText(new_text)
        textedit.clearFocus()
    
    @staticmethod
    def _setup_lineedit_validators(widget: QWidget):
        """Configure les validateurs pour les QLineEdit"""
        lineedits = widget.findChildren(QLineEdit)
        if not lineedits:
            return
        
        # Séparer le QLineEdit lié à une checkbox
        checkbox_lineedit = None
        regular_lineedits = []
        
        for lineedit in lineedits:
            parent = lineedit.parent()
            if parent and any(isinstance(child, QCheckBox) for child in parent.children()):
                checkbox_lineedit = lineedit
            else:
                regular_lineedits.append(lineedit)
        
        # Valideurs pour les QLineEdit réguliers
        for idx, lineedit in enumerate(regular_lineedits):
            default_val = "50,50" if (len(regular_lineedits) > 1 and idx == 0) else "1,1"
            
            def create_validator(le, default):
                return lambda: ValidationUtils.validate_qlineedit_with_range(le, default)
            
            lineedit.editingFinished.connect(create_validator(lineedit, default_val))
        
        # Validateur pour le QLineEdit lié à checkbox
        if checkbox_lineedit:
            checkbox_lineedit.editingFinished.connect(
                lambda: UIManager.validate_checkbox_linked_qlineedit(checkbox_lineedit)
            )
    
    @staticmethod
    def validate_checkbox_linked_qlineedit(qlineedit: QLineEdit):
        """Valide un QLineEdit lié à une checkbox"""
        if not qlineedit:
            return
        
        parent_widget = qlineedit.parent()
        full_state = parent_widget.property("full_state") if parent_widget else None
        text = qlineedit.text().strip()
        old_style = qlineedit.styleSheet()
        cleaned_style = ValidationUtils.remove_border_from_style(old_style)
        
        # Validation conditionnelle basée sur full_state
        if full_state and isinstance(full_state, dict):
            sub_id = full_state.get("id", "")
            
            # Chercher la checkbox associée
            checkbox = next((child for child in parent_widget.children() 
                            if isinstance(child, QCheckBox)), None)
            
            if sub_id in ["open_spam", "open_inbox"] and checkbox and checkbox.isChecked():
                if text:
                    qlineedit.setStyleSheet(cleaned_style)
                    qlineedit.setToolTip("")
                    return
                else:
                    default_text = full_state.get("label", "Google")
                    qlineedit.setText(default_text)
                    new_style = ValidationUtils.inject_border_into_style(cleaned_style)
                    qlineedit.setStyleSheet(new_style)
                    qlineedit.setToolTip("Texte invalide. Valeur remplacée par défaut.")
                    return
        
        # Validation classique
        if text.isdigit() or len(text) < 4:
            qlineedit.setText("Google")
            new_style = ValidationUtils.inject_border_into_style(cleaned_style)
            qlineedit.setStyleSheet(new_style)
            qlineedit.setToolTip("Le texte est un nombre ou trop court, veuillez corriger.")
        else:
            qlineedit.setStyleSheet(cleaned_style)
            qlineedit.setToolTip("")
    
    @staticmethod
    def remove_copier(scenario_layout: QVBoxLayout, reset_options_layout: QVBoxLayout):
        """
        Supprime les boutons de réinitialisation redondants
        """
        # Trouver l'index du dernier widget avec checkbox
        last_checkbox_index = -1
        for i in range(scenario_layout.count()):
            widget = scenario_layout.itemAt(i).widget()
            if widget and any(isinstance(child, QCheckBox) for child in widget.children()):
                last_checkbox_index = i
        
        if last_checkbox_index == -1:
            return
        
        # Collecter les labels des widgets après la dernière checkbox
        scenario_labels = []
        for i in range(last_checkbox_index + 1, scenario_layout.count()):
            widget = scenario_layout.itemAt(i).widget()
            if widget:
                labels = [child.text() for child in widget.children() 
                         if isinstance(child, QLabel)]
                if labels:
                    scenario_labels.append(labels[0])
        
        # Collecter les textes des boutons existants
        reset_button_texts = []
        for i in range(reset_options_layout.count()):
            widget = reset_options_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                reset_button_texts.append(widget.text())
        
        # Déterminer les boutons à conserver
        buttons_to_keep = [text for text in reset_button_texts 
                          if text not in scenario_labels]
        
        # Supprimer les boutons redondants
        for i in reversed(range(reset_options_layout.count())):
            widget = reset_options_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() not in buttons_to_keep:
                widget.deleteLater()
                reset_options_layout.removeWidget(widget)
    
    @staticmethod
    def remove_initaile(scenario_layout: QVBoxLayout, reset_options_layout: QVBoxLayout):
        """
        Supprime les boutons correspondant aux états initiaux
        """
        # Collecter les labels des états initiaux
        init_state_labels = []
        for i in range(scenario_layout.count()):
            widget = scenario_layout.itemAt(i).widget()
            if widget:
                full_state = widget.property("full_state")
                if full_state and full_state.get("INITAILE"):
                    init_state_labels.append(full_state.get("label", ""))
        
        # Collecter les textes des boutons
        reset_button_texts = []
        for i in range(reset_options_layout.count()):
            widget = reset_options_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                reset_button_texts.append(widget.text())
        
        # Déterminer les boutons à conserver
        buttons_to_keep = [text for text in reset_button_texts 
                          if text not in init_state_labels]
        
        # Supprimer les boutons redondants
        for i in reversed(range(reset_options_layout.count())):
            widget = reset_options_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() not in buttons_to_keep:
                widget.deleteLater()
                reset_options_layout.removeWidget(widget)


class UIInitializer:
    """Classe pour initialiser l'interface utilisateur depuis MainWindow"""
    
    @staticmethod
    def initialize_main_window(window, json_data):
        """
        Initialise la fenêtre principale avec toutes ses composantes
        """
        # Charger l'interface
        uic.loadUi(Settings.INTERFACE_UI, window)
        
        # Initialiser les données
        window.states = json_data
        window.STATE_STACK = []
        
        # Initialiser les conteneurs principaux
        UIInitializer._initialize_containers(window)
        
        # Initialiser les templates
        UIInitializer._initialize_templates(window)
        
        # Initialiser les boutons
        UIInitializer._initialize_buttons(window)
        
        # Initialiser les champs de texte
        UIInitializer._initialize_text_fields(window)
        
        # Initialiser les onglets
        UIInitializer._initialize_tabs(window)
        
        # Initialiser les combobox
        UIInitializer._initialize_comboboxes(window)
        
        # Initialiser les logs
        UIInitializer._initialize_logs(window)
        
        # Configurer les tables
        UIInitializer._configure_tables(window)
        
        return window
    
    @staticmethod
    def _initialize_containers(window):
        """Initialise les conteneurs de layout"""
        # Conteneur des options de réinitialisation
        window.reset_options_container = window.findChild(QWidget, "resetOptionsContainer")
        if window.reset_options_container:
            window.reset_options_layout = QVBoxLayout(window.reset_options_container)
            window.reset_options_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Conteneur du scénario
        window.scenario_container = window.findChild(QWidget, "scenarioContainer")
        if window.scenario_container:
            window.scenario_layout = QVBoxLayout(window.scenario_container)
            window.scenario_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    
    @staticmethod
    def _initialize_templates(window):
        """Initialise et cache les templates"""
        templates = {
            "template_button": ("TemepleteButton", QPushButton),
            "template_button_2": ("TemepleteButton_2", QPushButton),
            "template_frame1": ("Template1", QFrame),
            "template_frame2": ("Template2", QFrame),
            "template_frame3": ("Template3", QFrame),
            "template_frame4": ("Template4", QFrame),
            "template_frame5": ("Template5", QFrame)
        }
        
        for attr_name, (obj_name, obj_type) in templates.items():
            widget = window.findChild(obj_type, obj_name)
            if widget:
                setattr(window, attr_name, widget)
                if hasattr(widget, 'hide'):
                    widget.hide()
    
    @staticmethod
    def _initialize_buttons(window):
        """Initialise et configure les boutons"""
        # Bouton d'état initial
        window.Button_Initaile_state = window.findChild(QPushButton, "Button_Initaile_state")
        if window.Button_Initaile_state:
            window.Button_Initaile_state.clicked.connect(window.Load_Initial_Options)
        
        # Bouton de soumission
        window.submit_button = window.findChild(QPushButton, "submitButton")
        if window.submit_button:
            window.submit_button.clicked.connect(lambda: window.Submit_Button_Clicked(window))
        
        # Bouton de nettoyage
        window.ClearButton = window.findChild(QPushButton, "ClearButton")
        UIInitializer._style_icon_button(
            window.ClearButton, "clear.png", QSize(32, 32), 
            window.Clear_Button_Clicked
        )
        
        # Bouton de copie
        window.CopyButton = window.findChild(QPushButton, "CopyButton")
        UIInitializer._style_icon_button(
            window.CopyButton, "copyLog.png", QSize(26, 26),
            window.Copy_Logs_To_Clipboard
        )
        
        # Bouton de sauvegarde
        window.SaveButton = window.findChild(QPushButton, "saveButton")
        if window.SaveButton:
            icon_path = os.path.join(Settings.ICONS_DIR, "save.png")
            if ValidationUtils.path_exists(icon_path):
                window.SaveButton.setIcon(QIcon(icon_path))
                window.SaveButton.setIconSize(QSize(16, 16))
                window.SaveButton.clicked.connect(window.Handle_Save)
        
        # Bouton de déconnexion
        window.log_out_Button = window.findChild(QPushButton, "LogOut")
        if window.log_out_Button:
            window.log_out_Button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            window.log_out_Button.clicked.connect(window.logOut)
            
            icon_path = os.path.join(Settings.ICONS_DIR, "LogOut4.png")
            if ValidationUtils.path_exists(icon_path):
                window.log_out_Button.setIcon(QIcon(icon_path))
                window.log_out_Button.setIconSize(QSize(18, 18))
    
    @staticmethod
    def _style_icon_button(button: QPushButton, icon_name: str, 
                          icon_size: QSize, click_handler: Callable):
        """Applique un style d'icône à un bouton"""
        if not button:
            return
        
        icon_path = os.path.join(Settings.ICONS_DIR, icon_name)
        if ValidationUtils.path_exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(icon_size)
        
        button.setText("")
        button.setFixedSize(icon_size.width() + 4, icon_size.height() + 4)
        button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
            }
            QPushButton::icon {
                alignment: center;
            }
        """)
        button.clicked.connect(click_handler)
    
    @staticmethod
    def _initialize_text_fields(window):
        """Initialise les champs de texte"""
        # Placeholder pour textEdit_3
        if hasattr(window, 'textEdit_3'):
            window.textEdit_3.setPlaceholderText(
                "Please enter the data in the following format : \n"
                "Email* ; passwordEmail* ; ipAddress* ; port* ; login ; password ; recovery_email , new_recovery_email"
            )
        
        # Placeholder pour textEdit_4
        if hasattr(window, 'textEdit_4'):
            window.textEdit_4.setPlaceholderText(
                "Specify the maximum number of operations to process"
            )
        
        # Champ de recherche
        window.lineEdit_search = window.findChild(QLineEdit, "lineEdit_search")
        if window.lineEdit_search:
            window.lineEdit_search.hide()
    
    @staticmethod
    def _initialize_tabs(window):
        """Initialise et configure les onglets"""
        # Onglet principal des résultats
        window.tabWidgetResult = window.findChild(QTabWidget, "tabWidgetResult")
        if window.tabWidgetResult:
            window.tabWidgetResult.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)
            UIInitializer._set_tab_icons(window.tabWidgetResult)
        
        # Interface secondaire
        window.INTERFACE = window.findChild(QTabWidget, "interface_2")
        if window.INTERFACE:
            window.INTERFACE.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)
            UIInitializer._add_result_tab_frame(window.INTERFACE)
    
    @staticmethod
    def _set_tab_icons(tab_widget: QTabWidget):
        """Définit les icônes pour les onglets"""
        if not ValidationUtils.path_exists(Settings.ICONS_DIR):
            return
        
        icon_size = QSize(40, 40)
        for i in range(tab_widget.count()):
            tab_text = tab_widget.tabText(i)
            icon_name = tab_text.lower().replace(" ", "_") + ".png"
            icon_path = os.path.join(Settings.ICONS_DIR, icon_name)
            
            if ValidationUtils.path_exists(icon_path):
                icon = QIcon(icon_path)
                icon_pixmap = icon.pixmap(icon_size)
                tab_widget.setTabIcon(i, QIcon(icon_pixmap))
    
    @staticmethod
    def _add_result_tab_frame(tab_widget: QTabWidget):
        """Ajoute un cadre à l'onglet Result"""
        for i in range(tab_widget.count()):
            if tab_widget.tabText(i).startswith("Result"):
                tab_content = tab_widget.widget(i)
                frame = QFrame(tab_content)
                frame.setStyleSheet("background-color: #F5F5F5; border-right: 1px solid #669bbc;")
                frame.setGeometry(0, 660, 179, 300)
                frame.show()
                break
    
    @staticmethod
    def _initialize_comboboxes(window):
        """Initialise et configure les combobox"""
        # Combobox des navigateurs
        window.browser = window.findChild(QComboBox, "browsers")
        if window.browser:
            UIInitializer._style_combobox_arrow(window.browser)
            UIInitializer._populate_browser_combobox(window.browser)
        
        # Combobox des ISPs
        window.Isp = window.findChild(QComboBox, "Isps")
        if window.Isp:
            UIInitializer._style_combobox_arrow(window.Isp)
            UIInitializer._populate_isp_combobox(window.Isp)
            UIInitializer._set_default_isp(window.Isp)
        
        # Combobox des scénarios sauvegardés
        window.saveSanario = window.findChild(QComboBox, "saveSanario")
        if window.saveSanario:
            UIInitializer._style_combobox_arrow(window.saveSanario)
            window.saveSanario.currentTextChanged.connect(window.Scenario_Changed)
    
    @staticmethod
    def _style_combobox_arrow(combobox: QComboBox):
        """Applique un style de flèche personnalisé au combobox"""
        if not ValidationUtils.path_exists(Settings.ARROW_DOWN_PATH):
            return
        
        style = f'''
            QComboBox::down-arrow {{
                image: url("{Settings.ARROW_DOWN_PATH}");
                width: 16px;
                height: 16px;
            }}
        '''
        current_style = combobox.styleSheet()
        combobox.setStyleSheet(f"{current_style} {style}")
    
    @staticmethod
    def _populate_browser_combobox(combobox: QComboBox):
        """Remplit le combobox des navigateurs"""
        browsers = [
            ("chrome.png", "Chrome"),
            ("firefox.png", "Firefox"),
            ("edge.png", "Edge"),
            ("comodo.png", "Comodo")
        ]
        
        for icon_name, browser_name in browsers:
            icon_path = os.path.join(Settings.ICONS_DIR, icon_name)
            if ValidationUtils.path_exists(icon_path):
                combobox.addItem(QIcon(icon_path), browser_name)
            else:
                combobox.addItem(browser_name)
    
    @staticmethod
    def _populate_isp_combobox(combobox: QComboBox):
        """Remplit le combobox des ISPs"""
        combobox.clear()
        
        for name, icon_file in Settings.SERVICES.items():
            icon_path = os.path.join(Settings.ICONS_DIR, icon_file)
            if ValidationUtils.path_exists(icon_path):
                combobox.addItem(QIcon(icon_path), name)
            else:
                combobox.addItem(name)
    
    @staticmethod
    def _set_default_isp(combobox: QComboBox):
        """Définit l'ISP par défaut depuis le fichier de configuration"""
        if not ValidationUtils.path_exists(Settings.FILE_ISP):
            return
        
        try:
            with open(Settings.FILE_ISP, 'r', encoding='utf-8') as f:
                line = f.readline().strip().lower()
            
            isp_map = {
                "gmail": "Gmail",
                "hotmail": "Hotmail",
                "yahoo": "Yahoo"
            }
            
            selected_isp = None
            for key, value in isp_map.items():
                if key in line:
                    selected_isp = value
                    break
            
            if selected_isp:
                index = combobox.findText(selected_isp)
                if index >= 0:
                    combobox.setCurrentIndex(index)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier ISP: {e}")
    
    @staticmethod
    def _initialize_logs(window):
        """Initialise la zone de logs"""
        window.log_container = window.findChild(QWidget, "log")
        if window.log_container:
            window.log_layout = QVBoxLayout(window.log_container)
            window.log_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            window.log_container.adjustSize()
            window.log_container.setFixedWidth(1627)
    
    @staticmethod
    def _configure_tables(window):
        """Configure les tables pour l'étirement automatique"""
        for table in window.findChildren(QTableWidget):
            for col in range(table.columnCount()):
                table.horizontalHeader().setSectionResizeMode(
                    col, QHeaderView.ResizeMode.Stretch
                )
        
        # Style des QSpinBox
        if Settings.DOWN_EXISTS and Settings.UP_EXISTS:
            for spin_box in window.findChildren(QSpinBox):
                current_style = spin_box.styleSheet()
                arrow_style = f"""
                    QSpinBox::down-button {{
                        image: url("{Settings.ARROW_DOWN_PATH}");
                        width: 13px;
                        height: 13px;
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                    }}
                    QSpinBox::up-button {{
                        image: url("{Settings.ARROW_UP_PATH}");
                        width: 13px;
                        height: 13px;
                        border-top-left-radius: 5px;
                        border-bottom-left-radius: 5px;
                    }}
                """
                spin_box.setStyleSheet(f"{current_style} {arrow_style}")