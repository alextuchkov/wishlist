function toggleButtons() {
    const editBtn = document.getElementById('editDetailsBtn');
    const saveBtn = document.getElementById('saveChangesBtn');

    if (editBtn.style.display !== 'none') {
        // If Edit button is visible, hide it and show Save Changes button
        editBtn.style.display = 'none';
        saveBtn.style.display = 'block';

        // Enable form elements and copy placeholder to value
        const formElements = document.getElementById('editForm').elements;
        for (let i = 0; i < formElements.length; i++) {
            const placeholder = formElements[i].getAttribute('placeholder');
            formElements[i].value = placeholder;
            formElements[i].disabled = false;
        }
    } else {
        // If Save Changes button is visible, hide it and show Edit button
        editBtn.style.display = 'block';
        saveBtn.style.display = 'none';

        // Disable form elements
        const formElements = document.getElementById('editForm').elements;
        for (let i = 0; i < formElements.length; i++) {
            formElements[i].disabled = true;
        }
    }
}