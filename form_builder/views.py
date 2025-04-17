from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Form, FormSubmission, FileUpload
from django.utils import timezone
import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Create your views here.

def view_form(request, slug):
    form = get_object_or_404(Form, slug=slug, is_published=True)
    form_fields = json.loads(form.fields) if form.fields else []

    context = {
        'form': form,
        'form_fields': form_fields,
    }
    return render(request, 'form_builder/view_form.html', context)

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
