import os
import cv2
import numpy as np
from ultralytics import YOLO
from fastapi import FastAPI, File, UploadFile
import uvicorn
import logging
import shutil

# --- Setup and Initialization ---

# Initialize a logger for better debugging and info messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load a pre-trained YOLOv8x-seg model that supports segmentation
try:
    # Ensure this model is downloaded and in your directory
    model = YOLO('yolov8x-seg.pt')
    logger.info("YOLOv8x-seg model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    exit()

# Initialize the FastAPI application
app = FastAPI()

# --- Main Logic Function ---

def process_students_with_yolo(image_data: np.ndarray, output_dir: str, start_index: int = 0):
    """
    Detects students in an image using YOLOv8, counts them,
    and saves square crops of each detected student with a blurred background.
    
    Args:
        image_data (np.ndarray): The image data as a NumPy array.
        output_dir (str): The directory to save the cropped images.
        start_index (int): The starting index for naming cropped student images.
        
    Returns:
        int: The number of students detected in this image.
    """
    # Run inference with tuned parameters for better separation
    results = model(image_data, iou=0.3, conf=0.6, verbose=False)

    student_count = 0
    person_class_id = 0  # COCO class for 'person'
    
    for r in results:
        boxes = r.boxes
        masks = r.masks
        
        # Check if masks exist for this result object
        if masks is None:
            logger.warning("No segmentation masks found for the detected objects. Saving unblurred images.")
            continue
            
        for i, box in enumerate(boxes):
            if int(box.cls[0]) == person_class_id:
                student_count += 1

                x1, y1, x2, y2 = [int(val) for val in box.xyxy[0]]
                
                # --- CORRECTED BLURRING AND CROPPING LOGIC ---
                try:
                    # Get the mask for the current detected person
                    mask_data = masks.data[i].cpu().numpy()
                    
                    # Create a blurred version of the entire original image
                    blurred_image = cv2.GaussianBlur(image_data, (99, 99), 0)
                    
                    # Resize the mask to the original image dimensions
                    mask_resized = cv2.resize(mask_data, (image_data.shape[1], image_data.shape[0]))
                    
                    # Ensure mask is in the correct format (single channel)
                    mask_resized = mask_resized > 0.5  # Convert to boolean mask
                    mask_3_channel = np.stack([mask_resized, mask_resized, mask_resized], axis=2)

                    # Use the mask to combine the sharp foreground and blurred background
                    final_image = np.where(mask_3_channel, image_data, blurred_image)
                    
                except Exception as e:
                    logger.warning(f"Failed to apply blur mask for student {student_count}: {e}. Saving unblurred image.")
                    final_image = image_data

                # --- NOW CROP THE FINAL IMAGE ---
                # Calculate the crop dimensions
                w = x2 - x1
                square_side = w + 20
                
                new_x1 = max(0, x1 - 10)
                new_y1 = max(0, y1)
                new_x2 = min(final_image.shape[1], new_x1 + square_side)
                new_y2 = min(final_image.shape[0], new_y1 + square_side)
                
                final_width = new_x2 - new_x1
                final_height = new_y2 - new_y1
                
                if final_width > final_height:
                    new_x2 = new_x1 + final_height
                else:
                    new_y2 = new_y1 + final_width
                
                # Crop the final image
                cropped_student = final_image[new_y1:new_y2, new_x1:new_x2]
                
                # Resize the crop to a standard size
                final_resized = cv2.resize(cropped_student, (300, 300), interpolation=cv2.INTER_AREA)

                # Save the final image
                image_index = start_index + student_count
                output_path = os.path.join(output_dir, f'student_{image_index:03d}.jpg')
                cv2.imwrite(output_path, final_resized)
                logger.info(f"Saved student crop to {output_path}")

    return student_count

# --- FastAPI Endpoint Definition ---

@app.post("/detect_students/")
async def detect_students_api(file: UploadFile = File(...)):
    """
    API endpoint to detect students in an uploaded image.
    
    Args:
        file (UploadFile): The image file uploaded via the request.
        
    Returns:
        dict: A dictionary containing the total number of students detected.
    """
    try:
        output_directory = "classroomouts"

        # Ensure the output directory exists (but don't delete it)
        os.makedirs(output_directory, exist_ok=True)

        # Read the uploaded file
        file_bytes = await file.read()

        # Convert bytes to NumPy array
        np_array = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("Failed to decode image from uploaded file.")
            return {"error": "Failed to decode image."}

        logger.info(f"Received and decoded image: {file.filename}")

        # Count existing student images to avoid overwriting
        existing_files = [
            f for f in os.listdir(output_directory)
            if f.startswith("student_") and f.endswith(".jpg")
        ]
        existing_count = len(existing_files)

        # Process the image and get the student count
        student_count = process_students_with_yolo(
            image, output_directory, start_index=existing_count
        )

        logger.info(f"Processed {file.filename}. Detected {student_count} students.")

        return {"total_students": student_count}

    except Exception as e:
        logger.error(f"An error occurred during processing: {e}", exc_info=True)
        return {"error": "Internal server error. Please check the logs."}

# --- Uvicorn Entry Point (for local development) ---

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
