from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Form, FormSubmission
from django.utils import timezone
import json
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
    for index, field in enumerate(form_fields, 1):
        field_name = f'field_{index}'
        
        if field['type'] in ['checkbox']:
            # Handle multiple checkbox values
            responses[field['label']] = request.POST.getlist(field_name)
        else:
            # Handle single value fields
            responses[field['label']] = request.POST.get(field_name)
    
    # Save form submission
    FormSubmission.objects.create(
        form=form,
        responses=json.dumps(responses)
    )
    
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
