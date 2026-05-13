import os
import json
from app.pipeline.pipeline import ProcessingPipeline
from app.core.data_file import DataFile

def setup_test_environment():
    os.makedirs("../data/input", exist_ok=True)
    os.makedirs("../data/output", exist_ok=True)

def create_mock_files():
    """Generate dummy data files for testing."""
    # 1. Create a valid CSV file
    with open("../data/input/test_users.csv", "w", encoding="utf-8") as f:
        f.write("id,name,role\n1,Alice,Admin\n2,Bob,User")
        
    # 2. Create a valid JSON file
    with open("../data/input/test_config.json", "w", encoding="utf-8") as f:
        json.dump({"status": "active", "version": 1.0}, f)

    # 3. Create an unsupported file type
    with open("../data/input/test_image.png", "w", encoding="utf-8") as f:
        f.write("fake_image_data")

def run_tests():
    setup_test_environment()
    create_mock_files()
    # Initialize the pipeline
    pipeline = ProcessingPipeline()
    print("=== STARTING PIPELINE TESTS ===")
    
    # Test Case 1: Valid CSV file processing
    print("\n--- Test Case 1: Valid CSV ---")
    #data_file = DataFile("../data/input/test_users.csv")
    csv_success = pipeline.run("../data/input/test_users.csv")
    print(f"Result Status: {csv_success}")
    
    # Test Case 2: Valid JSON file processing
    print("\n--- Test Case 2: Valid JSON ---")
    json_success = pipeline.run("../data/input/test_config.json")
    print(f"Result Status: {json_success}")
    
    # Test Case 3: Unsupported File Extension (Should fail gracefully)
    print("\n--- Test Case 3: Unsupported Extension (.png) ---")
    png_success = pipeline.run("data/input/test_image.png")
    print(f"Result Status: {png_success} (Expected: False)")

    # 4. Verify Output Files Exist
    print("\n=== VERIFYING OUTPUT DIRECTORY ===")
    output_files = os.listdir("../data/output")
    print(f"Files found in data/output: {output_files}")

if __name__ == "__main__":
    run_tests()
