# from __future__ import division
# import os
# from PIL import Image
# import numpy as np
# from util import load_image, array2PIL
# from scipy.stats import percentileofscore

# def TEST(image_path, saliency_map_path):
#     # Save the plot and the map
#     if not os.path.exists('static/default_output'):
#         os.makedirs('static/default_output')

#     output_directory = 'static/default_output'  # Default output directory

#     # Compression and processing settings
#     jpeg_compression = 50
#     find_best = 1
#     threshold_pct = 20
#     use_convert = 0
#     model = 3
#     print_metrics = 0  # Set to 1 to print quality metrics


#     def make_quality_compression(original, sal):
#         if print_metrics:
#             print(f"Processing image: {image_path}")

#         # Resize saliency map if needed
#         if original.size != sal.size:
#             sal = sal.resize(original.size)

#         sal_arr = np.asarray(sal)
#         img_qualities = []
#         quality_steps = [i * 10 for i in range(1, 11)]

#         # Create temporary directory for intermediate images
#         os.makedirs('temp_xxx_yyy', exist_ok=True)

#         for q in quality_steps:
#             name = 'temp_xxx_yyy/temp_' + str(q) + '.jpg'
#             if use_convert:
#                 os.system(f'convert -colorspace sRGB -filter Lanczos -interlace Plane -type truecolor -quality {q} {image_path} {name}')
#             else:
#                 original.save(name, quality=q)
#             img_qualities.append(np.asarray(Image.open(name)))
#             os.remove(name)

#         os.rmdir('temp_xxx_yyy')

#         # Create a writable copy of the highest quality image
#         k = np.copy(img_qualities[-1])  # Make a writable copy of the highest quality
#         shape = k.shape

#         mx, mn = np.max(sal_arr), np.mean(sal_arr)
#         sal_flatten = sal_arr.flatten()

#         q_a = [np.percentile(sal_arr, j) for j in quality_steps]
#         low, high = 1, 9

#         # Adjust the quality for each pixel based on the model
#         for i in range(shape[0]):
#             for j in range(shape[1]):
#                 for l in range(shape[2]):
#                     ss = sal_arr[i, j]
#                     if model == 3:
#                         for index, q_i in enumerate(q_a):
#                             if ss < q_i: 
#                                 qq = index + 1
#                                 break
#                     else:
#                         raise Exception("Unknown model number")

#                     qq = min(max(qq, low), high)
#                     k[i, j, l] = img_qualities[qq][i, j, l]

#         # Save original image with JPEG compression
#         compressed = os.path.join(output_directory, f'original_compressed.jpg')
#         original.save(compressed, quality=jpeg_compression)

#         original_size = os.path.getsize(compressed)

#         out_img = array2PIL(k)

#         # Convert out_img to RGB if it is RGBA
#         if out_img.mode == 'RGBA':
#             out_img = out_img.convert('RGB')

#         # Save compressed image
#         if find_best:
#             out_name = os.path.join(output_directory, 'best_compressed.jpg')
#             for qual in range(90, 20, -1):
#                 out_img.save(out_name, quality=qual)
#                 current_size = os.path.getsize(out_name)
#                 if current_size <= original_size * (1 + threshold_pct / 100.0):
#                     if print_metrics:
#                         print(model, original_size, current_size, jpeg_compression, qual, '|')
#                     break
#             else:
#                 if print_metrics:
#                     print(model, original_size, current_size, jpeg_compression, qual, '|')
#         else:
#             final_quality = [100, 85, 65, 45]
#             for fq in final_quality:
#                 out_name = os.path.join(output_directory, f'compressed_{fq}.jpg')
#                 out_img.save(out_name, quality=fq)

#         return compressed, out_name



#     # Ensure the output directory exists
#     if not os.path.exists(output_directory):
#         os.makedirs(output_directory)

#     # Load the input image and saliency map
#     original = Image.open(image_path)
#     sal = Image.open(saliency_map_path)

#     # Process the image
#     compressed_image, best_compressed_image = make_quality_compression(original, sal)

#     # Optionally print out paths to the saved images
#     print(f"Original compressed image saved at: {compressed_image}")
#     print(f"Best compressed image saved at: {best_compressed_image}")
from __future__ import division
import os
from PIL import Image
import numpy as np
from util import load_image, array2PIL
from scipy.stats import percentileofscore
import io # <-- NEW: For in-memory file operations

def TEST(image_path, saliency_map_path):
    # Save the plot and the map
    if not os.path.exists('static/default_output'):
        os.makedirs('static/default_output')

    output_directory = 'static/default_output'  # Default output directory

    # Compression and processing settings
    jpeg_compression = 50
    find_best = 1
    threshold_pct = 20
    use_convert = 0
    model = 3
    print_metrics = 0  # Set to 1 to print quality metrics


    def make_quality_compression(original, sal):
        if print_metrics:
            print(f"Processing image: {image_path}")

        # Resize saliency map if needed
        if original.size != sal.size:
            sal = sal.resize(original.size)

        sal_arr = np.asarray(sal)
        img_qualities = []
        
        # ------------------- MODIFIED: Drastically Reduced Quality Steps -------------------
        # Reduced from 10 steps (10, 20, ..., 100) to 4 steps for speed
        quality_steps = [10, 40, 70, 100]

        # MODIFIED: In-Memory JPEG Generation
        for q in quality_steps:
            # Use an in-memory buffer instead of a file
            buffer = io.BytesIO() 
            original.save(buffer, format='JPEG', quality=q)
            buffer.seek(0)
            
            # Open the image from the buffer and convert to array
            img_qualities.append(np.asarray(Image.open(buffer)))
            buffer.close()
        # ------------------------------------------------------------------------------------

        # Create a writable copy of the highest quality image
        k = np.copy(img_qualities[-1]) 
        shape = k.shape

        mx, mn = np.max(sal_arr), np.mean(sal_arr)
        sal_flatten = sal_arr.flatten()

        # MODIFIED: Align Percentile Steps to the new 4 quality levels
        percentile_steps = [10, 40, 70, 100]
        q_a = [np.percentile(sal_arr, j) for j in percentile_steps]
        low, high = 0, len(quality_steps) - 1 # Adjust limits (0 to 3)

        # Adjust the quality for each pixel based on the model
        for i in range(shape[0]):
            for j in range(shape[1]):
                for l in range(shape[2]):
                    ss = sal_arr[i, j]
                    qq = high 
                    if model == 3:
                        for index, q_i in enumerate(q_a):
                            if ss < q_i: 
                                qq = index
                                break
                    else:
                        raise Exception("Unknown model number")

                    qq = min(max(qq, low), high)
                    k[i, j, l] = img_qualities[qq][i, j, l]

        # Save original image with JPEG compression
        compressed = os.path.join(output_directory, f'original_compressed.jpg')
        original.save(compressed, quality=jpeg_compression)

        original_size = os.path.getsize(compressed)

        out_img = array2PIL(k)

        # Convert out_img to RGB if it is RGBA
        if out_img.mode == 'RGBA':
            out_img = out_img.convert('RGB')

        # Save compressed image
        if find_best:
            out_name = os.path.join(output_directory, 'best_compressed.jpg')
            # ------------------- MODIFIED: Aggressive Quality Search Step --------------------
            # Checks fewer quality levels (90, 80, 70, etc.) for speed
            for qual in range(90, 20, -10):
                out_img.save(out_name, quality=qual)
                current_size = os.path.getsize(out_name)
                if current_size <= original_size * (1 + threshold_pct / 100.0):
                    if print_metrics:
                        print(model, original_size, current_size, jpeg_compression, qual, '|')
                    break
            # --------------------------------------------------------------------------------------
            else:
                if print_metrics:
                    print(model, original_size, current_size, jpeg_compression, qual, '|')
        else:
            final_quality = [100, 85, 65, 45]
            for fq in final_quality:
                out_name = os.path.join(output_directory, f'compressed_{fq}.jpg')
                out_img.save(out_name, quality=fq)

        return compressed, out_name


    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load the input image and saliency map
    original = Image.open(image_path)
    sal = Image.open(saliency_map_path)

    # Process the image
    compressed_image, best_compressed_image = make_quality_compression(original, sal)

    # Optionally print out paths to the saved images
    print(f"Original compressed image saved at: {compressed_image}")
    print(f"Best compressed image saved at: {best_compressed_image}")