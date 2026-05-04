import requests
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def classify_name(request):
    name = request.GET.get('name')

    # Validation
    if not name:
        return Response(
            {"status": "error", "message": "Missing or empty name parameter"},
            status=400
        )

    if not name.isalpha():
        return Response(
            {"status": "error", "message": "Name must contain only letters"},
            status=422
        )

    url = f"https://api.genderize.io?name={name}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return Response(
            {"status": "error", "message": "External API request failed"},
            status=502
        )

    # Extract
    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count")

    # Edge case
    if gender is None or count == 0:
        return Response(
            {"status": "error", "message": "No prediction available for the provided name"},
            status=422
        )

    # Transform
    sample_size = count
    is_confident = probability >= 0.7 and sample_size >= 100

    # Timestamp
    processed_at = datetime.utcnow().isoformat() + "Z"

    # Final response
    return Response({
        "status": "success",
        "data": {
            "name": name,
            "gender": gender,
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at
        }
    })