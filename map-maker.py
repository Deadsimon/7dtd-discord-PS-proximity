from PIL import Image

# Paths to DTM and biomes images
dtm_path = r"C:\Users\Creep\OneDrive\Documents\GitHub\backupper\7daystodie-Bot-Prototype\dtm_out.png"
biomes_path = r"C:\Users\Creep\AppData\Roaming\7DaysToDie\GeneratedWorlds\Cuziti Valley\biomes.png"

# Load the DTM image
dtm_image = Image.open(dtm_path)

# Load the biomes image
biomes_image = Image.open(biomes_path)

# Check if the dimensions of both images match
if dtm_image.size != biomes_image.size:
    # Adjust the size or raise an error if the dimensions don't match
    raise ValueError("Dimensions of DTM and biomes images do not match")

# Create a blank image for the combined map
combined_map = Image.new("RGBA", dtm_image.size)

# Iterate over each pixel in the DTM image
for x in range(dtm_image.width):
    for y in range(dtm_image.height):
        # Get the intensity value from the DTM pixel
        dtm_pixel = dtm_image.getpixel((x, y))
        intensity = dtm_pixel[1]

        # Get the color values from the biomes pixel
        biomes_pixel = biomes_image.getpixel((x, y))
        color = biomes_pixel[:3]  # Use the RGB values, ignoring alpha

        # Combine the intensity and color values to create a new pixel
        combined_pixel = (color[0], color[1], color[2], intensity)

        # Set the combined pixel in the output image
        combined_map.putpixel((x, y), combined_pixel)

# Save the combined map
combined_map.save("combined_map.png")
