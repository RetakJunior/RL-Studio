"""
RL Studio - 3D Reference & Mannequin Docker
Clean, modern dark studio interface integrated into RL Studio.
Provides model selection, viewport controls, and 1-click canvas layer injection.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QLabel, QSlider, QRadioButton, QButtonGroup, QFileDialog,
    QProgressBar, QGroupBox, QFrame, QDockWidget
)
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QImage, QColor

try:
    import krita
    BaseDockWidget = getattr(krita, 'DockWidget', QDockWidget)
except Exception:
    BaseDockWidget = QDockWidget
from .obj_loader import OBJLoader
from .gl_viewport import GLViewport3D
from .model_manager import ModelManager

# Modern RL Studio Palette
STYLE_SHEET = """
QFrame#mainContainer {
    background-color: #16191F;
    color: #E2E8F0;
    font-family: sans-serif;
}
QComboBox {
    background-color: #212631;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 12px;
}
QComboBox:hover {
    border-color: #00ADB5;
}
QComboBox::drop-down {
    border: none;
}
QPushButton {
    background-color: #262D3D;
    color: #F1F5F9;
    border: 1px solid #3B455B;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #333D52;
    border-color: #00ADB5;
    color: #00ADB5;
}
QPushButton#btnTransfer {
    background-color: #00ADB5;
    color: #0F172A;
    border: none;
    font-weight: bold;
    padding: 8px 16px;
    font-size: 13px;
}
QPushButton#btnTransfer:hover {
    background-color: #00C4CE;
}
QLabel {
    color: #94A3B8;
    font-size: 11px;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #2D3748;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #00ADB5;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #F8FAFC;
    border: 1px solid #00ADB5;
    width: 12px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 6px;
}
"""

class RLStudio3DDocker(BaseDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Referans & Modeller")
        self.manager = ModelManager()
        self.current_mesh = None

        # Base Widget & Layout
        self.base_widget = QFrame()
        self.base_widget.setObjectName("mainContainer")
        self.base_widget.setStyleSheet(STYLE_SHEET)
        self.layout = QVBoxLayout(self.base_widget)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(6)

        # 1. Category & Model Selector
        top_bar = QHBoxLayout()
        self.cat_combo = QComboBox()
        self.cat_combo.setToolTip("Kategori seçin")
        self.model_combo = QComboBox()
        self.model_combo.setToolTip("3D Model seçin")
        self.btn_import = QPushButton("＋ Model Ekle")
        self.btn_import.setToolTip("Bilgisayarınızdan kendi OBJ modelinizi içe aktarın")

        top_bar.addWidget(self.cat_combo, 2)
        top_bar.addWidget(self.model_combo, 3)
        top_bar.addWidget(self.btn_import, 2)
        self.layout.addLayout(top_bar)

        # Download progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #00ADB5; }")
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        # 2. Interactive 3D Viewport
        self.viewport = GLViewport3D(self.base_widget)
        self.viewport.setMinimumSize(220, 260)
        self.layout.addWidget(self.viewport, 1)

        # 3. Viewport Mode & Light Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(4)

        self.btn_clay = QPushButton("Gölge")
        self.btn_clay.setCheckable(True)
        self.btn_clay.setChecked(True)
        self.btn_wire = QPushButton("Tel Kafes")
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

        self.btn_reset_cam = QPushButton("↺ Sıfırla")
        self.btn_reset_cam.setToolTip("Kamera açısını sıfırla")
        self.btn_reset_cam.clicked.connect(self.viewport.reset_camera)
        controls_layout.addWidget(self.btn_reset_cam)
        self.layout.addLayout(controls_layout)

        # Light Angle Slider
        light_layout = QHBoxLayout()
        lbl_light = QLabel("Işık Yönü:")
        self.light_slider = QSlider(Qt.Horizontal)
        self.light_slider.setRange(0, 360)
        self.light_slider.setValue(45)
        self.light_slider.valueChanged.connect(self._on_light_changed)
        light_layout.addWidget(lbl_light)
        light_layout.addWidget(self.light_slider)
        self.layout.addLayout(light_layout)

        # 4. Canvas Bridge (Tuvale Aktar Butonu)
        self.btn_transfer = QPushButton("🖼  Tuvale Aktar (Yeni Katman)")
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
        filepath, _ = QFileDialog.getOpenFileName(
            self, "3D Model Seç (*.obj)", "", "Wavefront OBJ (*.obj)"
        )
        if filepath:
            imported_path = self.manager.import_custom_model(filepath)
            if imported_path:
                # Switch to custom category
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
            print("[RL Studio 3D] Aktif tuval belgesi bulunamadı.")
            return

        # Grab viewport frame
        snapshot = self.viewport.capture_snapshot(transparent_bg=True)
        if snapshot.isNull():
            return

        # Prepare layer name
        model_title = self.model_combo.currentText() or "Model"
        layer_name = f"3D Referans ({model_title})"

        # Create new paint layer in Krita
        root_node = doc.rootNode()
        layer = doc.createPaintLayer(layer_name, "paintLayer")
        root_node.addChildNode(layer, None)

        # Scale snapshot to fit canvas maintaining aspect ratio
        canvas_w = doc.width()
        canvas_h = doc.height()

        target_size = snapshot.size().scaled(int(canvas_w * 0.8), int(canvas_h * 0.8), Qt.KeepAspectRatio)
        scaled_img = snapshot.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Center on canvas
        pos_x = (canvas_w - scaled_img.width()) // 2
        pos_y = (canvas_h - scaled_img.height()) // 2

        # Convert QImage to RGBA bytes for Krita setPixelData
        converted = scaled_img.convertToFormat(QImage.Format_RGBA8888)
        raw_bytes = converted.bits().asstring(converted.byteCount())
        byte_array = QByteArray(raw_bytes)

        layer.setPixelData(byte_array, pos_x, pos_y, scaled_img.width(), scaled_img.height())
        doc.refreshProjection()
        print(f"[RL Studio 3D] '{layer_name}' başarıyla tuvale aktarıldı!")
