I'm really sorry about that\! That is incredibly frustrating. It's definitely a VS Code rendering issue, but it's easier if I just give you the raw text.

Here is the complete, final `README.md` file. You can copy this entire block and paste it directly into your `README.md` file in VS Code.

-----

# Classroom Compass - Classroom Person Segregation Model

This repository contains the code for the **Classroom Person Segregation Model**, a key microservice for the larger **Classroom Compass** project.

Classroom Compass is an AI-powered platform designed to provide real-time, non-intrusive feedback to teachers about student engagement. It helps teachers understand when a class is confused or disengaged without tracking individual students, allowing them to adjust their teaching style on the fly.

## Role in the Project Pipeline

This service is the **first stage** in a two-stage computer vision pipeline for the larger Classroom Compass project.

1.  **Stage 1: Segregation (This Service)**
    This service's FastAPI endpoint (`/detect_students/`) accepts a single, large image of a classroom. It uses a YOLOv8 segmentation model to detect every person, blur the background (optional), and save each detected student as a separate 300x300 cropped image in the `classroomouts/` directory.

2.  **Stage 2: Classification (External)**
    The cropped images from the `classroomouts/` directory are then intended to be sent (in a batch) to a second microservice, the [Classroom-Compass-Classifier](https://github.com/asifur8282/Classroom-Compass-Classifier). That service is responsible for classifying each individual student image as `focusing` or `distracted`.

3.  **Final Output:**
    The classifier service returns a final JSON object with aggregated counts (e.g., `{"focusing": 15, "distracted": 3}`), which is then consumed by the main Classroom Compass dashboard to provide real-time feedback to the teacher.

## 🎓 Classroom Person Segregation Models

This project detects and segments **students in classroom images** using **YOLOv8 segmentation**.
It blurs the background ( or choose no blur model ) while keeping each person sharp and saves them as cropped images.
Built with **FastAPI** for easy API integration.

## 🚀 Features

  * Detects all people in a classroom image using **YOLOv8x-seg**.
  * Blurs the background while keeping students in focus.
  * Crops and saves each student into a square image.
  * Provides an easy-to-use **FastAPI endpoint** for uploading and processing images.

-----

## 🛠️ Installation & Running

You have two options to run this project: **Docker (Recommended)** or **Manual (Local)**.

### Option 1: Run with Docker (Recommended)

This is the easiest and most reliable method. It builds the application inside a container with all dependencies and hardware optimizations handled for you.

#### Step 1: Check Your Hardware (CPU vs. NVIDIA GPU)

This project can run on a standard CPU or be significantly accelerated by an NVIDIA GPU.

  * **For CPU-Only Users:** You can skip this step and go directly to Step 2.

  * **For NVIDIA GPU Users:** To use your GPU, you must find your CUDA version. Open your terminal (CMD or PowerShell) and run:

    ```bash
    nvidia-smi
    ```

    Look at the `CUDA Version` in the top-right corner.

      * If your CUDA version is `12.1` or higher, you will use the `cu121` build tag.
      * If your CUDA version is `11.8` (or `11.9`, `12.0`), you will use the `cu118` build tag.

#### Step 2: Build the Docker Image

Navigate to the project's root directory in your terminal and run *one* of the following commands:

  * **To build for CPU (default):**

    ```bash
    docker build -t segregation-model .
    ```

  * **To build for your NVIDIA GPU (example for CUDA 12.1):**

    ```bash
    docker build --build-arg PYTORCH_TARGET=cu121 -t segregation-model-gpu .
    ```

    *(Note: The GPU build takes 15-20 minutes as it installs large CUDA libraries).*

#### Step 3: Run the Docker Container

This is the most important step. We will use a **volume mount** (`-v`) to connect a folder on your computer (the "host") to the output folder *inside* the container. This ensures your segregated images are saved directly to your local machine, not hidden inside the container.

  * **To run the CPU container:**
    This command maps your local `D:\My-Outputs` folder to the container's output directory. You can change the `D:\My-Outputs` path to any folder you want.

    ```bash
    docker run -d -p 8000:8000 --name student-segregator \
    -v "D:\My-Outputs:/app/classroomouts" \
    segregation-model
    ```

    *(Note: If not on Windows, change the path format, e.g., `-v "/home/user/my-outputs:/app/classroomouts"`)*

  * **To run the GPU container:**
    This command does the same thing but adds the `--gpus all` flag to give the container access to your NVIDIA GPU.

    ```bash
    docker run -d -p 8000:8000 --gpus all --name student-segregator-gpu \
    -v "D:\My-Outputs:/app/classroomouts" \
    segregation-model-gpu
    ```

#### Step 4: Test the Server

Your server is now running\! Proceed to the [**Usage**](#-usage) section to test it with `curl`. The output images will appear in the local folder you specified (e.g., `D:\My-Outputs`).

-----

### Option 2: Manual Local Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/asifur8282/Classroom-Person-Segregation-Model.git
    cd Classroom-Person-Segregation-Model
    ```

2.  Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    ```

    **Activate the environment:**

    ```bash
    source venv/Scripts/activate    # On Linux/Mac/Git Bash
    venv\Scripts\activate.bat       # On Windows CMD
    .\venv\Scripts\Activate.ps1     # On Windows PowerShell (you may need to set execution policy)
    ```

3.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  Start the FastAPI server:

      * **For the Blur Model:**
        ```bash
        python body_lang_3.py
        ```
      * **For the No Blur Model:**
        ```bash
        python students_no_blur_final.py
        ```

    By default, it runs on `http://localhost:8000`.

-----

## 📤 Usage

Once your server is running (either via Docker or Manually), you can test it.

### Upload an Image

  * **Using PowerShell (Windows):**
    *(This example uses an image from the `assets` folder)*

    ```bash
    curl.exe -X POST -F "file=@assets\classroom_sample.jpg" http://localhost:8000/detect_students/
    ```

  * **Using Git Bash / Linux / Mac:**

    ```bash
    curl -X POST -F "file=@assets/classroom_sample.jpg" http://localhost:8000/detect_students/
    ```

### Response

The server will return a JSON object with the total student count.

```json
{
  "total_students": 5
}
```

### Output

  * **If using Docker:** Cropped student images are saved to the local folder you specified in your `docker run` command (e.g., `D:\My-Outputs`).
  * **If running manually:** Cropped student images are saved in the `classroomouts/` directory within the project.

-----

## 📂 Example

### For Blur Model

Input Classroom Image ⬇️

\<img src="assets/classroom\_sample.jpg" width="500" alt="Classroom Example"/\>

Output (segregated students with blurred background) ⬇️

\<img src="assets/output.jpg" width="800" alt="Output Example"/\>
<br>
Command Prompt Output <br>
\<img src="assets/output\_cmd.jpg" width="800" alt="Output Example"/\>

-----

### For No Blur Model

Input Classroom Image ⬇️ <br>
<br>
\<img src="assets/sample.jpg" width="500" alt="Classroom Example"/\>

Output (segregated students) ⬇️

\<img src="assets/output\_no\_blur.jpg" width="800" alt="Output Example"/\>
<br>
Command Prompt Output <br>
\<img src="assets/no\_blur\_cmd.jpg" width="800" alt="Output Example"/\>

-----

## ⚡ Tech Stack

  * [Python](https://www.python.org/)
  * [OpenCV](https://opencv.org/)
  * [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
  * [FastAPI](https://fastapi.tiangolo.com/)
  * [Uvicorn](https://www.uvicorn.org/)

-----

## 🧭 Choosing PYTORCH\_TARGET & Efficient Deployment

This repository's `Dockerfile` supports selecting the PyTorch wheel at build time via the build-arg `PYTORCH_TARGET`. The goal is to produce images that run efficiently on the target machine (CPU or NVIDIA GPU), and to avoid installing the wrong or heavy PyTorch binary.

### Quick guide

  * **Build for CPU (default):**

    ```bash
    docker build -t segregation-model .
    ```

  * **Build for NVIDIA GPU with CUDA 11.8:**

    ```bash
    docker build --build-arg PYTORCH_TARGET=cu118 -t segregation-model-gpu .
    ```

  * **Build for NVIDIA GPU with CUDA 12.1:**

    ```bash
    docker build --build-arg PYTORCH_TARGET=cu121 -t segregation-model-gpu .
    ```

### Notes and tips for choosing the right target

  * If the host has NVIDIA GPUs and drivers installed, prefer a matching CUDA wheel (e.g. `cu118`, `cu121`). Installing a CPU-only wheel on a GPU host will still run but will not take advantage of GPU acceleration.
  * To determine the correct CUDA target, check the host NVIDIA driver/CUDA compatibility. If unsure, test `cu118` or consult the PyTorch install selector: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

### Efficiency recommendations

  * Keep `requirements.txt` free of `torch`/`torchvision` so the Docker build installs the correct wheel for the target CPU/GPU.
  * If you prefer faster builds, remove or comment out the model preload step in the `Dockerfile`:
    ```dockerfile
    # RUN python -c "from ultralytics import YOLO; YOLO('yolov8x-seg.pt')"
    ```
    Let the container download the model on first run instead.

-----

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

-----

## 🙌 Acknowledgements

  * [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for object detection and segmentation.
  * [FastAPI](https://fastapi.tiangolo.com/) for creating a lightweight and fast API.
