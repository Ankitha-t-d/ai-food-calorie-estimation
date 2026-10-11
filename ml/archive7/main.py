import torch
import torch.nn as nn

from torchvision import transforms, models
from PIL import Image

from fastapi import FastAPI, File, UploadFile, Form, HTTPException

import io

from nutrition import calculate_nutrition
from daily_tracker import add_meal, get_daily_summary


# --------------------------------
# FastAPI
# --------------------------------

app = FastAPI(
    title="Food Calorie Estimation API",
    description="AI-powered Indian food calorie estimation system",
    version="1.0"
)


# --------------------------------
# Device
# --------------------------------

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# --------------------------------
# Load trained model
# --------------------------------

MODEL_PATH = r"C:\Users\nandi\Downloads\archive (7)\backend\food20_efficientnet.pth"

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

classes = checkpoint["classes"]

model = models.efficientnet_b0(
    weights=None
)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)
model.eval()


# --------------------------------
# Image preprocessing
# --------------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------
# Home
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "Food Calorie Estimation API is running"
    }


# --------------------------------
# Health check
# --------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# --------------------------------
# Predict + Nutrition + Save
# --------------------------------

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    quantity: float = Form(...)
):

    # Check quantity
    if quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0."
        )


    # Read image
    image_bytes = await file.read()

    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid image file."
        )


    # Preprocess
    image_tensor = transform(image)

    image_tensor = image_tensor.unsqueeze(0)

    image_tensor = image_tensor.to(device)


    # --------------------------------
    # ML prediction
    # --------------------------------

    with torch.no_grad():

        output = model(image_tensor)

        probabilities = torch.softmax(
            output,
            dim=1
        )

        confidence, predicted = torch.max(
            probabilities,
            1
        )


    predicted_class = classes[
        predicted.item()
    ]

    confidence_value = (
        confidence.item() * 100
    )


    # --------------------------------
    # Nutrition calculation
    # --------------------------------

    # Nutrition calculation

    nutrition = add_meal(
        predicted_class,
        quantity
    )

    if nutrition is None:
        raise HTTPException(
            status_code=404,
            detail="Nutrition information not found."
        )


    # --------------------------------
    # Response
    # --------------------------------

    return {

        "food": predicted_class,

        "confidence": round(
            confidence_value,
            2
        ),

        "quantity": quantity,

        "weight": nutrition["weight"],

        "calories": nutrition["calories"],

        "protein": nutrition["protein"],

        "carbs": nutrition["carbs"],

        "fat": nutrition["fat"]

    }


# --------------------------------
# Daily Summary
# --------------------------------

@app.get("/daily-summary")
def daily_summary():
    from daily_tracker import get_today_meals, get_daily_calorie_target

    meals = get_today_meals()
    target = get_daily_calorie_target()

    calories = sum(float(m["calories"] or 0) for m in meals)
    protein = sum(float(m["protein"] or 0) for m in meals)
    carbs = sum(float(m["carbs"] or 0) for m in meals)
    fat = sum(float(m["fat"] or 0) for m in meals)

    return {
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "remaining": target - calories,
        "percentage": calories / target * 100 if target > 0 else 0,
        "target": target,
        "meals": meals
    }