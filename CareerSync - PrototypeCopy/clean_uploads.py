import os

UPLOAD_FOLDER = 'uploads'

def clean_uploads():
    if not os.path.exists(UPLOAD_FOLDER):
        print("Uploads folder does not exist.")
        return

    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        print("Uploads folder is already empty.")
        return

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

    print("All uploaded files deleted successfully.")

if __name__ == "__main__":
    clean_uploads()
