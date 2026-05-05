import os


DEFAULT_VIDEO = os.path.join("Dataset", "VIRAT_S_010204_05_000856_000890.mp4")


def get_video_path(input_path=None):
    if input_path:
        return input_path

    default_path = os.path.abspath(DEFAULT_VIDEO)
    if os.path.exists(default_path):
        return default_path

    dataset_dir = os.path.abspath("Dataset")
    if os.path.isdir(dataset_dir):
        for filename in os.listdir(dataset_dir):
            if filename.lower().endswith(".mp4"):
                return os.path.join(dataset_dir, filename)

    return default_path