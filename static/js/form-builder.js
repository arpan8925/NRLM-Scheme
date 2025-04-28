// Global variables
let selectedField = null;
let userLocationData = null;

// Function to fetch user location data
async function fetchUserLocationData() {
    try {
        const response = await fetch('/forms/api/user-location/');
        if (!response.ok) {
            throw new Error(`Failed to fetch user location: ${response.status}`);
        }
        userLocationData = await response.json();
        console.log('User location data:', userLocationData);

        // Format IDs with leading zeros if needed
        if (userLocationData.state_id && typeof userLocationData.state_id === 'string' && userLocationData.state_id.length === 1) {
            userLocationData.state_id = '0' + userLocationData.state_id;
        }
        if (userLocationData.district_id && typeof userLocationData.district_id === 'string' && userLocationData.district_id.length === 1) {
            userLocationData.district_id = '0' + userLocationData.district_id;
        }
        if (userLocationData.block_id && typeof userLocationData.block_id === 'string' && userLocationData.block_id.length === 1) {
            userLocationData.block_id = '0' + userLocationData.block_id;
        }

        console.log('Formatted user location data:', userLocationData);
        return userLocationData;
    } catch (error) {
        console.error('Error fetching user location data:', error);
        return null;
    }
}

// Function to fetch villages using user's location
async function fetchVillages() {
    try {
        const response = await fetch('/forms/api/villages/');
        if (!response.ok) {
            throw new Error(`Failed to fetch villages: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching villages:', error);
        return [];
    }
}

// Function to fetch SHGs using user's location
async function fetchSHGs() {
    try {
        const response = await fetch('/forms/api/shgs/');
        if (!response.ok) {
            throw new Error(`Failed to fetch SHGs: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching SHGs:', error);
        return [];
    }
}

// Function to fetch VOs using user's location
async function fetchVOs() {
    try {
        const response = await fetch('/forms/api/vos/');
        if (!response.ok) {
            throw new Error(`Failed to fetch VOs: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching VOs:', error);
        return [];
    }
}

// Function to fetch CLFs using user's location
async function fetchCLFs() {
    try {
        const response = await fetch('/forms/api/clfs/');
        if (!response.ok) {
            throw new Error(`Failed to fetch CLFs: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching CLFs:', error);
        return [];
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Fetch user location data when the page loads
    fetchUserLocationData();
    const formCanvas = document.getElementById('formCanvas');
    const widgets = document.querySelectorAll('.widget-item');

    // Initialize drag and drop
    widgets.forEach(widget => {
        widget.addEventListener('dragstart', handleDragStart);
        widget.addEventListener('dragend', handleDragEnd);
    });

    formCanvas.addEventListener('dragover', handleDragOver);
    formCanvas.addEventListener('drop', handleDrop);

    // Add event delegation for field selection and delete buttons
    document.addEventListener('click', function(e) {
        // Handle delete button clicks
        if (e.target.classList.contains('delete-field-btn')) {
            console.log('Delete button clicked');
            e.stopPropagation(); // Prevent event bubbling
            const field = e.target.closest('.form-field');
            console.log('Field found:', field);

            if (field) {
                // Check if this is the selected field
                const isSelected = field.classList.contains('selected');
                console.log('Is selected field:', isSelected);

                // Remove the field
                field.remove();
                console.log('Field removed');

                // Clear field settings if this was the selected field
                if (isSelected) {
                    selectedField = null;
                    const fieldSettings = document.getElementById('fieldSettings');
                    console.log('Field settings element:', fieldSettings);

                    if (fieldSettings) {
                        // Force a complete reset of the field settings panel
                        fieldSettings.innerHTML = '';
                        setTimeout(() => {
                            fieldSettings.innerHTML = '<h3>Field Settings</h3><p class="no-field-selected">Select a field to edit its properties</p>';
                            console.log('Field settings cleared from global click handler');
                        }, 0);
                    }
                }
            }
        }
        // Handle field selection (but not when clicking on delete button or other controls)
        else {
            const field = e.target.closest('.form-field');
            if (field && !e.target.closest('.field-action-btn') && !e.target.closest('.add-option-btn')) {
                console.log('Field clicked for selection:', field);
                selectField(field);
            }
        }

    // Check if form canvas is empty
    if (document.querySelectorAll('.form-field').length === 0) {
        const emptyState = `
            <div class="empty-canvas">
                <p>Drag and drop form elements here</p>
                <div class="quick-add-container">
                    <h4>Quick Add Common Fields</h4>
                    <div class="quick-add-grid">
                        <button type="button" class="quick-add-btn" data-type="text">Text Field</button>
                        <button type="button" class="quick-add-btn" data-type="email">Email Field</button>
                        <button type="button" class="quick-add-btn" data-type="select">Dropdown</button>
                        <button type="button" class="quick-add-btn" data-type="radio">Radio Buttons</button>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('formCanvas').innerHTML = emptyState;

        // Re-add event listeners to quick add buttons
        document.querySelectorAll('.quick-add-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const fieldType = e.currentTarget.dataset.type;
                addFormField(fieldType);
            });
        });
    }
});

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

    // Make createFormField globally accessible
    window.createFormField = function(type, label = '') {
        console.log('Creating form field of type:', type, 'with label:', label);
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

            case 'file':
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.className = 'field-preview-input';
                fileInput.disabled = true; // Disabled in preview mode
                fieldPreview.appendChild(fileInput);
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

            case 'village_list':
                const villageSelect = document.createElement('select');
                villageSelect.className = 'field-preview-input dynamic-dropdown';
                villageSelect.disabled = true; // Disabled in preview mode

                const villageDefaultOption = document.createElement('option');
                villageDefaultOption.value = '';
                villageDefaultOption.textContent = 'Select a Village (Will load dynamically)';
                villageSelect.appendChild(villageDefaultOption);

                // Add API info as data attributes
                villageSelect.setAttribute('data-api-type', 'village');
                villageSelect.setAttribute('data-api-url', '/forms/api/villages/');

                fieldPreview.appendChild(villageSelect);

                // Add API info note
                const villageApiInfo = document.createElement('div');
                villageApiInfo.className = 'api-info';
                villageApiInfo.innerHTML = '<small>Data will be loaded from Village API based on user\'s State, District, and Block</small>';
                fieldPreview.appendChild(villageApiInfo);

                // Load villages if user location data is available
                if (userLocationData && userLocationData.state_id && userLocationData.district_id && userLocationData.block_id) {
                    // Show loading indicator
                    villageApiInfo.innerHTML = '<small>Loading villages...</small>';

                    // Fetch villages
                    fetchVillages()
                        .then(villages => {
                            // Clear existing options except the first one
                            while (villageSelect.options.length > 1) {
                                villageSelect.remove(1);
                            }

                            // Add villages to the dropdown
                            // Check if we have a list of panchayats with nested villages
                            if (villages.length > 0 && villages[0].villagelist) {
                                // Process nested village structure
                                villages.forEach(panchayat => {
                                    if (panchayat.villagelist && panchayat.villagelist.length > 0) {
                                        // Create an optgroup for the panchayat if it has multiple villages
                                        let optgroup = null;
                                        if (panchayat.villagelist.length > 1) {
                                            optgroup = document.createElement('optgroup');
                                            optgroup.label = panchayat.panchayat_name_en;
                                            villageSelect.appendChild(optgroup);
                                        }

                                        // Add each village in the panchayat
                                        panchayat.villagelist.forEach(village => {
                                            const option = document.createElement('option');
                                            // Use lowercase village name as value
                                            option.value = village.villageNameEnglish.toLowerCase();
                                            // Use proper case for display text
                                            option.textContent = village.villageNameEnglish;

                                            // Add to optgroup if it exists, otherwise directly to select
                                            if (optgroup) {
                                                optgroup.appendChild(option);
                                            } else {
                                                villageSelect.appendChild(option);
                                            }
                                        });
                                    }
                                });
                            } else {
                                // Fallback to direct village list if structure is different
                                villages.forEach(village => {
                                    const option = document.createElement('option');
                                    if (village.villageNameEnglish) {
                                        // New API format
                                        option.value = village.villageNameEnglish.toLowerCase();
                                        option.textContent = village.villageNameEnglish;
                                    } else {
                                        // Old API format
                                        option.value = (village.village_name_en || village.name || '').toLowerCase();
                                        option.textContent = village.village_name_en || village.name || '';
                                    }
                                    villageSelect.appendChild(option);
                                });
                            }

                            // Update API info note
                            villageApiInfo.innerHTML = `<small>Loaded ${villages.length} villages from API</small>`;
                        })
                        .catch(error => {
                            console.error('Error loading villages:', error);
                            villageApiInfo.innerHTML = '<small>Error loading villages. Please try again.</small>';
                        });
                }
                break;

            case 'shg_list':
                const shgSelect = document.createElement('select');
                shgSelect.className = 'field-preview-input dynamic-dropdown';
                shgSelect.disabled = true; // Disabled in preview mode

                const shgDefaultOption = document.createElement('option');
                shgDefaultOption.value = '';
                shgDefaultOption.textContent = 'Select an SHG (Will load dynamically)';
                shgSelect.appendChild(shgDefaultOption);

                // Add API info as data attributes
                shgSelect.setAttribute('data-api-type', 'shg');
                shgSelect.setAttribute('data-api-url', '/forms/api/shgs/');
                shgSelect.setAttribute('data-api-key', '18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf');
                shgSelect.setAttribute('data-api-client', 'in.co.glpc');

                fieldPreview.appendChild(shgSelect);

                // Add API info note
                const shgApiInfo = document.createElement('div');
                shgApiInfo.className = 'api-info';
                shgApiInfo.innerHTML = '<small>Data will be loaded from SHG API based on user\'s State and Block</small>';
                fieldPreview.appendChild(shgApiInfo);

                // Load SHGs if user location data is available
                if (userLocationData && userLocationData.state_id && userLocationData.block_id) {
                    // Show loading indicator
                    shgApiInfo.innerHTML = '<small>Loading SHGs...</small>';

                    // Fetch SHGs
                    fetchSHGs()
                        .then(shgs => {
                            // Clear existing options except the first one
                            while (shgSelect.options.length > 1) {
                                shgSelect.remove(1);
                            }

                            // Add SHGs to the dropdown
                            shgs.forEach(shg => {
                                const option = document.createElement('option');
                                const shgName = shg.shg_name || shg.name || '';
                                option.value = shgName.toLowerCase();
                                option.textContent = shgName;
                                shgSelect.appendChild(option);
                            });

                            // Update API info note
                            shgApiInfo.innerHTML = `<small>Loaded ${shgs.length} SHGs from API</small>`;
                        })
                        .catch(error => {
                            console.error('Error loading SHGs:', error);
                            shgApiInfo.innerHTML = '<small>Error loading SHGs. Please try again.</small>';
                        });
                }
                break;

            case 'vo_list':
                const voSelect = document.createElement('select');
                voSelect.className = 'field-preview-input dynamic-dropdown';
                voSelect.disabled = true; // Disabled in preview mode

                const voDefaultOption = document.createElement('option');
                voDefaultOption.value = '';
                voDefaultOption.textContent = 'Select a VO (Will load dynamically)';
                voSelect.appendChild(voDefaultOption);

                // Add API info as data attributes
                voSelect.setAttribute('data-api-type', 'vo');
                voSelect.setAttribute('data-api-url', '/forms/api/vos/');
                voSelect.setAttribute('data-api-key', '18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf');
                voSelect.setAttribute('data-api-client', 'in.co.glpc');

                fieldPreview.appendChild(voSelect);

                // Add API info note
                const voApiInfo = document.createElement('div');
                voApiInfo.className = 'api-info';
                voApiInfo.innerHTML = '<small>Data will be loaded from VO API based on user\'s State and Block</small>';
                fieldPreview.appendChild(voApiInfo);

                // Load VOs if user location data is available
                if (userLocationData && userLocationData.state_id && userLocationData.block_id) {
                    // Show loading indicator
                    voApiInfo.innerHTML = '<small>Loading VOs...</small>';

                    // Fetch VOs
                    fetchVOs()
                        .then(vos => {
                            // Clear existing options except the first one
                            while (voSelect.options.length > 1) {
                                voSelect.remove(1);
                            }

                            // Add VOs to the dropdown
                            vos.forEach(vo => {
                                const option = document.createElement('option');
                                const voName = vo.vo_name || vo.name || '';
                                option.value = voName.toLowerCase();
                                option.textContent = voName;
                                voSelect.appendChild(option);
                            });

                            // Update API info note
                            voApiInfo.innerHTML = `<small>Loaded ${vos.length} VOs from API</small>`;
                        })
                        .catch(error => {
                            console.error('Error loading VOs:', error);
                            voApiInfo.innerHTML = '<small>Error loading VOs. Please try again.</small>';
                        });
                }
                break;

            case 'clf_list':
                const clfSelect = document.createElement('select');
                clfSelect.className = 'field-preview-input dynamic-dropdown';
                clfSelect.disabled = true; // Disabled in preview mode

                const clfDefaultOption = document.createElement('option');
                clfDefaultOption.value = '';
                clfDefaultOption.textContent = 'Select a CLF (Will load dynamically)';
                clfSelect.appendChild(clfDefaultOption);

                // Add API info as data attributes
                clfSelect.setAttribute('data-api-type', 'clf');
                clfSelect.setAttribute('data-api-url', '/forms/api/clfs/');
                clfSelect.setAttribute('data-api-key', '18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf');
                clfSelect.setAttribute('data-api-client', 'in.co.glpc');

                fieldPreview.appendChild(clfSelect);

                // Add API info note
                const clfApiInfo = document.createElement('div');
                clfApiInfo.className = 'api-info';
                clfApiInfo.innerHTML = '<small>Data will be loaded from CLF API based on user\'s State and Block</small>';
                fieldPreview.appendChild(clfApiInfo);

                // Load CLFs if user location data is available
                if (userLocationData && userLocationData.state_id && userLocationData.block_id) {
                    // Show loading indicator
                    clfApiInfo.innerHTML = '<small>Loading CLFs...</small>';

                    // Fetch CLFs
                    fetchCLFs()
                        .then(clfs => {
                            // Clear existing options except the first one
                            while (clfSelect.options.length > 1) {
                                clfSelect.remove(1);
                            }

                            // Add CLFs to the dropdown
                            clfs.forEach(clf => {
                                const option = document.createElement('option');
                                const clfName = clf.clf_name || clf.name || '';
                                option.value = clfName.toLowerCase();
                                option.textContent = clfName;
                                clfSelect.appendChild(option);
                            });

                            // Update API info note
                            clfApiInfo.innerHTML = `<small>Loaded ${clfs.length} CLFs from API</small>`;
                        })
                        .catch(error => {
                            console.error('Error loading CLFs:', error);
                            clfApiInfo.innerHTML = '<small>Error loading CLFs. Please try again.</small>';
                        });
                }
                break;
        }

        field.appendChild(fieldPreview);

        // Add delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'delete-field-btn';
        deleteBtn.innerHTML = '&times;';
        // No onclick handler - using event delegation instead
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
        const fieldSettingsPanel = document.getElementById('fieldSettings');

        fieldSettingsPanel.innerHTML = `
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
            ${['village_list', 'shg_list', 'vo_list', 'clf_list'].includes(type) ? `
                <div class="settings-group">
                    <label>API Information</label>
                    <div class="api-info-settings">
                        ${type === 'village_list' ? `
                            <p>This field will load village data from:</p>
                            <code>/forms/api/villages/</code>
                            <p>Data will be automatically loaded based on the user's location.</p>
                            <p><strong>Note:</strong> The user must have state, district, and block information in their profile.</p>
                        ` : ''}
                        ${type === 'shg_list' ? `
                            <p>This field will load SHG data from:</p>
                            <code>/forms/api/shgs/</code>
                            <p>Data will be automatically loaded based on the user's location.</p>
                            <p><strong>Note:</strong> The user must have state and block information in their profile.</p>
                        ` : ''}
                        ${type === 'vo_list' ? `
                            <p>This field will load VO data from:</p>
                            <code>/forms/api/vos/</code>
                            <p>Data will be automatically loaded based on the user's location.</p>
                            <p><strong>Note:</strong> The user must have state and block information in their profile.</p>
                        ` : ''}
                        ${type === 'clf_list' ? `
                            <p>This field will load CLF data from:</p>
                            <code>/forms/api/clfs/</code>
                            <p>Data will be automatically loaded based on the user's location.</p>
                            <p><strong>Note:</strong> The user must have state and block information in their profile.</p>
                        ` : ''}
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
                window.updateFieldSetting(this, 'label');
            });
        }

        if (settingRequired) {
            settingRequired.addEventListener('change', function() {
                window.updateFieldSetting(this, 'required');
            });
        }

        if (settingPlaceholder) {
            settingPlaceholder.addEventListener('input', function() {
                window.updateFieldSetting(this, 'placeholder');
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

    // Single function to collect form data - make it globally accessible
    window.collectFormFields = function() {
        console.log('Collecting form fields');
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

            // Add accept attribute for file upload fields
            if (type === 'file') {
                fieldData.accept = '*/*'; // Accept all file types by default
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

            // Handle dynamic dropdown fields
            if (['village_list', 'shg_list', 'vo_list', 'clf_list'].includes(type)) {
                const dropdown = field.querySelector('.dynamic-dropdown');
                if (dropdown) {
                    // Add API information to the field data
                    fieldData.apiType = dropdown.getAttribute('data-api-type');
                    fieldData.apiUrl = dropdown.getAttribute('data-api-url');

                    // Add authentication info for SHG, VO, and CLF lists
                    if (['shg_list', 'vo_list', 'clf_list'].includes(type)) {
                        fieldData.apiKey = dropdown.getAttribute('data-api-key');
                        fieldData.apiClient = dropdown.getAttribute('data-api-client');
                    }
                }
            }

            fields.push(fieldData);
        });

        // Log the collected fields for debugging
        console.log('Collected fields:', fields);

        return fields;
    }

    // Function to get complete form data - make it globally accessible
    window.getFormData = function() {
        console.log('Getting form data');
        const formData = {
            title: document.getElementById('formTitle').value || 'Untitled Form',
            fields: collectFormFields()
        };

        // Log the complete form data for debugging
        console.log('Complete form data:', formData);

        return formData;
    }

    // Add notification function - make it globally accessible
    window.showNotification = function(message, type = 'success') {
        console.log('Showing notification:', message, 'type:', type);
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

            case 'file':
                return `
                    <input type="file"
                           class="form-input"
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

            case 'file':
                return `
                    <input type="file" class="form-input" accept="${field.accept || '*/*'}">
                `;

            case 'village_list':
                return `
                    <select class="form-input dynamic-dropdown" disabled>
                        <option value="">Select a Village (Will load dynamically)</option>
                    </select>
                    <div class="api-info-preview">
                        <small>Village data will be loaded dynamically based on user's location</small>
                    </div>
                `;

            case 'shg_list':
                return `
                    <select class="form-input dynamic-dropdown" disabled>
                        <option value="">Select an SHG (Will load dynamically)</option>
                    </select>
                    <div class="api-info-preview">
                        <small>SHG data will be loaded dynamically based on user's location</small>
                    </div>
                `;

            case 'vo_list':
                return `
                    <select class="form-input dynamic-dropdown" disabled>
                        <option value="">Select a VO (Will load dynamically)</option>
                    </select>
                    <div class="api-info-preview">
                        <small>VO data will be loaded dynamically based on user's location</small>
                    </div>
                `;

            case 'clf_list':
                return `
                    <select class="form-input dynamic-dropdown" disabled>
                        <option value="">Select a CLF (Will load dynamically)</option>
                    </select>
                    <div class="api-info-preview">
                        <small>CLF data will be loaded dynamically based on user's location</small>
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

            // First save the form to get a slug
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Save the form first
            const saveResponse = await fetch('/manager/forms/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(formData)
            });

            if (!saveResponse.ok) {
                throw new Error(`HTTP error during save! status: ${saveResponse.status}`);
            }

            const saveResult = await saveResponse.json();

            if (!saveResult.success) {
                throw new Error(saveResult.error || 'Failed to save form before publishing');
            }

            // Now publish the form using the slug
            const slug = saveResult.form_slug;
            console.log('Publishing form with slug:', slug);

            // Get the URL from the data-publish-url attribute if it exists, otherwise use the default
            const publishUrl = document.querySelector('.btn-publish').dataset.publishUrl || `/manager/forms/${slug}/publish/`;
            console.log('Publishing to URL:', publishUrl);

            // Submit using fetch to the correct publish endpoint
            const response = await fetch(publishUrl.replace('PLACEHOLDER', slug), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                showNotification(`Form "${formData.title}" published successfully!`, 'success');
                await wait(1000);
                redirectToUrl(result.redirect_url);
            } else {
                throw new Error(result.error || 'Failed to publish form');
            }

        } catch (error) {
            console.error('Publish error:', error);
            showNotification(error.message, 'error');
        }
    });

    function redirectToUrl(url) {
        window.location.href = url;
    }

    function wait(milliseconds) {
        return new Promise(resolve => setTimeout(resolve, milliseconds));
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

// This function is kept for backward compatibility but delegates to the click handler
function deleteField(btn) {
    // Simulate a click on the delete button
    if (btn) {
        const deleteBtn = btn.querySelector('.delete-field-btn') || btn.closest('.delete-field-btn');
        if (deleteBtn) {
            deleteBtn.click();
        } else {
            console.error('Delete button not found');
        }
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

        case 'file':
            return `<input type="file"
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

        case 'village_list':
            return `
                <select name="${field.label}"
                        class="form-select dynamic-dropdown"
                        data-api-type="village"
                        data-api-url="/forms/api/villages/"
                        ${field.required ? 'required' : ''}>
                    <option value="">Select a Village</option>
                    <!-- Options will be loaded dynamically -->
                </select>`;

        case 'shg_list':
            return `
                <select name="${field.label}"
                        class="form-select dynamic-dropdown"
                        data-api-type="shg"
                        data-api-url="/forms/api/shgs/"
                        data-api-key="18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf"
                        data-api-client="in.co.glpc"
                        ${field.required ? 'required' : ''}>
                    <option value="">Select an SHG</option>
                    <!-- Options will be loaded dynamically -->
                </select>`;

        case 'vo_list':
            return `
                <select name="${field.label}"
                        class="form-select dynamic-dropdown"
                        data-api-type="vo"
                        data-api-url="/forms/api/vos/"
                        data-api-key="18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf"
                        data-api-client="in.co.glpc"
                        ${field.required ? 'required' : ''}>
                    <option value="">Select a VO</option>
                    <!-- Options will be loaded dynamically -->
                </select>`;

        case 'clf_list':
            return `
                <select name="${field.label}"
                        class="form-select dynamic-dropdown"
                        data-api-type="clf"
                        data-api-url="/forms/api/clfs/"
                        data-api-key="18034065a7d2f7114df06cd7e6388ce677e536514fccd1e923fef0453ff26cbf"
                        data-api-client="in.co.glpc"
                        ${field.required ? 'required' : ''}>
                    <option value="">Select a CLF</option>
                    <!-- Options will be loaded dynamically -->
                </select>`;

        default:
            return '';
    }
}