def save_file(file, destination_path):
    with open(destination_path, "wb") as f:
        f.write(file)
