supported_file = [".csv", ".txt", ".json"]

def is_supported_file(file_path: str) -> bool:
    return any(file_path.endswith(ext) for ext in supported_file)