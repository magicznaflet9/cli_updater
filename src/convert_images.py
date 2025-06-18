import os
import shutil
import subprocess


def convert_images_to_webp(source_folder, target_folder):
    """
    Convert all images in source_folder to .webp (except .gif), 
    and save them in a new folder under target_base_path.
    If the target folder exists, it will be replaced.
    Uses ImageMagick's `convert` command for conversion.
    """
    if not os.path.isdir(source_folder):
        print(f"Source folder does not exist: {source_folder}")
        return

    # Remove target folder if it exists
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)
    os.makedirs(target_folder, exist_ok=True)

    for filename in os.listdir(source_folder):
        src_path = os.path.join(source_folder, filename)
        if not os.path.isfile(src_path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext == ".gif":
            # Copy GIFs as-is
            shutil.copy2(src_path, os.path.join(target_folder, filename))
        else:
            webp_name = os.path.splitext(filename)[0] + ".webp"
            target_path = os.path.join(target_folder, webp_name)
            try:
                subprocess.run(
                    ["magick", src_path, target_path],
                    check=True
                )
            except Exception as e:
                print(f"Failed to convert {filename} using ImageMagick: {e}")

    print(f"Images converted and saved to {target_folder}")

if __name__ == "__main__":
    # Example usage:
    convert_images_to_webp("/Users/zofiabochenek/Desktop/cli_updater/temp/66870/1724639/images", "/Users/zofiabochenek/Desktop/cli_updater/temp/images")
    pass
