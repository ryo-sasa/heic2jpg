import os
import pyheif
from PIL import Image, UnidentifiedImageError
from datetime import datetime
from tqdm import tqdm

def convert_all_images_to_jpg(input_folder):
    # 出力フォルダを作成（YYYYMMDD形式）
    today_str = datetime.now().strftime("%Y%m%d")
    output_folder = os.path.join("output", today_str)
    os.makedirs(output_folder, exist_ok=True)

    # ログファイル作成
    log_path = os.path.join(output_folder, "conversion_log.txt")
    log_lines = []

    supported_extensions = [".png", ".bmp", ".tiff", ".gif", ".heic", ".jpeg", ".jpg"]
    files = [f for f in os.listdir(input_folder) if os.path.splitext(f)[1].lower() in supported_extensions]

    for filename in tqdm(files, desc="Converting images"):
        ext = os.path.splitext(filename)[1].lower()
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + ".jpg"
        output_path = os.path.join(output_folder, output_filename)

        try:
            if ext == ".heic":
                heif_file = pyheif.read(input_path)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
            else:
                image = Image.open(input_path)

            # 透過画像を白背景に合成
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            image.save(
                output_path,
                "JPEG",
                quality=95,
                optimize=True,
                subsampling=0
            )

            # 写真情報ログ
            info = f"[SUCCESS] {filename} → {output_filename}\n" \
                    f" - Size: {image.size[0]}x{image.size[1]}\n" \
                    f" - Format: {ext}\n" \
                    f" - Output: {output_path}\n"
            log_lines.append(info)

        except (UnidentifiedImageError, Exception) as e:
            error_log = f"[FAILED] {filename}: {e}\n"
            log_lines.append(error_log)

    # ログファイルに出力
    with open(log_path, "w", encoding="utf-8") as f:
        f.writelines(log_lines)

    print(f"\n📝 変換完了！ログファイル: {log_path}")

# 使用例
input_dir = "input_images"  # 入力フォルダ
convert_all_images_to_jpg(input_dir)