import tkinter as tk
from tkinter import filedialog, messagebox
from google.cloud import documentai_v1 as documentai
from PIL import Image, ImageTk, ImageDraw
import os

# Current location of main.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set up Google credentials
json_credentials = '' # Insert your JSON API key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(current_dir, json_credentials)

# Global variables to store bounding boxes and corresponding texts
bounding_boxes_with_text = []
tooltip = None

# Function to process the document using Google Document AI
def process_document_ai(image_path):
    project_id = 'htrengi'
    location = 'eu' 
    processor_id = ''  # Insert your processor ID
    api_endpoint = 'eu-documentai.googleapis.com' #workaround of american server endpoint being default in API

    client = documentai.DocumentProcessorServiceClient(client_options={"api_endpoint": api_endpoint})
    name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

    # Read the image file
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    # Create the raw document to send to the API
    raw_document = documentai.RawDocument(content=content, mime_type='image/jpeg')

    # Process the document
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)

    # Extract document text and bounding boxes
    document = result.document
    full_text = document.text
    bounding_boxes = []

    for page in document.pages:
        for paragraph in page.paragraphs:
            bbox = [(vertex.x, vertex.y) for vertex in paragraph.layout.bounding_poly.vertices]
            for text_segment in paragraph.layout.text_anchor.text_segments:
                segment_start = text_segment.start_index
                segment_end = text_segment.end_index
                segment_text = full_text[segment_start:segment_end]
                bounding_boxes.append((bbox, segment_text))

    return full_text, bounding_boxes

# Function to handle file selection and process the image
def select_file():
    global bounding_boxes_with_text, img_label, img, tooltip
    bounding_boxes_with_text = []  # Reset bounding boxes on new image
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*"))
    )

    if file_path:
        try:
            img = Image.open(file_path)
            original_size = img.size
            height_display = 1536
            width_display = 864
            img = img.resize((height_display, width_display))
            draw = ImageDraw.Draw(img)
            
            extracted_text, bounding_boxes = process_document_ai(file_path)

            for bbox, text in bounding_boxes:
                adjusted_bbox = [(x * (height_display / original_size[0]), y * (width_display / original_size[1])) for x, y in bbox]
                draw.polygon(adjusted_bbox, outline="red", width=2)
                bounding_boxes_with_text.append((adjusted_bbox, text))

            img_tk = ImageTk.PhotoImage(img)
            img_label.config(image=img_tk)
            img_label.image = img_tk
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, extracted_text)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process the image: {str(e)}")

# Function to detect mouse hover over bounding boxes and display the tooltip
def show_tooltip(event):
    global tooltip, bounding_boxes_with_text
    if tooltip:
        tooltip.destroy()  # Remove the existing tooltip
    for bbox, text in bounding_boxes_with_text:
        # Check if mouse is inside the bounding box
        if is_point_inside_polygon(event.x, event.y, bbox):
            # Offset the tooltip position by 10 pixels to the right and below the cursor
            tooltip = tk.Label(img_label, text=text, bg="yellow", relief=tk.SOLID, borderwidth=1)
            tooltip.place(x=event.x + 10, y=event.y + 10)
            return


# Utility function to check if a point is inside a polygon (bounding box)
def is_point_inside_polygon(x, y, polygon):
    n = len(polygon)
    inside = False
    px, py = x, y
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside

# Set up the GUI window
root = tk.Tk()
root.state('zoomed')
root.title("Document AI Image Processing")

# Set the window to full screen size without removing the title bar
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Create a canvas and scrollbar
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Upload button
upload_button = tk.Button(scrollable_frame, text="Select Image", command=select_file)
upload_button.pack(pady=20)

# Label to display the selected image
img_label = tk.Label(scrollable_frame)
img_label.pack(pady=10)
img_label.bind("<Motion>", show_tooltip)  # Bind mouse motion to show tooltips

# Text widget to display the result
result_text = tk.Text(scrollable_frame, wrap='word', width=200, height=10)
result_text.pack(pady=20)

# Start the GUI event loop
root.mainloop()