from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------
model = joblib.load("car_price_random_forest.pkl")

# Exact column order the model was trained on
FEATURE_COLUMNS = list(model.feature_names_in_)

# Options extracted from the one-hot columns (used to build the form
# and to validate/encode incoming requests)
INSURANCE_OPTIONS = [c.replace('insurance_', '') for c in FEATURE_COLUMNS if c.startswith('insurance_')]
OWNER_OPTIONS = [c.replace('owner_type_', '') for c in FEATURE_COLUMNS if c.startswith('owner_type_')]
FUEL_OPTIONS = [c.replace('fuel_type_', '') for c in FEATURE_COLUMNS if c.startswith('fuel_type_')]
BODY_OPTIONS = [c.replace('body_type_', '') for c in FEATURE_COLUMNS if c.startswith('body_type_')]
CITY_OPTIONS = [c.replace('city_', '') for c in FEATURE_COLUMNS if c.startswith('city_')]
BRAND_OPTIONS = [c.replace('Brand_', '') for c in FEATURE_COLUMNS if c.startswith('Brand_')]

NUMERIC_FIELDS = ['registered_year', 'max_power', 'seats', 'Year', 'driven', 'avg', 'engine_size']


@app.route('/')
def home():
    return render_template(
        'index.html',
        insurance_options=sorted(INSURANCE_OPTIONS),
        owner_options=sorted(OWNER_OPTIONS),
        fuel_options=sorted(FUEL_OPTIONS),
        body_options=sorted(BODY_OPTIONS),
        city_options=sorted(CITY_OPTIONS),
        brand_options=sorted(BRAND_OPTIONS),
    )


def build_feature_row(data):
    """Turn the incoming JSON into a single-row DataFrame that exactly
    matches the columns/order the model was trained on."""

    # Start every one-hot column at 0
    row = {col: 0 for col in FEATURE_COLUMNS}

    # Fill numeric fields directly
    for field in NUMERIC_FIELDS:
        row[field] = float(data.get(field, 0))

    # transmission_type_Manual is a single binary column
    # (Automatic -> 0, Manual -> 1)
    row['transmission_type_Manual'] = 1 if data.get('transmission_type') == 'Manual' else 0

    # Set the matching one-hot flag to 1 for each categorical group
    def set_onehot(prefix, value):
        key = f"{prefix}_{value}"
        if key in row:
            row[key] = 1

    set_onehot('insurance', data.get('insurance'))
    set_onehot('owner_type', data.get('owner_type'))
    set_onehot('fuel_type', data.get('fuel_type'))
    set_onehot('body_type', data.get('body_type'))
    set_onehot('city', data.get('city'))
    set_onehot('Brand', data.get('Brand'))

    # Build DataFrame with columns in the EXACT order the model expects
    df = pd.DataFrame([row], columns=FEATURE_COLUMNS)
    return df


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        input_df = build_feature_row(data)
        prediction = model.predict(input_df)[0]
        return jsonify({'success': True, 'predicted_price': round(float(prediction), 2)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)
