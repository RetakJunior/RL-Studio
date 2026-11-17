"""
RL Studio - 3D Model & Cloud Asset Manager
Handles caching in ~/.local/share/rlstudio/3d_models/, category management,
and downloading models from free online CDN repositories.
"""

import os
import json
import shutil
import urllib.request
from PyQt5.QtCore import QObject, pyqtSignal, QThread

DEFAULT_MODELS_INDEX = {
    "categories": [
        {
            "id": "anatomy",
            "name": "İnsan & Anatomi",
            "models": [
                {
                    "id": "builtin_head",
                    "title": "Asaro / Düzlem Kafa Modeli",
                    "category": "anatomy",
                    "filename": "mannequin_head.obj",
                    "is_builtin": True,
                    "description": "Işık ve açı çalışması için düzlemsel insan kafası.",
                    "license": "CC0"
                },
                {
                    "id": "builtin_body",
                    "title": "Temel Manken Gövdesi",
                    "category": "anatomy",
                    "filename": "mannequin_body.obj",
                    "is_builtin": True,
                    "description": "Poz ve oran orantı için temel insan mankeni.",
                    "license": "CC0"
                }
            ]
        },
        {
            "id": "perspective",
            "name": "Perspektif & Formlar",
            "models": [
                {
                    "id": "builtin_cube",
                    "title": "3 Noktalı Perspektif Küpü",
                    "category": "perspective",
                    "filename": "perspective_cube.obj",
                    "is_builtin": True,
                    "description": "Kaçış noktaları ve mekan perspektifi kılavuz küpü.",
                    "license": "CC0"
                }
            ]
        },
        {
            "id": "custom",
            "name": "Özel Modellerim",
            "models": []
        }
    ]
}

# Free community models remote index URL (hosted on GitHub raw)
REMOTE_INDEX_URL = "https://raw.githubusercontent.com/RetakJunior/RL-Studio/main/assets/3d_models/models_index.json"

class DownloadWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str, str) # success, file_path, error_msg

    def __init__(self, url, target_path):
        super().__init__()
        self.url = url
        self.target_path = target_path

    def run(self):
        try:
            def report(count, block_size, total_size):
                if total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    self.progress.emit(min(percent, 100), f"%{min(percent, 100)}")

            temp_path = self.target_path + ".tmp"
            urllib.request.urlretrieve(self.url, temp_path, reporthook=report)
            os.rename(temp_path, self.target_path)
            self.finished.emit(True, self.target_path, "")
        except Exception as e:
            self.finished.emit(False, "", str(e))

class ModelManager(QObject):
    catalog_updated = pyqtSignal()
    download_progress = pyqtSignal(int, str)
    model_ready = pyqtSignal(str) # model_path

    def __init__(self):
        super().__init__()
        try:
            self.base_dir = os.path.expanduser("~/.local/share/rlstudio/3d_models")
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError:
            self.base_dir = "/tmp/rlstudio/3d_models"
            os.makedirs(self.base_dir, exist_ok=True)
        self.builtin_dir = os.path.join(os.path.dirname(__file__), "default_models")
        self.index_file = os.path.join(self.base_dir, "models_index.json")
        self.catalog = self._load_or_init_catalog()
        self._sync_builtin_models()
        self.active_worker = None

    def _sync_builtin_models(self):
        """Ensure built-in default models exist in local cache."""
        for root, _, files in os.walk(self.builtin_dir):
            for f in files:
                if f.endswith('.obj'):
                    src = os.path.join(root, f)
                    dst = os.path.join(self.base_dir, f)
                    if not os.path.exists(dst):
                        try:
                            shutil.copy2(src, dst)
                        except Exception as e:
                            print(f"[ModelManager] Copy error: {e}")

    def _load_or_init_catalog(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        self._save_catalog(DEFAULT_MODELS_INDEX)
        return DEFAULT_MODELS_INDEX

    def _save_catalog(self, catalog):
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ModelManager] Save catalog error: {e}")

    def get_categories(self):
        return self.catalog.get("categories", [])

    def get_model_path(self, model_info):
        """Returns absolute path if available locally, else None."""
        fname = model_info.get("filename")
        if not fname:
            return None
        local_path = os.path.join(self.base_dir, fname)
        if os.path.exists(local_path):
            return local_path
        builtin_path = os.path.join(self.builtin_dir, fname)
        if os.path.exists(builtin_path):
            return builtin_path
        return None

    def fetch_model(self, model_info):
        """Ensures model is on disk. If remote, downloads it."""
        path = self.get_model_path(model_info)
        if path:
            self.model_ready.emit(path)
            return

        url = model_info.get("url")
        fname = model_info.get("filename", f"{model_info.get('id', 'model')}.obj")
        target_path = os.path.join(self.base_dir, fname)

        if not url:
            print("[ModelManager] No URL for model download.")
            return

        self.active_worker = DownloadWorker(url, target_path)
        self.active_worker.progress.connect(self.download_progress.emit)
        self.active_worker.finished.connect(self._on_download_finished)
        self.active_worker.start()

    def _on_download_finished(self, success, file_path, error_msg):
        if success:
            self.model_ready.emit(file_path)
        else:
            print(f"[ModelManager] Download failed: {error_msg}")

    def import_custom_model(self, src_filepath):
        """User imports their own OBJ model into RL Studio."""
        if not os.path.isfile(src_filepath):
            return None

        fname = os.path.basename(src_filepath)
        dst_path = os.path.join(self.base_dir, fname)
        try:
            if os.path.abspath(src_filepath) != os.path.abspath(dst_path):
                shutil.copy2(src_filepath, dst_path)

            title = os.path.splitext(fname)[0].replace('_', ' ').title()
            model_info = {
                "id": f"custom_{os.path.splitext(fname)[0]}",
                "title": title,
                "category": "custom",
                "filename": fname,
                "is_custom": True,
                "description": f"Yerel içe aktarılan model: {fname}"
            }

            # Add to custom category
            for cat in self.catalog.get("categories", []):
                if cat.get("id") == "custom":
                    # Avoid duplicates
                    cat["models"] = [m for m in cat["models"] if m.get("filename") != fname]
                    cat["models"].append(model_info)
                    break

            self._save_catalog(self.catalog)
            self.catalog_updated.emit()
            return dst_path
        except Exception as e:
            print(f"[ModelManager] Error importing custom model: {e}")
            return None
