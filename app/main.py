# from app.core.data_file import DataFile
# from app.processors.csv_processor import CSVProcessor
# from app.processors.txt_processor import TXTProcessor
# from app.processors.json_processor import JsonProcessor
from app.monitoring.monitor import FileMonitor


# def get_processor(file_type: str):
#     if file_type == "csv":
#         return CSVProcessor()
#     elif file_type == "txt":
#         return TXTProcessor()
#     elif file_type == "json":
#         return JsonProcessor()
#     else:
#         raise ValueError('Unsupported file')
# def run(file_path: str):
#     data_file = DataFile(file_path)
#     metadata = data_file.get_metadata()

#     print(f"[INFO] Processing file: {metadata}")

#     processor = get_processor(metadata["type"])
#     data = processor.load(file_path)
#     processed_data = processor.process(data)

#     output_path = f"data/output/processoed_{metadata['name']}"
#     processor.save(processed_data, output_path)

#     print(f"[SUCCESS] Saved to {output_path}")

def main():
    monitor = FileMonitor("data/input")
    print("[INFO] Starting file monitor...")
    monitor.start()
if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     # run("data/input/sample.txt")
#     monitor = FileMonitor("data/input")
#     print("[INFO] Starting file monitor...")
#     monitor.start()




