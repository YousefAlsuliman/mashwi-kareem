from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from different origins

data = None
data2 = pd.read_excel("اخر تحديث.xlsx")

# Cleanup data2 (drop unnecessary columns)
data2 = data2.drop(data2.columns[[4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17]], axis=1)

# Standardizing product names
name_replacements = {
    "Arais Laham عرايس لحم": "عرايس لحم Arayes Meat",
    "Kabab Chiken Sandwish ساندويش كباب دجاج": "ساندويتش كباب دجاج Chicken Kebab Sandwish",
    "Pizza With Jobon بتزا بالجبن": "بيتزا بالجبن Pizza With Cheese",
    "Arais Dajaj With Jobon عرايس دجاج بالجبن": "عرايس دجاج بالجبن Arais Chicken With Cheese",
    "Mshakal Laham مشكل لحم": "مشكل لحم Meat Mshakal",
    "Kabab Laham كباب لحم": "كباب لحم Meat Kebab",
    "حمص شمندر -Hummus Beetroot": "حمص شمندر Hummus Beetroot",
    "Muqlqal Lahm مقلقل لحم": "مقلقل لحم Muqalqal Lahm",
    "ريش لحم rysh lahm": "ريش لحم Lamb chops",
    "سندويش اوصال Awsal sandwich": "ساندويتش اوصال Awsal sandwich",
}
data2["name"] = data2["name"].replace(name_replacements)


@app.route("/upload", methods=["POST"])
def upload_file():
    global data
    if "file" not in request.files:
        return jsonify({"error": "يرجى تحديد ملف لتحميله!"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "لم يتم اختيار أي ملف!"}), 400

    try:
        data = pd.read_csv(file)
        unique_products = data["المنتج"].unique().tolist()
        return jsonify({"products": unique_products})
    except Exception as e:
        return jsonify({"error": f"خطأ أثناء تحميل الملف: {str(e)}"}), 500


@app.route("/calculate", methods=["GET"])
def calculate_recipe():
    global data
    if data is None:
        return jsonify({"error": "يرجى تحميل ملف المبيعات أولاً!"}), 400

    product_name = request.args.get("product")
    product_data = data[data["المنتج"] == product_name]

    if product_data.empty:
        return jsonify({"error": "لم يتم العثور على المنتج"}), 404

    amount = product_data["صافي الكمية"].sum()

    recipe_data = data2[data2["name"] == product_name]
    if recipe_data.empty:
        return jsonify({"error": "لم يتم العثور على بيانات الوصفة"}), 404

    recipe_name = recipe_data["الصنف"].values
    recipe_price = recipe_data.iloc[:, 5].values
    recipe_amount_grams = recipe_data.iloc[:, 4].values
    recipe_total_price = recipe_price * amount

    recipe_result = []
    for i in range(len(recipe_name)):
        recipe_result.append(
            {
                "name": recipe_name[i],
                "amount": int(recipe_amount_grams[i] * amount),
                "total_price": int(recipe_price[i] * amount),
            }
        )

    return jsonify({"recipe": recipe_result})


if __name__ == "__main__":
    app.run(debug=True)
