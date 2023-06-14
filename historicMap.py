from PIL import Image, ImageDraw, ImageFont
import mysql.connector
import random
import os

# Define marker colors for each player
marker_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Example colors, add more as needed

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='drivebolt.asuscomm.cn',
    port=3306,
    user='python',
    password='$M1n1stry$!',
    database='player_data'  # Replace with the actual database name
)
cursor = conn.cursor()

# Retrieve player location data from the MySQL database
query = "SELECT player_id, x, z FROM player_movement ORDER BY timestamp ASC"
cursor.execute(query)
player_data = cursor.fetchall()
cursor.close()
conn.close()

# Get the absolute path of the image file
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "map.png")
# Load the game map image
map_image = Image.open(image_path)

# Calculate the dimensions of the output canvas to accommodate the map, grid, and legend
canvas_width = map_image.width + 400  # Increased width for the legend
canvas_height = map_image.height + 400

# Create a new image with the calculated dimensions
canvas_image = Image.new("RGB", (canvas_width, canvas_height), color=(255, 255, 255))
canvas_draw = ImageDraw.Draw(canvas_image)

# Calculate the top-left position to place the map image
map_position = ((canvas_width - map_image.width) // 2, (canvas_height - map_image.height) // 2)

# Paste the map image onto the canvas
canvas_image.paste(map_image, map_position)

# Create a drawing object to overlay markers, grid lines, and legend on the canvas
draw = ImageDraw.Draw(canvas_image)

# Initialize a dictionary to keep track of marker colors for each player
player_marker_colors = {}

# Map the player locations onto the canvas with separate marker colors and track their movement
for i, player in enumerate(player_data):
    player_id, x, z = player

    # Assign a random marker color for the player if not already assigned
    if player_id not in player_marker_colors:
        player_marker_colors[player_id] = random.choice(marker_colors)

    marker_color = player_marker_colors[player_id]

    # Map the coordinates to the canvas dimensions
    mapped_x = int((x + 3072) / 6144 * map_image.width) + map_position[0]
    mapped_y = int((3072 - (z - 0)) / 6144 * map_image.height) + map_position[1]

    # Draw a marker at the mapped position
    marker_size = 5
    draw.rectangle(((mapped_x - marker_size, mapped_y - marker_size),
                    (mapped_x + marker_size, mapped_y + marker_size)),
                   fill=marker_color)

    # Draw a line connecting the current position with the previous position (if applicable)
    if i > 0:
        prev_player_id, prev_x, prev_z = player_data[i - 1]
        prev_marker_color = player_marker_colors[prev_player_id]
        prev_mapped_x = int((prev_x + 3072) / 6144 * map_image.width) + map_position[0]
        prev_mapped_y = int((3072 - (prev_z - 0)) / 6144 * map_image.height) + map_position[1]
        draw.line([(prev_mapped_x, prev_mapped_y), (mapped_x, mapped_y)], fill=prev_marker_color, width=2)

# Create a "test" coordinate at (x=-3071, z=3071)
test_x = -3071
test_z = 3071
test_color = (0, 0, 0)  # Black color for the test marker

# Map the test coordinate to the canvas dimensions
mapped_test_x = int((test_x + 3072) / 6144 * map_image.width) + map_position[0]
mapped_test_y = int((3072 - (test_z - 0)) / 6144 * map_image.height) + map_position[1]

# Draw a marker for the test coordinate
draw.rectangle(((mapped_test_x - marker_size, mapped_test_y - marker_size),
                (mapped_test_x + marker_size, mapped_test_y + marker_size)),
               fill=test_color)

# Define the font size for the legend text
font_size = 20  # Reduced font size for better readability

# Draw the legend for each player
legend_offset_x = map_position[0] + map_image.width + 20
legend_offset_y = map_position[1]
for i, player in enumerate(player_marker_colors):
    player_name = f"Player {player}"
    marker_color = player_marker_colors[player]
    draw.rectangle(((legend_offset_x, legend_offset_y + i * font_size),
                    (legend_offset_x + font_size, legend_offset_y + (i + 1) * font_size)),
                   fill=marker_color)
    draw.text((legend_offset_x + font_size * 1.5, legend_offset_y + i * font_size), player_name, fill=marker_color,
              font=ImageFont.truetype("arial.ttf", font_size))

# Draw the grid lines
grid_color = (128, 128, 128)  # Gray color for the grid lines
grid_spacing = 100  # Adjust the grid spacing as desired

for x in range(-3072, 3073, grid_spacing):
    mapped_x = int((x + 3072) / 6144 * map_image.width) + map_position[0]
    draw.line([(mapped_x, map_position[1]), (mapped_x, map_position[1] + map_image.height)], fill=grid_color, width=1)
    # Add grid square value at the top of the grid line
    grid_label = str(x)
    label_width, label_height = draw.textsize(grid_label, font=ImageFont.truetype("arial.ttf", 20))
    draw.text((mapped_x - label_width // 2, map_position[1] - label_height - 5), grid_label, fill=grid_color,
              font=ImageFont.truetype("arial.ttf", 20))

for z in range(-3072, 3073, grid_spacing):
    mapped_y = int((3072 - (z - 0)) / 6144 * map_image.height) + map_position[1]
    draw.line([(map_position[0], mapped_y), (map_position[0] + map_image.width, mapped_y)], fill=grid_color, width=1)
    # Add grid square value at the right of the grid line
    grid_label = str(z)
    label_width, label_height = draw.textsize(grid_label, font=ImageFont.truetype("arial.ttf", 20))
    draw.text((map_position[0] + map_image.width + 5, mapped_y - label_height // 2), grid_label, fill=grid_color,
              font=ImageFont.truetype("arial.ttf", 20))

# Display or save the mapped image
canvas_image.show()
canvas_image.save("mapped_players.png")
