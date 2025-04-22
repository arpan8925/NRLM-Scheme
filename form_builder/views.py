from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Form, FormSubmission, FileUpload
from django.utils import timezone
import json
import os
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def view_form(request, slug):
    form = get_object_or_404(Form, slug=slug, is_published=True)
    form_fields = json.loads(form.fields) if form.fields else []

    context = {
        'form': form,
        'form_fields': form_fields,
    }
    return render(request, 'form_builder/view_form.html', context)

@login_required
@require_POST
def submit_form(request, slug):
    form = get_object_or_404(Form, slug=slug, is_published=True)
    form_fields = json.loads(form.fields) if form.fields else []

    # Collect form responses
    responses = {}

    # Create form submission first to get the ID for file uploads
    form_submission = FormSubmission.objects.create(
        form=form,
        responses=json.dumps({}),  # Empty responses initially
        employee=request.user if request.user.is_authenticated else None
    )

    # Process each field
    for index, field in enumerate(form_fields, 1):
        field_name = f'field_{index}'
        field_label = field['label']

        if field['type'] == 'file':
            # Handle file upload
            if field_name in request.FILES:
                uploaded_file = request.FILES[field_name]

                # Save the file upload record
                file_upload = FileUpload.objects.create(
                    form_submission=form_submission,
                    field_label=field_label,
                    file=uploaded_file
                )

                # Store the file name in responses
                responses[field_label] = os.path.basename(file_upload.file.name)
            else:
                # No file was uploaded
                responses[field_label] = ''
        elif field['type'] == 'checkbox':
            # Handle multiple checkbox values
            responses[field_label] = request.POST.getlist(field_name)
        else:
            # Handle single value fields
            responses[field_label] = request.POST.get(field_name, '')

    # Update the form submission with the collected responses
    form_submission.responses = json.dumps(responses)
    form_submission.save()

    messages.success(request, 'Form submitted successfully!')
    return redirect('form_builder:view_form', slug=slug)

def preview_form(request):
    if request.method == 'POST':
        # Here you would handle form preview
        # For now, we'll just return a success message
        return JsonResponse({
            'success': True,
            'message': 'Form preview generated successfully'
        })
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)

# API endpoints for dynamic form fields

def get_user_location_data(request):
    """
    Get the current user's state, district, and block information
    """
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    # Return the user's location data
    location_data = {
        'state_id': user.state,
        'district_id': user.district,
        'block_id': user.block,
    }

    # Check if any location data is missing
    missing_fields = [field for field, value in location_data.items() if not value]
    if missing_fields:
        location_data['warnings'] = f"Missing location data: {', '.join(missing_fields)}"

    return JsonResponse(location_data)

@login_required
@require_http_methods(["GET"])
def fetch_states(request):
    """
    Fetch all states from the API
    """
    try:
        # Make request to the states API
        response = requests.get('https://cdn.lokos.in/lokos-masterdata/statemaster.json')

        # Check if the request was successful
        if response.status_code == 200:
            states = response.json()
            return JsonResponse(states, safe=False)
        else:
            return JsonResponse({'error': f'Failed to fetch states: {response.status_code}'}, status=response.status_code)

    except Exception as e:
        return JsonResponse({'error': f'Error fetching states: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def fetch_districts(request, state_id):
    """
    Fetch districts for a specific state
    """
    try:
        # Format state ID with leading zero if it's a single digit
        formatted_state_id = f"0{state_id}" if len(state_id) == 1 else state_id

        # Make request to the districts API
        response = requests.get(f'https://cdn.lokos.in/lokos-masterdata/state/{formatted_state_id}.json')

        # Check if the request was successful
        if response.status_code == 200:
            districts = response.json()
            return JsonResponse(districts, safe=False)
        else:
            return JsonResponse({'error': f'Failed to fetch districts: {response.status_code}'}, status=response.status_code)

    except Exception as e:
        return JsonResponse({'error': f'Error fetching districts: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def fetch_blocks(request, state_id, district_id):
    """
    Fetch blocks for a specific district
    """
    try:
        # Format state ID and district ID with leading zeros if they're single digits
        formatted_state_id = f"0{state_id}" if len(state_id) == 1 else state_id
        formatted_district_id = f"0{district_id}" if len(district_id) == 1 else district_id

        # Make request to the blocks API
        response = requests.get(f'https://cdn.lokos.in/lokos-masterdata/state/{formatted_state_id}/district/{formatted_district_id}.json')

        # Check if the request was successful
        if response.status_code == 200:
            blocks = response.json()
            return JsonResponse(blocks, safe=False)
        else:
            return JsonResponse({'error': f'Failed to fetch blocks: {response.status_code}'}, status=response.status_code)

    except Exception as e:
        return JsonResponse({'error': f'Error fetching blocks: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def fetch_villages(request, state_id=None, district_id=None, block_id=None):
    """
    Fetch villages for a specific block
    If state_id, district_id, or block_id are not provided, use the user's assigned location
    """
    try:
        user = request.user
        print(f"[DEBUG] Request User: {user}")

        # Use user's assigned location if not provided
        state_id = state_id or user.state
        district_id = district_id or user.district
        block_id = block_id or user.block

        # Pad state_id to two digits if needed (e.g., 3 -> 03)
        if state_id and isinstance(state_id, int):
            state_id = f"{state_id:02d}"
        elif state_id and isinstance(state_id, str) and state_id.isdigit():
            state_id = state_id.zfill(2)

        # Pad district_id to two digits if needed
        if district_id and isinstance(district_id, int):
            district_id = f"{district_id:02d}"
        elif district_id and isinstance(district_id, str) and district_id.isdigit():
            district_id = district_id.zfill(2)

        # Pad block_id to two digits if needed
        if block_id and isinstance(block_id, int):
            block_id = f"{block_id:02d}"
        elif block_id and isinstance(block_id, str) and block_id.isdigit():
            block_id = block_id.zfill(2)

        print(f"[DEBUG] Final State ID: {state_id}")
        print(f"[DEBUG] Final District ID: {district_id}")
        print(f"[DEBUG] Final Block ID: {block_id}")

        if not all([state_id, district_id, block_id]):
            print("[ERROR] Missing location data")
            return JsonResponse({'error': 'Missing location data. User does not have complete location information.'}, status=400)

        api_url = f'https://cdn.lokos.in/lokos-masterdata/state/{state_id}/district/{district_id}/block/{block_id}.json'
        print(f"[DEBUG] API URL: {api_url}")

        response = requests.get(api_url)
        print(f"[DEBUG] API Response Status Code: {response.status_code}")

        if response.status_code == 200:
            villages = response.json()
            print(f"[DEBUG] Villages Data Retrieved: {villages}")
            return JsonResponse(villages, safe=False)
        elif response.status_code == 404:
            print(f"[WARN] No data found for Block ID: {block_id}")
            return JsonResponse([], safe=False)
        else:
            print(f"[ERROR] Failed to fetch villages: {response.status_code} - {response.text}")
            return JsonResponse({'error': f'Failed to fetch villages: {response.status_code}'}, status=response.status_code)

    except Exception as e:
        print(f"[EXCEPTION] Exception occurred: {str(e)}")
        return JsonResponse({'error': f'Error fetching villages: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def fetch_shgs(request, state_code=None, block_id=None):
    """
    Fetch SHGs for a specific block
    If state_code or block_id are not provided, use the user's assigned location
    """
    try:
        # Get the user's location data if parameters are not provided
        user = request.user
        state_code = state_code or user.state
        block_id = block_id or user.block

        # Pad state_code to two digits if needed
        if state_code and isinstance(state_code, int):
            state_code = f"{state_code:02d}"
        elif state_code and isinstance(state_code, str) and state_code.isdigit():
            state_code = state_code.zfill(2)

        # Pad block_id to two digits if needed
        if block_id and isinstance(block_id, int):
            block_id = f"{block_id:02d}"
        elif block_id and isinstance(block_id, str) and block_id.isdigit():
            block_id = block_id.zfill(2)

        # Check if we have all required location data
        if not all([state_code, block_id]):
            return JsonResponse({'error': 'Missing location data. User does not have complete location information.'}, status=400)

        # Make request to the SHG API with required headers
        headers = {
            'X-APISETU-APIKEY': '18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf',
            'X-APISETU-CLIENTID': 'in.co.glpc'
        }

        response = requests.get(
            f'https://apisetu.gov.in/mord/lokos/srv/v1/{state_code}/shg/block?block_id={block_id}',
            headers=headers
        )

        # Check if the request was successful
        if response.status_code == 200:
            shgs = response.json()
            return JsonResponse(shgs, safe=False)
        else:
            return JsonResponse({'error': f'Failed to fetch SHGs: {response.status_code}'}, status=response.status_code)

    except Exception as e:
        return JsonResponse({'error': f'Error fetching SHGs: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def fetch_vos(request, state_code=None, block_id=None):
    """
    Fetch VOs for a specific block
    If state_code or block_id are not provided, use the user's assigned location
    """
    try:
        # Get the user's location data if parameters are not provided
        user = request.user
        state_code = state_code or user.state
        block_id = block_id or user.block

        # Pad state_code to two digits if needed
        if state_code and isinstance(state_code, int):
            state_code = f"{state_code:02d}"
        elif state_code and isinstance(state_code, str) and state_code.isdigit():
            state_code = state_code.zfill(2)

        # Pad block_id to two digits if needed
        if block_id and isinstance(block_id, int):
            block_id = f"{block_id:02d}"
        elif block_id and isinstance(block_id, str) and block_id.isdigit():
            block_id = block_id.zfill(2)

        # Check if we have all required location data
        if not all([state_code, block_id]):
            return JsonResponse({'error': 'Missing location data. User does not have complete location information.'}, status=400)

        # Make request to the VO API with required headers
        headers = {
            'X-APISETU-APIKEY': '18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf',
            'X-APISETU-CLIENTID': 'in.co.glpc'
        }

        response = requests.get(
            f'https://apisetu.gov.in/mord/lokos/srv/v1/{state_code}/vo/block?block_id={block_id}',
            headers=headers
        )

        # Check if the request was successful
        if response.status_code == 200:
            vos = response.json()
            return JsonResponse(vos, safe=False)
        else:
            return JsonResponse({'error': f'Failed to fetch VOs: {response.status_code}'}, status=response.status_code)

    except Exception as e:
        return JsonResponse({'error': f'Error fetching VOs: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def fetch_clfs(request, state_code=None, block_id=None):
    """
    Fetch CLFs for a specific block
    If state_code or block_id are not provided, use the user's assigned location
    """
    try:
        # Get the user's location data if parameters are not provided
        user = request.user
        state_code = state_code or user.state
        block_id = block_id or user.block

        # Pad state_code to two digits if needed
        if state_code and isinstance(state_code, int):
            state_code = f"{state_code:02d}"
        elif state_code and isinstance(state_code, str) and state_code.isdigit():
            state_code = state_code.zfill(2)

        # Pad block_id to two digits if needed
        if block_id and isinstance(block_id, int):
            block_id = f"{block_id:02d}"
        elif block_id and isinstance(block_id, str) and block_id.isdigit():
            block_id = block_id.zfill(2)

        # Check if we have all required location data
        if not all([state_code, block_id]):
            return JsonResponse({'error': 'Missing location data. User does not have complete location information.'}, status=400)

        # Make request to the CLF API with required headers
        headers = {
            'X-APISETU-APIKEY': '18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf',
            'X-APISETU-CLIENTID': 'in.co.glpc'
        }

        response = requests.get(
            f'https://apisetu.gov.in/mord/lokos/srv/v1/{state_code}/clf/block?block_id={block_id}',
            headers=headers
        )

        # Check if the request was successful
        if response.status_code == 200:
            clfs = response.json()
            return JsonResponse(clfs, safe=False)
        else:
            return JsonResponse({'error': f'Failed to fetch CLFs: {response.status_code}'}, status=response.status_code)

    except Exception as e:
        return JsonResponse({'error': f'Error fetching CLFs: {str(e)}'}, status=500)
