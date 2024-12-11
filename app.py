from flask import Flask, render_template, jsonify, request
import os
import boto3
import pandas as pd
import json

app = Flask(__name__)

# Load CSV data at startup
DATA_FILE = "data/zip_risk_table.csv"
zip_risk_table = pd.read_csv(DATA_FILE)

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

# Route to get the legend based on dropdown selection
@app.route('/get-legend', methods=['GET'])
def get_legend():
    legend_type = request.args.get('legend_type', 'insurance-metrics')  # Default legend
    legends = {
        "insurance-metrics": """
            <h3>Insurance Metrics</h3>
            <table>
                <tr><th>Avg Deductible</th><td>The average deductible amount in dollars ($).</td></tr>
                <tr><th>Avg Fire Cov A</th><td>The average dollar ($) amount of insurance provided under Coverage A (Structure).</td></tr>
                <tr><th>Avg Fire Cov C</th><td>The average dollar ($) amount of insurance provided under Coverage C (Contents).</td></tr>
                <tr><th>Count of MERGED_P...</th><td>IGNORE (Technical Necessity, Disregard this Information).</td></tr>
                <tr><th>Earned Exposure</th><td>The number of exposure units earned during the calendar year (in exposure-years).</td></tr>
                <tr><th>Earned Premium</th><td>The dollar ($) amount of premium earned.</td></tr>
                <tr><th>Total Policies</th><td>The total number of policies in-effect during the calendar year.</td></tr>
            </table>
        """,
        "home-type": """
            <h3>Home Type</h3>
            <table>
                <tr><th>DO</th><td>Dwelling Owner-Occupied, sold to owners occupying the insured property. Also includes Lender/Forced Placed and Real Estate Owned (REO) type policies covering an Occupied Dwelling.</td></tr>
                <tr><th>DT</th><td>Dwelling Tenant-Occupied (including Condominium units), sold to owners not occupying the insured property, but occupied by a tenant. Also includes any policies covering an Unoccupied Dwelling/Vacant Dwelling.</td></tr>
                <tr><th>HC</th><td>Condominium Unit Owner, defined as HO6 or equivalent. Homeowners insurance sold to condominium owners occupying or renting out the insured property.</td></tr>
                <tr><th>HO</th><td>Homeowners, defined as HO1, HO2, HO3, HO5, HO8, or equivalent. Homeowners insurance sold to owners occupying the insured property.</td></tr>
                <tr><th>HT</th><td>Tenant/Renter, defined as HO4 or equivalent. Homeowners insurance sold to tenants renting the insured property.</td></tr>
                <tr><th>MO</th><td>Mobile Home, defined as HO7 or equivalent. Homeowners insurance sold to owners occupying or renting out the insured mobile home.</td></tr>
            </table>
        """
    }
    return jsonify({'legend': legends.get(legend_type, legends["insurance-metrics"])})

@app.route('/prediction-tool')
def prediction_tool_page():
    #endpoint
    #add data validation
    print("Serving prediction_tool.html")  # Debug log
    return render_template('prediction_tool.html')

def preprocess_user_input(data):
    # Continuous features
    processed_data = [
        float(data['longitude']),
        float(data['latitude']),
        float(data['propertyTax']),
        int(data['zipCode'])
    ]

    # One-hot encoding mappings
    # Window Type (2 features: Multi Pane, Single Pane)
    window_type_mapping = {
        '1': [1, 0],  # Multi Pane
        '2': [0, 1],  # Single Pane
        '3': [0, 0]   # Other/Unknown
    }
    window_type = window_type_mapping.get(data['windowType'], [0, 0])

    # Roof Type (4 features: Asphalt, Metal, Fire Resistant, Tile)
    roof_type_mapping = {
        '1': [1, 0, 0, 0],  # Asphalt
        '2': [0, 1, 0, 0],  # Metal
        '3': [0, 0, 1, 0],  # Fire Resistant
        '4': [0, 0, 0, 1],  # Tile
        '5': [0, 0, 0, 0]   # Other/Unknown
    }
    roof_type = roof_type_mapping.get(data['roofType'], [0, 0, 0, 0])

    # Vent Screen Type (3 features: No Vent Screen, Mesh Screen ≤ ⅛ inch, Mesh Screen > ⅛ inch)
    vent_screen_mapping = {
        '1': [1, 0, 0],  # No Vent Screen
        '2': [0, 1, 0],  # Mesh Screen (≤ ⅛ inch)
        '3': [0, 0, 1],  # Mesh Screen (> ⅛ inch)
        '4': [0, 0, 0]   # Other/Unknown
    }
    vent_screen = vent_screen_mapping.get(data['ventScreenType'], [0, 0, 0])

    # Initialize deck-related features as zeros (in the order: 
    # [Wood Deck or Porch Ground Level, Wood Deck or Porch Elevated, 
    # Masonry/Concrete Deck or Porch Ground Level, No Elevated Deck or Porch, No Ground Level Deck or Porch])
    deck_features = [0, 0, 0, 0, 0]

    # Update based on the user input
    ground_deck_type = data['groundDeck']
    elevated_deck_type = data['elevatedDeck']

    # Assign values based on ground deck type
    if ground_deck_type == '1':  # Wood Deck or Porch Ground Level
        deck_features[0] = 1
    elif ground_deck_type == '2':  # Masonry/Concrete Deck or Porch Ground Level
        deck_features[2] = 1
    elif ground_deck_type == '3':  # No Ground Level Deck or Porch
        deck_features[4] = 1
    # If ground_deck_type == '4', keep [0, 0, 0, 0, 0] as it is for Other/Unknown

    # Assign values based on elevated deck type
    if elevated_deck_type == '1':  # Wood Elevated Deck
        deck_features[1] = 1
    elif elevated_deck_type == '2':  # No Elevated Deck
        deck_features[3] = 1
    # If elevated_deck_type == '3', keep [0, 0, 0, 0, 0] as it is for Other/Unknown

    # Exterior Siding (3 features: Wood, Stucco/Brick, Combustible)
    exterior_siding_mapping = {
        '1': [1, 0, 0],  # Wood
        '2': [0, 1, 0],  # Stucco/Brick
        '3': [0, 0, 1],  # Combustible
        '4': [0, 0, 0]   # Other/Unknown
    }
    exterior_siding = exterior_siding_mapping.get(data['exteriorSiding'], [0, 0, 0])

    # Fence Type (3 features: No Fence, Non-Combustible Fence, Combustible Fence)
    fence_type_mapping = {
        '1': [1, 0, 0],  # No Fence Attached
        '2': [0, 1, 0],  # Non-Combustible Fence
        '3': [0, 0, 1],  # Combustible Fence
        '4': [0, 0, 0]   # Other/Unknown
    }
    fence_type = fence_type_mapping.get(data['fenceType'], [0, 0, 0])

    # Eave Type (3 features: Enclosed, Unenclosed, Other/Unknown)
    eave_type_mapping = {
        '1': [1, 0, 0],  # Enclosed
        '2': [0, 1, 0],  # Unenclosed
        '3': [0, 0, 1]   # Other/Unknown
    }
    eave_type = eave_type_mapping.get(data['eaveType'], [0, 0, 1])

    # Defensive Actions (2 features: No Action, Action Taken)
    # defensive_actions_mapping = {
    #     '1': [0, 1],  # Structure Defense Action Taken
    #     '0': [1, 0]   # No Structure Defense Actions
    # }
    # defensive_actions = defensive_actions_mapping.get(data['defensiveActions'], [1, 0])

    # Patio Cover (2 features: No Patio Cover, Combustible Attached Patio Cover)
    patio_cover_mapping = {
        '1': [0, 1],  # Combustible Attached Patio Cover
        '2': [1, 0],  # No Patio Cover
        '3': [0, 0]   # Other/Unknown
    }
    patio_cover = patio_cover_mapping.get(data['patioCover'], [0, 0])

    # Combine all processed features
    processed_data.extend(window_type)
    processed_data.extend(roof_type)
    processed_data.extend(vent_screen)
    processed_data.extend(deck_features)
    processed_data.extend(exterior_siding)
    processed_data.extend(fence_type)
    processed_data.extend(eave_type)
    # processed_data.extend(defensive_actions)
    processed_data.extend(patio_cover)

    # Ensure all categorical features are represented as integers
    processed_data = processed_data[:4] + [int(val) for val in processed_data[4:]]

    return processed_data


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION") 
SAGEMAKER_ENDPOINT = os.getenv("SAGEMAKER_ENDPOINT_URL")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse JSON data from the request
        data = request.get_json()
        if not data:
            raise ValueError("No JSON data received")

        # Preprocess user input
        processed_input = preprocess_user_input(data)

        print(processed_input)

        # Convert the input to a format suitable for the SageMaker endpoint (CSV format here)
        input_payload = ",".join(map(str, processed_input))  # Convert list to CSV string

        # Initialize the SageMaker runtime client
        runtime = boto3.client(
            'sagemaker-runtime',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

        # SageMaker endpoint name
        endpoint_name = SAGEMAKER_ENDPOINT

        # Invoke the SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',  # Match this to your model's expected format
            Body=input_payload
        )

        # Read and parse the response
        prediction = response['Body'].read().decode('utf-8')

        # Print and return prediction
        print(f"Prediction: {prediction}")
        return jsonify({
            "message": "Prediction successful",
            "prediction": prediction
        })

    except Exception as e:
        # Log error for easier debugging
        print("Error processing request:", str(e))
        return jsonify({"error": str(e)}), 400

@app.route('/fire-hazard-lookup', methods=['GET', 'POST'])
def fire_hazard_lookup_page():
    if request.method == 'GET':
        return render_template('fire_hazard_lookup.html')
    
    # Handle POST request for lookup
    data = request.json
    zipcode = data.get('zipcode')
    if not zipcode:
        return jsonify({'error': 'Please provide a valid zip code.'}), 400
    
    # Search for the zip code in the data
    row = zip_risk_table[zip_risk_table['ZIP_CODE'] == int(zipcode)]
    if row.empty:
        return jsonify({'error': f'No data found for ZIP Code {zipcode}.'}), 404
    
    # Extract values
    row_data = row.iloc[0]
    zip_code = int(row_data['ZIP_CODE'])  # Convert to native Python int
    fhsz = float(row_data['FHSZ'])        # Convert to native Python float
    risk_category = str(row_data['Risk Category'])  # Convert to string
    
    # Determine CSS class for risk category
    risk_class = {
        'Low': 'low-risk',
        'Moderate': 'moderate-risk',
        'High': 'high-risk',
        'Very High': 'very-high-risk',
    }.get(risk_category, '')

    # Return data as JSON
    return jsonify({
        'zip_code': zip_code,
        'fhsz': fhsz,
        'risk_category': risk_category,
        'risk_class': risk_class,
    })

@app.route('/about-us')
def about_us_page():
    return render_template('about_us.html')

if __name__ == '__main__':
    app.run(debug=True)
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port)

