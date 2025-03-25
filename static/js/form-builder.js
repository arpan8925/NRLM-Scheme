document.addEventListener('DOMContentLoaded', function() {
    const formCanvas = document.getElementById('formCanvas');
    const widgets = document.querySelectorAll('.widget-item');
    const fieldSettings = document.querySelector('.field-settings-content');
    const noFieldSelected = document.querySelector('.no-field-selected');
    let selectedField = null;
    let formId = null; // To store the draft form ID
    let cachedFields = []; // To store fields before saving

    // Create draft form when page loads
    createDraftForm();

    // Initialize drag and drop for widgets
    widgets.forEach(widget => {
        widget.addEventListener('dragstart', (e) => {
            // Set dragging attribute on the widget
            widget.setAttribute('isdragging', 'true');
            widget.classList.add('dragging');
        });

        widget.addEventListener('dragend', (e) => {
            widget.removeAttribute('isdragging');
            widget.classList.remove('dragging');
        });
        
        // Keep the click-to-add functionality
        widget.addEventListener('click', (e) => {
            const type = e.currentTarget.dataset.type;
            addFieldToCanvas(type);
        });
    });

    // Form canvas drop zone handlers
    formCanvas.addEventListener('dragenter', (e) => {
        e.preventDefault();
        e.stopPropagation();
        formCanvas.classList.add('drag-over');
    });

    formCanvas.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
    });

    formCanvas.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!formCanvas.contains(e.relatedTarget)) {
            formCanvas.classList.remove('drag-over');
        }
    });

    formCanvas.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        formCanvas.classList.remove('drag-over');
        
        // Find the dragging widget
        const draggingWidget = document.querySelector('.widget-item[isdragging="true"]');
        if (draggingWidget) {
            const type = draggingWidget.dataset.type;
            draggingWidget.removeAttribute('isdragging');
            addFieldToCanvas(type);
        }
    });

    function addFieldToCanvas(type) {
        const field = createField(type);
        
        // Remove empty canvas message if it exists
        const emptyCanvas = formCanvas.querySelector('.empty-canvas');
        if (emptyCanvas) {
            emptyCanvas.remove();
        }

        formCanvas.appendChild(field);
        field.scrollIntoView({ behavior: 'smooth' });
        selectField(field);
        cacheField(field);

        // Make the field draggable within the canvas
        makeFieldDraggable(field);
    }

    function cacheField(field) {
        const fieldData = {
            type: field.dataset.type,
            label: field.querySelector('label')?.textContent,
            required: field.querySelector('input, textarea, select')?.required,
            placeholder: field.querySelector('input, textarea')?.placeholder,
            options: Array.from(field.querySelectorAll('option, input[type="radio"], input[type="checkbox"]'))
                .map(opt => opt.value || opt.textContent)
        };
        cachedFields.push(fieldData);
    }

    function makeFieldDraggable(field) {
        field.draggable = true;
        
        field.addEventListener('dragstart', (e) => {
            e.stopPropagation();
            field.setAttribute('isdragging', 'true');
            field.classList.add('dragging');
        });
        
        field.addEventListener('dragend', () => {
            field.removeAttribute('isdragging');
            field.classList.remove('dragging');
        });
    }

    function createField(type) {
        const field = document.createElement('div');
        field.className = 'form-field';
        field.dataset.type = type;
        field.innerHTML = getFieldHTML(type);

        field.addEventListener('click', (e) => {
            e.stopPropagation();
            selectField(field);
        });

        // Make the field draggable
        makeFieldDraggable(field);

        return field;
    }

    function selectField(field) {
        // Remove selection from previously selected field
        if (selectedField) {
            selectedField.classList.remove('selected');
        }

        // Select new field
        selectedField = field;
        field.classList.add('selected');

        // Show field settings
        fieldSettings.style.display = 'block';
        noFieldSelected.style.display = 'none';

        // Update settings panel based on field type
        updateFieldSettings(field);
    }

    function updateFieldSettings(field) {
        const type = field.dataset.type;
        const optionsSection = document.querySelector('.field-options');
        
        // Show/hide options section based on field type
        if (['select', 'radio', 'checkbox'].includes(type)) {
            optionsSection.style.display = 'block';
        } else {
            optionsSection.style.display = 'none';
        }

        // Update current values
        document.getElementById('fieldLabel').value = field.querySelector('label')?.textContent || '';
        document.getElementById('fieldPlaceholder').value = field.querySelector('input')?.placeholder || '';
        document.getElementById('fieldRequired').checked = field.querySelector('input')?.required || false;
    }

    function getFieldHTML(type) {
        const templates = {
            text: `
                <label>Text Field</label>
                <input type="text" placeholder="Enter text">
            `,
            textarea: `
                <label>Text Area</label>
                <textarea placeholder="Enter long text"></textarea>
            `,
            number: `
                <label>Number</label>
                <input type="number" placeholder="Enter number">
            `,
            select: `
                <label>Dropdown</label>
                <select>
                    <option value="">Select an option</option>
                </select>
            `,
            radio: `
                <label>Radio Group</label>
                <div class="radio-group">
                    <label><input type="radio" name="radio-group"> Option 1</label>
                    <label><input type="radio" name="radio-group"> Option 2</label>
                </div>
            `,
            checkbox: `
                <label>Checkbox Group</label>
                <div class="checkbox-group">
                    <label><input type="checkbox"> Option 1</label>
                    <label><input type="checkbox"> Option 2</label>
                </div>
            `
        };
        return templates[type] || '';
    }

    // Field Settings Event Listeners
    document.getElementById('fieldLabel').addEventListener('input', (e) => {
        if (selectedField) {
            selectedField.querySelector('label').textContent = e.target.value;
        }
    });

    document.getElementById('fieldPlaceholder').addEventListener('input', (e) => {
        if (selectedField) {
            const input = selectedField.querySelector('input, textarea');
            if (input) {
                input.placeholder = e.target.value;
            }
        }
    });

    document.getElementById('fieldRequired').addEventListener('change', (e) => {
        if (selectedField) {
            const input = selectedField.querySelector('input, textarea, select');
            if (input) {
                input.required = e.target.checked;
            }
        }
    });

    // Save Form
    document.querySelector('.btn-save').addEventListener('click', saveForm);

    function saveForm() {
        const formData = {
            title: document.getElementById('formTitle').value,
            fields: cachedFields,
            status: 'published',
            form_id: formId
        };

        fetch('/manager/forms/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}); 