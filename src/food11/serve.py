from __future__ import annotations

import io
import os

import mlflow
import numpy as np
import mlflow.pyfunc
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from torchvision import transforms


MODEL_NAME = "food11"
MODEL_ALIAS = "champion"

TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

CATEGORIES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

IMAGE_SIZE = 224

app = FastAPI(
    title="Food-11 Classification API",
    version="1.0.0",
)


transform = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


mlflow.set_tracking_uri(TRACKING_URI)

model = mlflow.pyfunc.load_model(
    "models:/food11@champion"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image.",
        )

    try:
        contents = await file.read()

        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read image: {exc}",
        ) from exc

    input_array = (
        transform(image)
        .unsqueeze(0)
        .numpy()
        .astype(np.float32)
    )

    try:
        predictions = model.predict(input_array)

        logits = np.asarray(predictions)

        # Handle a possible batch dimension.
        if logits.ndim == 1:
            logits = logits.reshape(1, -1)

        # Softmax using NumPy.
        exp_logits = np.exp(
            logits - np.max(logits, axis=1, keepdims=True)
        )

        probabilities = exp_logits / np.sum(
            exp_logits,
            axis=1,
            keepdims=True,
        )

        predicted_index = int(
            np.argmax(probabilities, axis=1)[0]
        )

        confidence = float(
            probabilities[0, predicted_index]
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc

    return {
        "category": CATEGORIES[predicted_index],
        "confidence": confidence,
    }