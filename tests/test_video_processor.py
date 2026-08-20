from video_processor import cache_key


def test_cache_key_is_deterministic():
    assert cache_key("clip.mp4", 1024) == cache_key("clip.mp4", 1024)


def test_cache_key_is_stable_across_processes():
    """Regression: this used to be built on hash(), which Python salts per
    process, so a cached upload never resolved again after a restart.

    The pinned value is the contract -- changing it silently orphans every
    video already sitting in .cache_videos.
    """
    assert cache_key("clip.mp4", 1024) == "b5833a3472f18953"


def test_cache_key_varies_with_name_and_size():
    assert cache_key("a.mp4", 1) != cache_key("b.mp4", 1)
    assert cache_key("a.mp4", 1) != cache_key("a.mp4", 2)
