import argparse
import os
from PIL import Image

def load_binary_from_file(filename="values.txt"):
  """Reads a text file and strips away any whitespace, spaces, or newlines."""
  if not os.path.exists(filename):
      raise FileNotFoundError(f"Error: The file '{filename}' was not found in this folder.")
      
  with open(filename, "r", encoding="utf-8") as f:
      content = f.read()
  
  return "".join([c for c in content if c in ("0", "1")])
  
def custom_binary_to_image(scale_factor, input_file="values.txt", output_path="output.png"):
  binary_str = load_binary_from_file(input_file)
  
  if len(binary_str) < 16:
      raise ValueError("Error: Data stream is too short to contain width and height headers.")
  
  width_bits = binary_str[0:8]
  height_bits = binary_str[8:16]
  
  width = int(width_bits, 2)
  height = int(height_bits, 2)
  
  print(f"Loaded '{input_file}' successfully.")
  print(f"Detected Dimensions: {width}x{height} pixels")
  
  pixel_bits = binary_str[16:]
  expected_bits = width * height * 24
  
  if len(pixel_bits) < expected_bits:
      print(f"Warning: Expected {expected_bits} bits for pixels, but found {len(pixel_bits)} bits. Padding with black.")
      pixel_bits = pixel_bits.ljust(expected_bits, '0')
  elif len(pixel_bits) > expected_bits:
      print(f"Note: Extra bits detected ({len(pixel_bits) - expected_bits} bits). Truncating to fit dimensions.")
      pixel_bits = pixel_bits[:expected_bits]
  
  rgb_pixels = []
  for i in range(0, len(pixel_bits), 24):
      chunk = pixel_bits[i:i+24]
      
      r = int(chunk[0:8], 2)
      g = int(chunk[8:16], 2)
      b = int(chunk[16:24], 2)
      
      rgb_pixels.append((r, g, b))
  
  img = Image.new("RGB", (width, height))
  img.putdata(rgb_pixels)
  
  new_width = width * scale_factor
  new_height = height * scale_factor
  scaled_img = img.resize((new_width, new_height), resample=Image.NEAREST)
  
  scaled_img.save(output_path)
  print(f"Success! Image saved to '{output_path}' ({new_width}x{new_height} pixels).")

if __name__ == "__main__":
parser = argparse.ArgumentParser(
    description="Convert a local text stream of binary data into an upscaled image."
)
parser.add_argument(
    "-s", "--scale", 
    type=int, 
    default=15, 
    help="Scale factor multiplier for the output image (default: 15)"
)
parser.add_argument(
    "-i", "--input", 
    type=str, 
    default="values.txt", 
    help="Input text file path (default: values.txt)"
)
parser.add_argument(
    "-o", "--output", 
    type=str, 
    default="decoded_output.png", 
    help="Output filename (default: decoded_output.png)"
)

args = parser.parse_args()

try:
    custom_binary_to_image(args.scale, args.input, args.output)
except Exception as e:
    print(e)
