import builtins

import pytest

from object_detector import _load_model


def test_missing_yolov5_explains_how_to_install(monkeypatch):
    """yolov5 is an optional extra, so its absence must produce an actionable
    message rather than a bare ImportError in the middle of the page."""
    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "yolov5":
            raise ImportError("No module named 'yolov5'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    _load_model.cache_clear()

    with pytest.raises(RuntimeError, match="requirements-optional.txt"):
        _load_model("yolov5s")

    _load_model.cache_clear()
