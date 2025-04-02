document.addEventListener('DOMContentLoaded', function() {
    const formCanvas = document.getElementById('formCanvas');
    const widgets = document.querySelectorAll('.widget-item');
    const fieldSettings = document.getElementById('fieldSettings');
    let selectedField = null;

    // Initialize drag and drop
    widgets.forEach(widget => {
        widget.addEventListener('dragstart', handleDragStart);
        widget.addEventListener('dragend', handleDragEnd);
    });

    formCanvas.addEventListener('dragover', handleDragOver);
    formCanvas.addEventListener('drop', handleDrop);

    // Quick add buttons
    document.querySelectorAll('.quick-add-btn').forEach(btn => {
        btn.addEventListener('click', handleQuickAdd);
    });

    function handleDragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.type);
        e.target.classList.add('dragging');
    }

    function handleDragEnd(e) {
        e.target.classList.remove('dragging');
    }

    function handleDragOver(e) {
        e.preventDefault();
        formCanvas.classList.add('drag-over');
    }

    function handleDrop(e) {
        e.preventDefault();
        formCanvas.classList.remove('drag-over');
        const fieldType = e.dataTransfer.getData('text/plain');
        addFormField(fieldType);
    }

    function handleQuickAdd(e) {
        const fieldType = e.currentTarget.dataset.type;
        addFormField(fieldType);
    }

    function addFormField(type) {
        const emptyCanvas = document.querySelector('.empty-canvas');
        if (emptyCanvas) {
            emptyCanvas.remove();
        }

        const field = createFormField(type);
        formCanvas.appendChild(field);
        selectField(field);
    }

    function createFormField(type, label = '') {
        const field = document.createElement('div');
        field.className = 'form-field';
        field.setAttribute('data-type', type);

        // Create field header
        const fieldHeader = document.createElement('div');
        fieldHeader.className = 'field-header';

        // Create label input
        const labelInput = document.createElement('input');
        labelInput.type = 'text';
        labelInput.name = 'label';
        labelInput.className = 'field-label-input';
        labelInput.value = label || `New ${type.charAt(0).toUpperCase() + type.slice(1)} Field`;
        fieldHeader.appendChild(labelInput);

        // Create required checkbox
        const requiredContainer = document.createElement('div');
        requiredContainer.className = 'required-container';
        const requiredCheckbox = document.createElement('input');
        requiredCheckbox.type = 'checkbox';
        requiredCheckbox.name = 'required';
        requiredCheckbox.className = 'field-required';
        requiredCheckbox.id = `required-${Date.now()}`;
        const requiredLabel = document.createElement('label');
        requiredLabel.htmlFor = requiredCheckbox.id;
        requiredLabel.textContent = 'Required';
        requiredContainer.appendChild(requiredCheckbox);
        requiredContainer.appendChild(requiredLabel);
        fieldHeader.appendChild(requiredContainer);

        field.appendChild(fieldHeader);

        // Create field preview
        const fieldPreview = document.createElement('div');
        fieldPreview.className = 'field-preview';

        switch(type) {
            case 'text':
            case 'email':
            case 'phone':
            case 'name':
                const input = document.createElement('input');
                input.type = type === 'text' || type === 'name' ? 'text' : type;
                input.className = 'field-preview-input';
                input.placeholder = 'Enter your text';
                fieldPreview.appendChild(input);
                break;

            case 'textarea':
            case 'address':
                const textarea = document.createElement('textarea');
                textarea.className = 'field-preview-input';
                textarea.placeholder = type === 'address' ? 'Enter your address' : 'Enter your text';
                fieldPreview.appendChild(textarea);
                break;

            case 'select':
            case 'radio':
            case 'checkbox':
                const optionsContainer = document.createElement('div');
                optionsContainer.className = 'options-container';
                
                // Add default options with better labels based on type
                const defaultOptions = type === 'select' ? 
                    ['Select an option...', 'Option 1', 'Option 2'] :
                    type === 'radio' ? 
                        ['Yes', 'No', 'Maybe'] :
                        ['Option 1', 'Option 2', 'Option 3'];
                
                defaultOptions.forEach(optionText => {
                    const optionItem = document.createElement('div');
                    optionItem.className = 'option-item';
                    
                    const optionInput = document.createElement('input');
                    optionInput.type = 'text';
                    optionInput.value = optionText;
                    optionItem.appendChild(optionInput);
                    
                    optionsContainer.appendChild(optionItem);
                });

                // Add button to add more options
                const addOptionBtn = document.createElement('button');
                addOptionBtn.type = 'button';
                addOptionBtn.className = 'add-option-btn';
                addOptionBtn.textContent = '+ Add Option';
                addOptionBtn.onclick = () => {
                    const optionItem = document.createElement('div');
                    optionItem.className = 'option-item';
                    
                    const optionInput = document.createElement('input');
                    optionInput.type = 'text';
                    optionInput.value = `Option ${optionsContainer.children.length + 1}`;
                    optionItem.appendChild(optionInput);
                    
                    optionsContainer.appendChild(optionItem);
                };

                fieldPreview.appendChild(optionsContainer);
                fieldPreview.appendChild(addOptionBtn);
                break;
        }

        field.appendChild(fieldPreview);

        // Add delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'delete-field-btn';
        deleteBtn.innerHTML = '&times;';
        deleteBtn.onclick = () => field.remove();
        field.appendChild(deleteBtn);

        return field;
    }

    function selectField(field) {
        if (selectedField) {
            selectedField.classList.remove('selected');
        }
        selectedField = field;
        field.classList.add('selected');
        showFieldSettings(field);
    }

    function showFieldSettings(field) {
        const type = field.getAttribute('data-type');
        const labelInput = field.querySelector('.field-label-input');
        const requiredCheckbox = field.querySelector('.field-required');
        const previewInput = field.querySelector('.field-preview-input');

        fieldSettings.innerHTML = `
            <h3>Field Settings</h3>
            <div class="settings-group">
                <label>Field Label</label>
                <input type="text" 
                       class="setting-input setting-label" 
                       value="${labelInput ? labelInput.value : ''}"
                       id="settingLabel">
            </div>
            <div class="settings-group">
                <label>Required Field</label>
                <input type="checkbox" 
                       class="setting-required"
                       ${requiredCheckbox && requiredCheckbox.checked ? 'checked' : ''}
                       id="settingRequired">
            </div>
            ${['text', 'email', 'phone', 'name', 'textarea', 'address'].includes(type) ? `
                <div class="settings-group">
                    <label>Placeholder Text</label>
                    <input type="text" 
                           class="setting-input setting-placeholder"
                           value="${previewInput ? previewInput.placeholder : 'Enter your text'}"
                           id="settingPlaceholder">
                    <small class="setting-help">Default: "Enter your text" if not specified</small>
                </div>
            ` : ''}
            ${['select', 'radio', 'checkbox'].includes(type) ? `
                <div class="settings-group">
                    <label>Options</label>
                    <div class="options-list" id="settingOptions">
                        ${Array.from(field.querySelectorAll('.options-container input')).map((input, index) => `
                            <div class="option-item">
                                <input type="text" value="${input.value}" data-index="${index}">
                                <button type="button" class="btn-remove-option" data-index="${index}">&times;</button>
                            </div>
                        `).join('')}
                        <button type="button" class="btn-add-option" id="addOption">+ Add Option</button>
                    </div>
                </div>
            ` : ''}
        `;

        // Add event listeners after creating the elements
        const settingLabel = document.getElementById('settingLabel');
        const settingRequired = document.getElementById('settingRequired');
        const settingPlaceholder = document.getElementById('settingPlaceholder');
        const settingOptions = document.getElementById('settingOptions');

        if (settingLabel) {
            settingLabel.addEventListener('input', function() {
                updateFieldSetting(this, 'label');
            });
        }

        if (settingRequired) {
            settingRequired.addEventListener('change', function() {
                updateFieldSetting(this, 'required');
            });
        }

        if (settingPlaceholder) {
            settingPlaceholder.addEventListener('input', function() {
                updateFieldSetting(this, 'placeholder');
            });
        }

        if (settingOptions) {
            // Handle option input changes
            settingOptions.addEventListener('input', function(e) {
                if (e.target.matches('input[type="text"]')) {
                    const index = e.target.dataset.index;
                    const fieldOption = field.querySelectorAll('.options-container input')[index];
                    if (fieldOption) {
                        fieldOption.value = e.target.value;
                    }
                }
            });

            // Handle remove option button clicks
            settingOptions.addEventListener('click', function(e) {
                if (e.target.matches('.btn-remove-option')) {
                    const index = e.target.dataset.index;
                    const optionItems = field.querySelectorAll('.options-container .option-item');
                    if (optionItems[index]) {
                        optionItems[index].remove();
                        e.target.closest('.option-item').remove();
                    }
                }
            });

            // Handle add option button clicks
            const addOptionBtn = document.getElementById('addOption');
            if (addOptionBtn) {
                addOptionBtn.addEventListener('click', function() {
                    const optionsContainer = field.querySelector('.options-container');
                    const newOptionValue = `Option ${optionsContainer.children.length + 1}`;
                    
                    // Add to field
                    const fieldOptionItem = document.createElement('div');
                    fieldOptionItem.className = 'option-item';
                    const fieldOptionInput = document.createElement('input');
                    fieldOptionInput.type = 'text';
                    fieldOptionInput.value = newOptionValue;
                    fieldOptionItem.appendChild(fieldOptionInput);
                    optionsContainer.appendChild(fieldOptionItem);

                    // Add to settings
                    const settingOptionItem = document.createElement('div');
                    settingOptionItem.className = 'option-item';
                    settingOptionItem.innerHTML = `
                        <input type="text" value="${newOptionValue}" data-index="${optionsContainer.children.length - 1}">
                        <button type="button" class="btn-remove-option" data-index="${optionsContainer.children.length - 1}">&times;</button>
                    `;
                    addOptionBtn.parentElement.insertBefore(settingOptionItem, addOptionBtn);
                });
            }
        }
    }

    // Make updateFieldSetting globally accessible and update its functionality
    window.updateFieldSetting = function(input, settingType) {
        const field = document.querySelector('.form-field.selected');
        if (!field) return;

        switch(settingType) {
            case 'label':
                const labelInput = field.querySelector('.field-label-input');
                if (labelInput) {
                    labelInput.value = input.value;
                }
                break;
            
            case 'required':
                const requiredCheckbox = field.querySelector('.field-required');
                if (requiredCheckbox) {
                    requiredCheckbox.checked = input.checked;
                }
                break;
            
            case 'placeholder':
                const previewInput = field.querySelector('.field-preview-input');
                if (previewInput) {
                    previewInput.placeholder = input.value;
                }
                break;
        }
    };

    // Single function to collect form data
    function collectFormFields() {
        const formCanvas = document.getElementById('formCanvas');
        const fields = [];
        
        // Get all form field elements
        const fieldElements = formCanvas.getElementsByClassName('form-field');
        
        Array.from(fieldElements).forEach(field => {
            const type = field.getAttribute('data-type');
            const labelInput = field.querySelector('.field-label-input');
            const requiredCheckbox = field.querySelector('.field-required');
            const previewInput = field.querySelector('.field-preview-input');
            
            const fieldData = {
                type: type,
                label: labelInput ? labelInput.value : 'Untitled Field',
                required: requiredCheckbox ? requiredCheckbox.checked : false
            };

            // Add placeholder for text, email, phone, name, textarea fields
            if (['text', 'email', 'phone', 'name', 'textarea', 'address'].includes(type)) {
                fieldData.placeholder = previewInput && previewInput.placeholder ? 
                    previewInput.placeholder : 'Enter your text';
            }

            // Handle options for select, radio, and checkbox fields only
            if (['select', 'radio', 'checkbox'].includes(type)) {
                const optionsContainer = field.querySelector('.options-container');
                if (optionsContainer) {
                    const options = Array.from(optionsContainer.getElementsByTagName('input'))
                        .map(input => input.value)
                        .filter(value => value.trim() !== '');
                    if (options.length > 0) {
                        fieldData.options = options;
                    }
                }
            }

            fields.push(fieldData);
        });
        
        // Log the collected fields for debugging
        console.log('Collected fields:', fields);
        
        return fields;
    }

    // Function to get complete form data
    function getFormData() {
        const formData = {
            title: document.getElementById('formTitle').value || 'Untitled Form',
            fields: collectFormFields()
        };
        
        // Log the complete form data for debugging
        console.log('Complete form data:', formData);
        
        return formData;
    }

    // Add notification function
    function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.style.display = 'block';
        
        // Hide notification after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                notification.style.display = 'none';
                notification.style.animation = 'slideIn 0.3s ease-out';
            }, 300);
        }, 3000);
    }

    // Update save button handler
    document.querySelector('.btn-save').addEventListener('click', async function saveForm(e) {
        // Prevent any other click handlers from firing
        e.stopPropagation();
        
        // Remove any existing click handlers
        const saveButton = document.querySelector('.btn-save');
        const clonedButton = saveButton.cloneNode(true);
        saveButton.parentNode.replaceChild(clonedButton, saveButton);
        
        // Add the event listener to the new button
        clonedButton.addEventListener('click', saveForm);
        
        try {
            const formData = getFormData();
            
            // Validate form data
            if (!formData.fields || formData.fields.length === 0) {
                showNotification('Please add at least one field to the form', 'error');
                return;
            }

            // Log form data for debugging
            console.log('Saving form data:', formData);
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Disable the save button while saving
            // Submit using fetch
            const response = await fetch('/manager/forms/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                showNotification(`Form "${formData.title}" saved successfully!`, 'success');
                showSaveSuccessModal(result);
            } else {
                throw new Error(result.error || 'Failed to save form');
            }
            
        } catch (error) {
            console.error('Save error:', error);
            showNotification(error.message, 'error');
        }
    });

    // Preview button handler
    const previewBtn = document.querySelector('.btn-preview');
    const previewModal = document.getElementById('previewModal');
    const modalClose = document.querySelector('.modal-close');

    previewBtn.addEventListener('click', function() {
        const formData = getFormData();
        showPreview(formData);
    });

    modalClose.addEventListener('click', function() {
        previewModal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === previewModal) {
            previewModal.style.display = 'none';
        }
    });

    function showPreview(formData) {
        const modalTitle = document.getElementById('previewFormTitle');
        const modalContent = document.getElementById('previewFormContent');
        
        // Set the form title
        modalTitle.textContent = formData.title || 'Form Preview';
        
        // Generate the preview form HTML
        let previewHtml = `
            <form id="previewForm" class="preview-form">
                ${formData.fields.map(field => `
                    <div class="preview-field">
                        <label>
                            ${field.label}
                            ${field.required ? '<span class="required">*</span>' : ''}
                        </label>
                        ${generatePreviewFieldHtml(field)}
                    </div>
                `).join('')}
            </form>
        `;
        
        // Set the preview content
        modalContent.innerHTML = previewHtml;
        
        // Show the modal
        previewModal.style.display = 'block';
    }

    function generatePreviewFieldHtml(field) {
        switch (field.type) {
            case 'text':
            case 'name':
            case 'email':
            case 'phone':
                return `
                    <input type="${field.type === 'text' || field.type === 'name' ? 'text' : field.type}"
                           class="form-input"
                           placeholder="Enter ${field.label.toLowerCase()}"
                           ${field.required ? 'required' : ''}>
                `;
            
            case 'textarea':
            case 'address':
                return `
                    <textarea class="form-textarea"
                             placeholder="Enter ${field.label.toLowerCase()}"
                             ${field.required ? 'required' : ''}></textarea>
                `;
            
            case 'select':
                return `
                    <select class="form-select" ${field.required ? 'required' : ''}>
                        <option value="">Select ${field.label.toLowerCase()}</option>
                        ${field.options.map(opt => `
                            <option value="${opt}">${opt}</option>
                        `).join('')}
                    </select>
                `;
            
            case 'radio':
                return `
                    <div class="radio-group">
                        ${field.options.map(opt => `
                            <label class="radio-label">
                                <input type="radio"
                                       name="${field.label}"
                                       value="${opt}"
                                       ${field.required ? 'required' : ''}>
                                <span>${opt}</span>
                            </label>
                        `).join('')}
                    </div>
                `;
            
            case 'checkbox':
                return `
                    <div class="checkbox-group">
                        ${field.options.map(opt => `
                            <label class="checkbox-label">
                                <input type="checkbox"
                                       name="${field.label}[]"
                                       value="${opt}">
                                <span>${opt}</span>
                            </label>
                        `).join('')}
                    </div>
                `;
            
            default:
                return '';
        }
    }

    // Update publish button handler
    document.querySelector('.btn-publish').addEventListener('click', async () => {
        try {
            const formData = getFormData();
            
            // Validate form data
            if (!formData.fields || formData.fields.length === 0) {
                showNotification('Please add at least one field to the form', 'error');
                return;
            }

            // Log form data for debugging
            console.log('Publishing form data:', formData);
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Submit using fetch
            const response = await fetch('/manager/forms/publish/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                showNotification(`Form "${formData.title}" published successfully!`, 'success');
                showPublishSuccessModal(result);
            } else {
                throw new Error(result.error || 'Failed to publish form');
            }
            
        } catch (error) {
            console.error('Publish error:', error);
            showNotification(error.message, 'error');
        }
    });

    // Add this function to show publish success modal
    function showPublishSuccessModal(result) {
        const modal = document.createElement('div');
        modal.className = 'modal publish-success-modal';
        modal.style.display = 'block';
        
        modal.innerHTML = `
            <div class="modal-content publish-success-content">
                <div class="modal-header">
                    <h2>Form Published Successfully!</h2>
                    <button class="modal-close" type="button">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="publish-details">
                        <div class="form-summary">
                            <h3>${result.form_data.title}</h3>
                            <p>Form ID: ${result.form_id}</p>
                            <p>Status: Published</p>
                            <p>Public URL: <a href="${result.public_url}" target="_blank">${result.public_url}</a></p>
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button class="btn-copy" onclick="copyToClipboard('${result.public_url}')">
                            Copy Public URL
                        </button>
                        <button class="btn-view" onclick="window.location.href='${result.redirect_url}'">
                            View All Forms
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add close button functionality
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.style.display = 'none';
            modal.remove();
        });

        // Close modal when clicking outside
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
                modal.remove();
            }
        });
    }

    // Add helper function to copy URL to clipboard
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert('Public URL copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy URL: ', err);
        });
    }

    // Add this function to show the save success modal
    function showSaveSuccessModal(result) {
        const modal = document.createElement('div');
        modal.className = 'modal save-success-modal';
        modal.style.display = 'block';
        
        const formattedFields = result.form_data.fields.map(field => `
            <div class="field-summary">
                <h4>${field.label}</h4>
                <ul>
                    <li>Type: ${field.type}</li>
                    <li>Required: ${field.required ? 'Yes' : 'No'}</li>
                    ${field.placeholder ? `<li>Placeholder: ${field.placeholder}</li>` : ''}
                    ${field.options && field.options.length > 0 ? 
                        `<li>Options: ${field.options.join(', ')}</li>` : ''}
                </ul>
            </div>
        `).join('');

        modal.innerHTML = `
            <div class="modal-content save-success-content">
                <div class="modal-header">
                    <h2>Form Saved Successfully!</h2>
                    <button class="modal-close" type="button">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="save-details">
                        <div class="form-summary">
                            <h3>${result.form_data.title}</h3>
                            <p>Form ID: ${result.form_id}</p>
                            <p>Created: ${result.form_data.created_at}</p>
                            <p>Status: ${result.form_data.status}</p>
                        </div>
                        
                        <div class="fields-summary">
                            <h3>Form Fields (${result.form_data.fields.length})</h3>
                            <div class="fields-grid">
                                ${formattedFields}
                            </div>
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button class="btn-view" onclick="window.location.href='${result.redirect_url}'">
                            View All Forms
                        </button>
                        <button class="btn-continue" onclick="this.closest('.modal').style.display='none'">
                            Continue Editing
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add styles for the save success modal
        const styles = document.createElement('style');
        styles.textContent = `
            .save-success-modal .modal-content {
                max-width: 800px;
            }
            
            .save-success-content {
                background: #1a1f2e;
            }
            
            .save-details {
                padding: 1.5rem;
            }
            
            .form-summary {
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #374151;
            }
            
            .form-summary h3 {
                color: #e2e8f0;
                margin-bottom: 1rem;
            }
            
            .form-summary p {
                color: #9ca3af;
                margin: 0.5rem 0;
            }
            
            .fields-summary h3 {
                color: #e2e8f0;
                margin-bottom: 1.5rem;
            }
            
            .fields-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1rem;
            }
            
            .field-summary {
                background: #242b3d;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 1rem;
            }
            
            .field-summary h4 {
                color: #e2e8f0;
                margin: 0 0 1rem 0;
            }
            
            .field-summary ul {
                list-style: none;
                padding: 0;
                margin: 0;
                color: #9ca3af;
            }
            
            .field-summary li {
                margin: 0.5rem 0;
            }
            
            .modal-actions {
                display: flex;
                justify-content: flex-end;
                gap: 1rem;
                padding: 1.5rem;
                background: #242b3d;
                border-top: 1px solid #374151;
            }
            
            .btn-view,
            .btn-continue {
                padding: 0.75rem 1.5rem;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .btn-view {
                background: #4f46e5;
                color: white;
                border: none;
            }
            
            .btn-continue {
                background: #2d3648;
                color: #e2e8f0;
                border: 1px solid #374151;
            }
            
            .btn-view:hover {
                background: #4338ca;
            }
            
            .btn-continue:hover {
                background: #374151;
            }
        `;

        document.head.appendChild(styles);
        document.body.appendChild(modal);

        // Add close button functionality
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.style.display = 'none';
            modal.remove();
        });

        // Close modal when clicking outside
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
                modal.remove();
            }
        });
    }
});

// Global functions for field actions
function moveField(btn, direction) {
    const field = btn.closest('.form-field');
    if (direction === 'up' && field.previousElementSibling) {
        field.parentNode.insertBefore(field, field.previousElementSibling);
    } else if (direction === 'down' && field.nextElementSibling) {
        field.parentNode.insertBefore(field.nextElementSibling, field);
    }
}

function deleteField(btn) {
    const field = btn.closest('.form-field');
    field.remove();
    
    if (document.querySelectorAll('.form-field').length === 0) {
        const emptyState = `
            <div class="empty-canvas">
                <p>Drag and drop form elements here</p>
                <div class="quick-add-container">
                    <h4>Quick Add Common Fields</h4>
                    <div class="quick-add-grid">
                        <!-- Quick add buttons here -->
                    </div>
                </div>
            </div>
        `;
        document.getElementById('formCanvas').innerHTML = emptyState;
    }
}

function updateFieldLabel(input) {
    const field = document.querySelector('.form-field.selected');
    if (field) {
        field.querySelector('label').textContent = input.value;
    }
}

function toggleRequired(checkbox) {
    const field = document.querySelector('.form-field.selected');
    if (field) {
        const input = field.querySelector('input, textarea, select');
        input.required = checkbox.checked;
    }
}

// Update the generateFieldHtml function
function generateFieldHtml(field) {
    switch (field.type) {
        case 'text':
        case 'name':
        case 'email':
        case 'phone':
            return `<input type="${field.type === 'text' || field.type === 'name' ? 'text' : field.type}" 
                           name="${field.label}" 
                           class="form-input"
                           ${field.required ? 'required' : ''}>`;
        
        case 'textarea':
        case 'address':
            return `<textarea name="${field.label}" 
                            class="form-textarea"
                            ${field.required ? 'required' : ''}></textarea>`;
        
        case 'select':
            return `
                <select name="${field.label}" 
                        class="form-select"
                        ${field.required ? 'required' : ''}>
                    <option value="">Select an option</option>
                    ${field.options.map(opt => `
                        <option value="${opt}">${opt}</option>
                    `).join('')}
                </select>`;
        
        case 'radio':
            return `
                <div class="radio-group">
                    ${field.options.map(opt => `
                        <label class="radio-label">
                            <input type="radio" 
                                   name="${field.label}" 
                                   value="${opt}"
                                   ${field.required ? 'required' : ''}>
                            ${opt}
                        </label>
                    `).join('')}
                </div>`;
        
        case 'checkbox':
            return `
                <div class="checkbox-group">
                    ${field.options.map(opt => `
                        <label class="checkbox-label">
                            <input type="checkbox" 
                                   name="${field.label}[]" 
                                   value="${opt}">
                            ${opt}
                        </label>
                    `).join('')}
                </div>`;
        
        default:
            return '';
    }
} 