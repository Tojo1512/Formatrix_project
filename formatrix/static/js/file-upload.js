/**
 * Script pour gu00e9rer les uploads de fichiers avec drag & drop
 */
document.addEventListener('DOMContentLoaded', function() {
  // Gu00e9rer l'upload de CV
  setupFileUpload('cv');
  
  // Gu00e9rer l'upload de photo
  setupImageUpload('photo');
});

/**
 * Configure l'upload de fichier standard
 * @param {string} fieldName - Nom du champ (cv)
 */
function setupFileUpload(fieldName) {
  const uploadBox = document.getElementById(`${fieldName}-upload-box`);
  const fileInput = document.getElementById(`id_${fieldName}`);
  const fileInfo = document.getElementById(`${fieldName}-file-info`);
  const fileName = document.getElementById(`${fieldName}-file-name`);
  const removeButton = document.getElementById(`${fieldName}-remove-file`);
  
  if (!uploadBox || !fileInput) return;
  
  // Vu00e9rifier si un fichier est du00e9ju00e0 su00e9lectionnu00e9
  if (fileInput.files && fileInput.files[0]) {
    showFileInfo(fieldName, fileInput.files[0].name);
  }
  
  // Cliquer sur la bou00eete ouvre le su00e9lecteur de fichier
  uploadBox.addEventListener('click', function(e) {
    if (e.target !== removeButton && e.target !== removeButton.querySelector('i')) {
      fileInput.click();
    }
  });
  
  // Gu00e9rer le changement de fichier
  fileInput.addEventListener('change', function() {
    if (fileInput.files && fileInput.files[0]) {
      showFileInfo(fieldName, fileInput.files[0].name);
    } else {
      hideFileInfo(fieldName);
    }
  });
  
  // Gu00e9rer le glisser-du00e9poser
  uploadBox.addEventListener('dragover', function(e) {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
  });
  
  uploadBox.addEventListener('dragleave', function() {
    uploadBox.classList.remove('drag-over');
  });
  
  uploadBox.addEventListener('drop', function(e) {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      fileInput.files = e.dataTransfer.files;
      showFileInfo(fieldName, e.dataTransfer.files[0].name);
      
      // Du00e9clencher l'u00e9vu00e9nement change pour que le formulaire du00e9tecte le changement
      const event = new Event('change', { bubbles: true });
      fileInput.dispatchEvent(event);
    }
  });
  
  // Supprimer le fichier
  if (removeButton) {
    removeButton.addEventListener('click', function(e) {
      e.stopPropagation();
      fileInput.value = '';
      hideFileInfo(fieldName);
      
      // Du00e9clencher l'u00e9vu00e9nement change
      const event = new Event('change', { bubbles: true });
      fileInput.dispatchEvent(event);
    });
  }
}

/**
 * Configure l'upload d'image avec pru00e9visualisation
 * @param {string} fieldName - Nom du champ (photo)
 */
function setupImageUpload(fieldName) {
  const uploadBox = document.getElementById(`${fieldName}-upload-box`);
  const fileInput = document.getElementById(`id_${fieldName}`);
  const preview = document.getElementById(`${fieldName}-preview`);
  
  if (!uploadBox || !fileInput || !preview) return;
  
  // Vu00e9rifier si une image est du00e9ju00e0 su00e9lectionnu00e9e
  if (fileInput.files && fileInput.files[0]) {
    showImagePreview(preview, fileInput.files[0]);
    uploadBox.classList.add('has-file');
  }
  
  // Cliquer sur la bou00eete ouvre le su00e9lecteur de fichier
  uploadBox.addEventListener('click', function() {
    fileInput.click();
  });
  
  // Gu00e9rer le changement d'image
  fileInput.addEventListener('change', function() {
    if (fileInput.files && fileInput.files[0]) {
      showImagePreview(preview, fileInput.files[0]);
      uploadBox.classList.add('has-file');
    } else {
      resetImagePreview(preview);
      uploadBox.classList.remove('has-file');
    }
  });
  
  // Gu00e9rer le glisser-du00e9poser
  uploadBox.addEventListener('dragover', function(e) {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
  });
  
  uploadBox.addEventListener('dragleave', function() {
    uploadBox.classList.remove('drag-over');
  });
  
  uploadBox.addEventListener('drop', function(e) {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      
      // Vu00e9rifier si c'est une image
      if (file.type.match('image.*')) {
        fileInput.files = e.dataTransfer.files;
        showImagePreview(preview, file);
        uploadBox.classList.add('has-file');
        
        // Du00e9clencher l'u00e9vu00e9nement change
        const event = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(event);
      }
    }
  });
}

/**
 * Affiche les informations du fichier su00e9lectionnu00e9
 * @param {string} fieldName - Nom du champ
 * @param {string} name - Nom du fichier
 */
function showFileInfo(fieldName, name) {
  const uploadBox = document.getElementById(`${fieldName}-upload-box`);
  const fileName = document.getElementById(`${fieldName}-file-name`);
  
  if (uploadBox && fileName) {
    fileName.textContent = name;
    uploadBox.classList.add('has-file');
  }
}

/**
 * Cache les informations du fichier
 * @param {string} fieldName - Nom du champ
 */
function hideFileInfo(fieldName) {
  const uploadBox = document.getElementById(`${fieldName}-upload-box`);
  const fileName = document.getElementById(`${fieldName}-file-name`);
  
  if (uploadBox && fileName) {
    fileName.textContent = 'Aucun fichier su00e9lectionnu00e9';
    uploadBox.classList.remove('has-file');
  }
}

/**
 * Affiche la pru00e9visualisation de l'image
 * @param {HTMLElement} preview - u00c9lu00e9ment de pru00e9visualisation
 * @param {File} file - Fichier image
 */
function showImagePreview(preview, file) {
  if (!preview) return;
  
  // Vider l'u00e9lu00e9ment de pru00e9visualisation
  preview.innerHTML = '';
  
  // Cru00e9er l'u00e9lu00e9ment d'image
  const img = document.createElement('img');
  img.file = file;
  preview.appendChild(img);
  
  // Lire le fichier et du00e9finir la source de l'image
  const reader = new FileReader();
  reader.onload = (function(aImg) { 
    return function(e) { 
      aImg.src = e.target.result; 
    }; 
  })(img);
  reader.readAsDataURL(file);
}

/**
 * Ru00e9initialise la pru00e9visualisation de l'image
 * @param {HTMLElement} preview - u00c9lu00e9ment de pru00e9visualisation
 */
function resetImagePreview(preview) {
  if (!preview) return;
  
  preview.innerHTML = '<i class="fas fa-user-circle placeholder-icon"></i>';
}
