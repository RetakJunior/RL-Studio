"""
RL Studio - 3D Reference & Mannequin Docker
Clean, modern dark studio interface integrated into RL Studio.
Provides model selection, viewport controls, and 1-click canvas layer injection.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QApplication, QLabel, QSlider, QRadioButton, QButtonGroup, QFileDialog,
    QProgressBar, QGroupBox, QFrame, QDockWidget, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QImage, QPalette

try:
    import krita
    BaseDockWidget = getattr(krita, 'DockWidget', QDockWidget)
except Exception:
    BaseDockWidget = QDockWidget
from .obj_loader import OBJLoader
from .gl_viewport import GLViewport3D
from .model_manager import ModelManager

def _build_style_sheet(palette):
    """Use Krita's active palette so the docker and import dialog fit the app."""
    window = palette.color(QPalette.Window).name()
    window_text = palette.color(QPalette.WindowText).name()
    base = palette.color(QPalette.Base).name()
    text = palette.color(QPalette.Text).name()
    button = palette.color(QPalette.Button).name()
    button_text = palette.color(QPalette.ButtonText).name()
    border = palette.color(QPalette.Mid).name()
    accent = palette.color(QPalette.Highlight).name()
    accent_text = palette.color(QPalette.HighlightedText).name()

    return """
    QFrame#mainContainer {{ background: {window}; color: {window_text}; }}
    QComboBox, QLineEdit, QSpinBox {{
        background: {base}; color: {text}; border: 1px solid {border};
        border-radius: 3px; padding: 4px 6px; min-height: 22px;
    }}
    QComboBox:hover, QLineEdit:focus {{ border-color: {accent}; }}
    QComboBox::drop-down {{ width: 18px; border: 0; }}
    QComboBox QAbstractItemView, QTreeView, QListView {{
        background: {base}; color: {text}; selection-background-color: {accent};
        selection-color: {accent_text}; outline: 0;
    }}
    QPushButton {{
        background: {button}; color: {button_text}; border: 1px solid {border};
        border-radius: 3px; padding: 5px 8px; min-height: 22px;
    }}
    QPushButton:hover, QToolButton:hover {{ background: {accent}; color: {accent_text}; }}
    QPushButton:checked {{ background: {accent}; color: {accent_text}; border-color: {accent}; }}
    QPushButton#btnImportModel {{ min-width: 28px; max-width: 28px; padding: 0; }}
    QPushButton#btnTransfer {{
        background: {accent}; color: {accent_text}; border: 0; font-weight: 600;
    }}
    QLabel {{ color: {window_text}; }}
    QHeaderView::section {{
        background: {button}; color: {button_text}; border: 0;
        border-bottom: 1px solid {border}; padding: 4px;
    }}
    QToolButton {{ background: transparent; color: {button_text}; border: 0; }}
    QProgressBar {{ background: {base}; border: 0; border-radius: 2px; }}
    QProgressBar::chunk {{ background: {accent}; border-radius: 2px; }}
    QSlider::groove:horizontal {{ height: 4px; background: {border}; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: {accent}; border-radius: 2px; }}
    QSlider::handle:horizontal {{
        background: {button_text}; border: 1px solid {accent}; width: 12px;
        margin: -4px 0; border-radius: 6px;
    }}
    """.format(**locals())

class RLStudio3DDocker(BaseDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Referans & Modeller")
        self.manager = ModelManager()
        self.current_mesh = None

        # Base Widget & Layout
        self.base_widget = QFrame()
        self.base_widget.setObjectName("mainContainer")
        self.style_sheet = _build_style_sheet(QApplication.palette())
        self.base_widget.setStyleSheet(self.style_sheet)
        self.layout = QVBoxLayout(self.base_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(4)

        # 1. Category & Model Selector
        top_bar = QHBoxLayout()
        self.cat_combo = QComboBox()
        self.cat_combo.setToolTip("Kategori seçin")
        self.model_combo = QComboBox()
        self.model_combo.setToolTip("3D Model seçin")
        for combo in (self.cat_combo, self.model_combo):
            combo.setMinimumContentsLength(6)
            combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            combo.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.btn_import = QPushButton("＋")
        self.btn_import.setObjectName("btnImportModel")
        self.btn_import.setToolTip("OBJ modeli ekle")
        self.btn_import.setFixedSize(28, 28)

        top_bar.addWidget(self.cat_combo, 1)
        top_bar.addWidget(self.model_combo, 1)
        top_bar.addWidget(self.btn_import)
        self.layout.addLayout(top_bar)

        # Download progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        # 2. Interactive 3D Viewport
        self.viewport = GLViewport3D(self.base_widget)
        self.viewport.setMinimumSize(120, 96)
        self.viewport.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.layout.addWidget(self.viewport, 1)

        # 3. Viewport Mode & Light Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(4)

        self.btn_clay = QPushButton("Gölge")
        self.btn_clay.setCheckable(True)
        self.btn_clay.setChecked(True)
        self.btn_wire = QPushButton("Tel")
        self.btn_wire.setCheckable(True)
        self.btn_silh = QPushButton("Silüet")
        self.btn_silh.setCheckable(True)

        mode_group = QButtonGroup(self)
        mode_group.addButton(self.btn_clay, 0)
        mode_group.addButton(self.btn_wire, 1)
        mode_group.addButton(self.btn_silh, 2)
        mode_group.buttonClicked[int].connect(self.viewport.set_render_mode)

        controls_layout.addWidget(self.btn_clay)
        controls_layout.addWidget(self.btn_wire)
        controls_layout.addWidget(self.btn_silh)

        self.btn_reset_cam = QPushButton("↺")
        self.btn_reset_cam.setToolTip("Kamera açısını sıfırla")
        self.btn_reset_cam.clicked.connect(self.viewport.reset_camera)
        controls_layout.addWidget(self.btn_reset_cam)
        self.layout.addLayout(controls_layout)

        # Light Angle Slider
        light_layout = QHBoxLayout()
        lbl_light = QLabel("Işık")
        self.light_slider = QSlider(Qt.Horizontal)
        self.light_slider.setRange(0, 360)
        self.light_slider.setValue(45)
        self.light_slider.valueChanged.connect(self._on_light_changed)
        light_layout.addWidget(lbl_light)
        light_layout.addWidget(self.light_slider)
        self.layout.addLayout(light_layout)

        # 4. Canvas Bridge (Tuvale Aktar Butonu)
        self.btn_transfer = QPushButton("Tuvale aktar")
        self.btn_transfer.setObjectName("btnTransfer")
        self.btn_transfer.setToolTip("Mevcut 3D açıyı tuval üzerine yeni bir referans katmanı olarak aktar")
        self.btn_transfer.clicked.connect(self.transfer_to_canvas)
        self.layout.addWidget(self.btn_transfer)

        self.setWidget(self.base_widget)

        # Signal connections
        self.cat_combo.currentIndexChanged.connect(self._on_category_changed)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.btn_import.clicked.connect(self._on_import_model)
        self.manager.download_progress.connect(self._on_download_progress)
        self.manager.model_ready.connect(self._on_model_loaded_from_disk)
        self.manager.catalog_updated.connect(self._populate_categories)

        # Initial populate
        self._populate_categories()

    def canvasChanged(self, canvas):
        pass

    def _on_light_changed(self, val):
        self.viewport.set_light_angle(float(val), 40.0)

    def _populate_categories(self):
        self.cat_combo.blockSignals(True)
        self.cat_combo.clear()
        categories = self.manager.get_categories()
        for cat in categories:
            self.cat_combo.addItem(cat.get("name", "Kategori"), cat)
        self.cat_combo.blockSignals(False)
        self._on_category_changed(0)

    def _on_category_changed(self, idx):
        cat_data = self.cat_combo.currentData()
        if not cat_data:
            return

        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        models = cat_data.get("models", [])
        for m in models:
            self.model_combo.addItem(m.get("title", "Model"), m)
        self.model_combo.blockSignals(False)

        if models:
            self._on_model_changed(0)

    def _on_model_changed(self, idx):
        model_data = self.model_combo.currentData()
        if not model_data:
            return
        self.manager.fetch_model(model_data)

    def _on_download_progress(self, percent, text):
        self.progress_bar.show()
        self.progress_bar.setValue(percent)
        if percent >= 100:
            self.progress_bar.hide()

    def _on_model_loaded_from_disk(self, filepath):
        self.progress_bar.hide()
        if not os.path.exists(filepath):
            return

        mesh = OBJLoader.load(filepath)
        if mesh:
            self.current_mesh = mesh
            self.viewport.set_mesh(mesh)

    def _on_import_model(self):
        dialog = QFileDialog(self, "OBJ modeli ekle", os.path.expanduser("~"))
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilter("Wavefront OBJ (*.obj)")
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setStyleSheet(self.style_sheet)
        dialog.setPalette(QApplication.palette())
        dialog.setLabelText(QFileDialog.Accept, "Ekle")
        dialog.setLabelText(QFileDialog.Reject, "İptal")
        dialog.setLabelText(QFileDialog.LookIn, "Konum")
        dialog.setLabelText(QFileDialog.FileName, "Dosya")
        dialog.setLabelText(QFileDialog.FileType, "Tür")

        if dialog.exec_() != QFileDialog.Accepted:
            return
        files = dialog.selectedFiles()
        if not files:
            return

        imported_path = self.manager.import_custom_model(files[0])
        if imported_path:
            for i in range(self.cat_combo.count()):
                cat = self.cat_combo.itemData(i)
                if cat and cat.get("id") == "custom":
                    self.cat_combo.setCurrentIndex(i)
                    break

    def transfer_to_canvas(self):
        """Captures the 3D snapshot and inserts it into active Krita canvas."""
        app = krita.Krita.instance()
        doc = app.activeDocument()
        if not doc:
            self._show_transfer_error("Önce bir tuval belgesi aç.")
            return
        if not self.current_mesh:
            self._show_transfer_error("Önce listeden bir 3D model seç.")
            return
        if doc.colorModel() != "RGBA" or doc.colorDepth() != "U8":
            self._show_transfer_error("Tuvale aktarım şu an RGBA / 8 bit belgelerde destekleniyor.")
            return

        # Grab viewport frame
        snapshot = self.viewport.capture_snapshot(transparent_bg=True)
        if snapshot.isNull():
            self._show_transfer_error("3D görünümünden görüntü alınamadı.")
            return

        # Prepare layer name
        model_title = self.model_combo.currentText() or "Model"
        layer_name = f"3D Referans ({model_title})"

        # Create new paint layer in Krita
        root_node = doc.rootNode()
        layer = doc.createNode(layer_name, "paintlayer")
        if not layer:
            self._show_transfer_error("Yeni boyama katmanı oluşturulamadı.")
            return
        # `above=None` appends at the bottom of Krita's layer stack. A white
        # Background layer there would cover the newly inserted transparent
        # render, so explicitly put the reference above the current top layer.
        root_children = root_node.childNodes()
        top_layer = root_children[0] if root_children else None
        if not root_node.addChildNode(layer, top_layer):
            self._show_transfer_error("Katman belgeye eklenemedi.")
            return

        # Scale snapshot to fit canvas maintaining aspect ratio
        canvas_w = doc.width()
        canvas_h = doc.height()

        target_size = snapshot.size().scaled(int(canvas_w * 0.8), int(canvas_h * 0.8), Qt.KeepAspectRatio)
        scaled_img = snapshot.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Center on canvas
        pos_x = (canvas_w - scaled_img.width()) // 2
        pos_y = (canvas_h - scaled_img.height()) // 2

        # Krita stores integer RGBA pixel data in BGRA byte order.
        converted = scaled_img.convertToFormat(QImage.Format_ARGB32)
        width = converted.width()
        height = converted.height()
        row_bytes = width * 4
        stride = converted.bytesPerLine()
        source_bytes = converted.bits().asstring(stride * height)
        if stride == row_bytes:
            raw_bytes = source_bytes
        else:
            raw_bytes = b"".join(
                source_bytes[row * stride:row * stride + row_bytes]
                for row in range(height)
            )
        byte_array = QByteArray(raw_bytes)
        pixel_size = len(layer.pixelData(0, 0, 1, 1))
        expected_bytes = width * height * pixel_size

        if pixel_size == 0:
            root_node.removeChildNode(layer)
            self._show_transfer_error("Krita yeni katmana yazılabilir piksel belleği hazırlamadı.")
            return
        if pixel_size != 4 or byte_array.size() != expected_bytes:
            root_node.removeChildNode(layer)
            self._show_transfer_error(
                "Görüntü verisi belge biçimiyle eşleşmiyor "
                "({} B alındı, {} B gerekiyor).".format(
                    byte_array.size(), expected_bytes
                )
            )
            return

        if not layer.setPixelData(byte_array, pos_x, pos_y, width, height):
            root_node.removeChildNode(layer)
            self._show_transfer_error(
                "Krita katmanına piksel yazımı reddetti "
                "({} B / {} B).".format(byte_array.size(), expected_bytes)
            )
            return
        doc.setActiveNode(layer)
        doc.refreshProjection()
        print(f"[RL Studio 3D] '{layer_name}' başarıyla tuvale aktarıldı!")

    def _show_transfer_error(self, message):
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle("Tuvale aktarılamadı")
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.setStyleSheet(self.style_sheet)
        dialog.setPalette(QApplication.palette())
        dialog.exec_()
