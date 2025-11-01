FROM python:3.11-slim

# Allow selecting CPU or CUDA wheel at build time. Usage example:
# docker build --build-arg PYTORCH_TARGET=cu118 -t segregation-model .
ARG PYTORCH_TARGET=cpu
ENV PYTORCH_TARGET=${PYTORCH_TARGET}

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install non-torch requirements first (filter out torch/torchvision so we
# can install the correct wheels below based on PYTORCH_TARGET).
RUN grep -v -E '^(torch|torchvision)(==|$)' requirements.txt > requirements_no_torch.txt || true \
    && pip install --no-cache-dir -r requirements_no_torch.txt

# Install torch + torchvision according to the build arg. Supported values:
#  - cpu    -> CPU wheels
#  - cu118  -> CUDA 11.8 wheels
#  - cu121  -> CUDA 12.1 wheels
# If an unknown value is provided we default to CPU wheels.
RUN set -eux; \
    if [ "$PYTORCH_TARGET" = "cpu" ]; then \
        pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu; \
    elif [ "$PYTORCH_TARGET" = "cu118" ]; then \
        pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu118; \
    elif [ "$PYTORCH_TARGET" = "cu121" ]; then \
        pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121; \
    else \
        echo "Unknown PYTORCH_TARGET=$PYTORCH_TARGET; defaulting to CPU wheels"; \
        pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu; \
    fi

COPY . .


RUN python -c "from ultralytics import YOLO; YOLO('yolov8x-seg.pt')"

EXPOSE 8000

CMD ["uvicorn", "students_no_blur_final:app", "--host", "0.0.0.0", "--port", "8000"]
