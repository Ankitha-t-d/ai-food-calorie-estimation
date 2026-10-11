import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "food20dataset"
    )
)

from database import save_meal, get_connection
from nutrition import calculate_nutrition
from user_database import get_user


USER_ID = 1


# -----------------------------------------
# ADD MEAL
# Calculate nutrition and save exactly once
# -----------------------------------------
def add_meal(food, quantity):

    nutrition = calculate_nutrition(
        food,
        quantity
    )

    if nutrition is None:
        print(
            f"Nutrition information not found for: {food}"
        )
        return None

    # Save the meal exactly once.
    save_meal(
        food,
        quantity,
        nutrition["weight"],
        nutrition["calories"],
        nutrition["protein"],
        nutrition["carbs"],
        nutrition["fat"]
    )

    return nutrition


# -----------------------------------------
# GET TODAY'S MEALS
# -----------------------------------------
def get_today_meals():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT *
            FROM meals
            WHERE meal_time IS NOT NULL
              AND DATE(meal_time) = DATE('now', 'localtime')
            ORDER BY meal_time DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        meals = [
            dict(zip(columns, row))
            for row in rows
        ]

        cursor.close()

        return meals

    finally:
        connection.close()


# -----------------------------------------
# DAILY CALORIE TARGET
# -----------------------------------------
def get_daily_calorie_target():

    user = get_user(USER_ID)

    if user is None:
        return 2000.0

    calorie_target = user.get(
        "daily_calorie_target"
    )

    if calorie_target is None:
        return 2000.0

    return float(calorie_target)


# -----------------------------------------
# DAILY SUMMARY
# -----------------------------------------
def get_daily_summary():

    meals = get_today_meals()

    daily_target = get_daily_calorie_target()

    total_calories = sum(
        float(meal.get("calories") or 0)
        for meal in meals
    )

    total_protein = sum(
        float(meal.get("protein") or 0)
        for meal in meals
    )

    total_carbs = sum(
        float(meal.get("carbs") or 0)
        for meal in meals
    )

    total_fat = sum(
        float(meal.get("fat") or 0)
        for meal in meals
    )

    calories_remaining = (
        daily_target - total_calories
    )

    percentage = (
        (total_calories / daily_target) * 100
        if daily_target > 0
        else 0
    )

    return {
        "calories": round(total_calories, 2),
        "protein": round(total_protein, 2),
        "carbs": round(total_carbs, 2),
        "fat": round(total_fat, 2),
        "remaining": round(calories_remaining, 2),
        "percentage": round(percentage, 2),
        "target": daily_target,
        "meals": meals
    }


# -----------------------------------------
# DISPLAY SUMMARY
# -----------------------------------------
def display_summary():

    summary = get_daily_summary()

    print("\n")
    print("=" * 55)
    print("          FOOD20 DAILY NUTRITION SUMMARY")
    print("=" * 55)

    print(
        f"Calories       : {summary['calories']:.1f} kcal"
    )

    print(
        f"Protein        : {summary['protein']:.1f} g"
    )

    print(
        f"Carbohydrates  : {summary['carbs']:.1f} g"
    )

    print(
        f"Fat            : {summary['fat']:.1f} g"
    )

    print(
        f"Calories Left  : {summary['remaining']:.1f} kcal"
    )

    print(
        f"Daily Target   : {summary['target']:.0f} kcal"
    )

    print(
        f"Target Used    : {summary['percentage']:.1f}%"
    )

    print("\nMEAL-WISE BREAKDOWN")
    print("-" * 55)

    for index, meal in enumerate(
        summary["meals"],
        start=1
    ):

        print(
            f"{index}. "
            f"{meal.get('meal_time')} | "
            f"{meal.get('food')} | "
            f"{meal.get('quantity')} serving(s) | "
            f"{float(meal.get('calories') or 0):.1f} kcal | "
            f"Fat: {float(meal.get('fat') or 0):.1f} g"
        )

    print("=" * 55)