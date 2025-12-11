from PIL import Image
import os


def decompress_image(compressed_image_path, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load the compressed image
    compressed_image = Image.open(compressed_image_path)

    # Since we can't fully recover the original image from a lossy compression, we just save it back with maximum quality
    decompressed_image_path = os.path.join(output_directory, 'decompressed_image.jpg')

    # Save it with the best possible quality (maximum 100)
    compressed_image.save(decompressed_image_path, quality=100)

    print(f"Decompressed image saved at: {decompressed_image_path}")

    return decompressed_image_path 