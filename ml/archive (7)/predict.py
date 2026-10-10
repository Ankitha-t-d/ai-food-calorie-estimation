import torch
from daily_tracker import add_meal, display_summary
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

from nutrition import calculate_nutrition


# -----------------------------
# Device
# -----------------------------
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# -----------------------------
# Load trained model
# -----------------------------
checkpoint = torch.load(
    r"C:\Users\nandi\Downloads\archive (7)\food20dataset\food20_efficientnet.pth",
    map_location=device
)

classes = checkpoint["classes"]

model = models.efficientnet_b0(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)
model.eval()


# -----------------------------
# Image preprocessing
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# -----------------------------
# Image
# -----------------------------
image_path = "my_images/food1.jpg"

image = Image.open(image_path).convert("RGB")

image_tensor = transform(image)
image_tensor = image_tensor.unsqueeze(0)
image_tensor = image_tensor.to(device)


# -----------------------------
# Prediction
# -----------------------------
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


predicted_class = classes[predicted.item()]
confidence_value = confidence.item() * 100


# -----------------------------
# Display prediction
# -----------------------------
print("\nPrediction")
print("----------------------")
print("Food:", predicted_class)
print(f"Confidence: {confidence_value:.2f}%")


# -----------------------------
# Ask for quantity
# -----------------------------
while True:

    try:

        quantity = float(
            input("\nEnter number of servings/pieces: ")
        )

        if quantity <= 0:
            print("Quantity must be greater than 0.")
            continue

        break

    except ValueError:

        print("Please enter a valid number.")


# -----------------------------
# Calculate nutrition
# -----------------------------
nutrition = calculate_nutrition(
    predicted_class,
    quantity
)
# Save meal to MySQL
add_meal(
    predicted_class,
    quantity
)

# -----------------------------
# Display nutrition
# -----------------------------
print("\nNutrition Estimate")
print("----------------------")
print(f"Food             : {predicted_class}")
print(f"Quantity         : {quantity:g}")
print(f"Estimated Weight : {nutrition['weight']:.0f} g")
print(f"Confidence       : {confidence_value:.2f}%")
print(f"Calories         : {nutrition['calories']:.1f} kcal")
print(f"Protein          : {nutrition['protein']:.1f} g")
print(f"Carbs            : {nutrition['carbs']:.1f} g")
print(f"Fat              : {nutrition['fat']:.1f} g")
print("----------------------")
display_summary()