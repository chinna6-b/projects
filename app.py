# app.py - FINAL VERSION WITH ERROR FIX
import os
from flask import Flask, render_template, request, flash
# ... rest of your code ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
from flask import Flask, render_template, request, flash
import joblib
import pandas as pd
import joblib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "grocery_mart_ai_secret_2025"

# YOUR PATH
SAVE_FOLDER = r"C:\Users\chinna\OneDrive\Desktop\inventory\sales-predictor"

# Load model & encoders
model = joblib.load(os.path.join(SAVE_FOLDER, "model.pkl"))
le_product = joblib.load(os.path.join(SAVE_FOLDER, "enc_product.pkl"))
le_category = joblib.load(os.path.join(SAVE_FOLDER, "enc_category.pkl"))

print("Grocery Mart Loaded – Ready!")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Get form data
            product_input = request.form["product_name"].strip()
            category = request.form["category"]
            stock = int(request.form["stock"])
            reorder_level = int(request.form["reorder_level"])
            reorder_qty = int(request.form["reorder_qty"])
            price = float(request.form["price"])
            turnover = float(request.form["turnover"])

            # SMART FIX: Handle unknown products
            known_products = le_product.classes_
            product_name = None

            # Try exact match
            if product_input.title() in known_products:
                product_name = product_input.title()
            else:
                # Try case-insensitive match
                for p in known_products:
                    if product_input.lower() in p.lower() or p.lower() in product_input.lower():
                        product_name = p
                        break
                else:
                    # If still not found → use most common product (safe fallback)
                    product_name = "Banana"  # or any product that exists
                    flash(f"Product '{product_input}' not in database → using '{product_name}' for prediction", "warning")

            if product_name is None:
                product_name = "Banana"  # final safety

            # Create DataFrame
            df = pd.DataFrame([{
                'Product_Name': product_name,
                'Catagory': category,
                'Stock_Quantity': stock,
                'Reorder_Level': reorder_level,
                'Reorder_Quantity': reorder_qty,
                'Unit_Price': price,
                'Inventory_Turnover_Rate': turnover
            }])

            # Now safe to encode
            df['Product_enc'] = le_product.transform(df['Product_Name'])
            df['Cat_enc'] = le_category.transform(df['Catagory'])

            X = df[['Product_enc', 'Cat_enc', 'Stock_Quantity', 'Reorder_Level',
                   'Reorder_Quantity', 'Unit_Price', 'Inventory_Turnover_Rate']]

            prediction = int(model.predict(X)[0])

            return render_template("result.html",
                product=product_name,
                category=category,
                stock=stock,
                price=price,
                turnover=turnover,
                prediction=prediction,
                time=datetime.now().strftime("%I:%M %p • %B %d, %Y")
            )

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template("index.html")

if __name__ == "__main__":

    app.run(debug=False, port=5000)

