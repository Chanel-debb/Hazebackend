import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

PAYSTACK_SECRET = str(os.getenv('PAYSTACK_SECRET'))
VERIFY_URL = "https://api.paystack.co/transaction/verify/{}"

@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    body = json.loads(request.body.decode("utf-8"))
    reference = body.get("reference")

    if not reference:
        return JsonResponse({"error": "Reference not provided"}, status=400)

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.get(VERIFY_URL.format(reference), headers=headers)

    data = response.json()

   
    if data["status"] and data["data"]["status"] == "success":
      
        return JsonResponse({
            "message": "Payment verified successfully",
            "data": data["data"]
        })

    return JsonResponse({"error": "Verification failed", "data": data}, status=400)
