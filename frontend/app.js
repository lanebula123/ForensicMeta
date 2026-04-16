// ================================================
// FORENSICMETA - JAVASCRIPT PRINCIPAL
// ================================================

const API_URL = 'http://localhost:5000/api';
let currentUser = null;
let sessionToken = null;

// ================================================
// FONDO ANIMADO - MATRIZ
// ================================================

const canvas = document.getElementById('matrix-bg');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const matrix = "FORENSICMETA0123456789ABCDEF";
const fontSize = 14;
const columns = canvas.width / fontSize;

const drops = [];
for (let x = 0; x < columns; x++) {
    drops[x] = Math.random() * canvas.height;
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(10, 14, 26, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#00f0ff';
    ctx.font = fontSize + 'px monospace';
    
    for (let i = 0; i < drops.length; i++) {
        const text = matrix.charAt(Math.floor(Math.random() * matrix.length));
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        
        drops[i]++;
    }
}

setInterval(drawMatrix, 50);

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// ================================================
// NAVEGACIÓN ENTRE PÁGINAS
// ================================================

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
}

// ================================================
// VALIDACIÓN DE FORMULARIOS
// ================================================

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showValidation(inputId, message, isValid) {
    const validationEl = document.getElementById(`${inputId}-validation`);
    validationEl.textContent = message;
    validationEl.className = 'validation-msg ' + (isValid ? 'success' : 'error');
}

// ================================================
// LOGIN
// ================================================

const loginForm = document.getElementById('login-form');
const loginBtn = document.getElementById('login-btn');
const loginError = document.getElementById('login-error');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    // Validación frontend
    if (!username) {
        showValidation('username', '✗ El usuario es requerido', false);
        return;
    } else {
        showValidation('username', '', true);
    }
    
    if (!password) {
        showValidation('password', '✗ La contraseña es requerida', false);
        return;
    } else {
        showValidation('password', '', true);
    }
    
    // Mostrar loading
    loginBtn.querySelector('.btn-text').style.display = 'none';
    loginBtn.querySelector('.btn-loading').style.display = 'flex';
    loginBtn.disabled = true;
    loginError.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Login exitoso
            currentUser = data.user;
            sessionToken = data.session_token;
            
            // Guardar en localStorage
            localStorage.setItem('sessionToken', sessionToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            // Ir al dashboard
            showPage('dashboard-page');
            loadDashboard();
        } else {
            // Error de login
            loginError.textContent = data.error || 'Error al iniciar sesión';
            loginError.style.display = 'block';
        }
    } catch (error) {
        loginError.textContent = 'Error de conexión. Asegúrate de que el servidor esté corriendo.';
        loginError.style.display = 'block';
    } finally {
        loginBtn.querySelector('.btn-text').style.display = 'inline';
        loginBtn.querySelector('.btn-loading').style.display = 'none';
        loginBtn.disabled = false;
    }
});

// ================================================
// REGISTRO
// ================================================

const showRegisterBtn = document.getElementById('show-register-btn');
const backToLoginBtn = document.getElementById('back-to-login-btn');
const registerForm = document.getElementById('register-form');
const registerBtn = document.getElementById('register-btn');
const registerError = document.getElementById('register-error');
const registerSuccess = document.getElementById('register-success');

showRegisterBtn.addEventListener('click', () => {
    showPage('register-page');
});

backToLoginBtn.addEventListener('click', () => {
    showPage('login-page');
    registerForm.reset();
    registerError.style.display = 'none';
    registerSuccess.style.display = 'none';
});

// Validación en tiempo real
const regUsername = document.getElementById('reg-username');
const regEmail = document.getElementById('reg-email');
const regPassword = document.getElementById('reg-password');
const regPasswordConfirm = document.getElementById('reg-password-confirm');

regUsername.addEventListener('blur', () => {
    if (regUsername.value.length < 3) {
        showValidation('reg-username', '✗ Mínimo 3 caracteres', false);
    } else {
        showValidation('reg-username', '✓ Usuario válido', true);
    }
});

regEmail.addEventListener('blur', () => {
    if (!validateEmail(regEmail.value)) {
        showValidation('reg-email', '✗ Email inválido', false);
    } else {
        showValidation('reg-email', '✓ Email válido', true);
    }
});

regPassword.addEventListener('blur', () => {
    if (regPassword.value.length < 6) {
        showValidation('reg-password', '✗ Mínimo 6 caracteres', false);
    } else {
        showValidation('reg-password', '✓ Contraseña válida', true);
    }
});

regPasswordConfirm.addEventListener('blur', () => {
    if (regPasswordConfirm.value !== regPassword.value) {
        showValidation('reg-password-confirm', '✗ Las contraseñas no coinciden', false);
    } else {
        showValidation('reg-password-confirm', '✓ Contraseñas coinciden', true);
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = regUsername.value.trim();
    const email = regEmail.value.trim();
    const password = regPassword.value;
    const passwordConfirm = regPasswordConfirm.value;
    const fullName = document.getElementById('reg-fullname').value.trim();
    
    // Validación final
    if (username.length < 3) {
        showValidation('reg-username', '✗ Mínimo 3 caracteres', false);
        return;
    }
    
    if (!validateEmail(email)) {
        showValidation('reg-email', '✗ Email inválido', false);
        return;
    }
    
    if (password.length < 6) {
        showValidation('reg-password', '✗ Mínimo 6 caracteres', false);
        return;
    }
    
    if (password !== passwordConfirm) {
        showValidation('reg-password-confirm', '✗ Las contraseñas no coinciden', false);
        return;
    }
    
    // Mostrar loading
    registerBtn.querySelector('.btn-text').style.display = 'none';
    registerBtn.querySelector('.btn-loading').style.display = 'flex';
    registerBtn.disabled = true;
    registerError.style.display = 'none';
    registerSuccess.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password, full_name: fullName }),
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            registerSuccess.textContent = '✓ Cuenta creada exitosamente. Redirigiendo al login...';
            registerSuccess.style.display = 'block';
            
            setTimeout(() => {
                showPage('login-page');
                registerForm.reset();
                registerSuccess.style.display = 'none';
            }, 2000);
        } else {
            registerError.textContent = data.error || 'Error al crear la cuenta';
            registerError.style.display = 'block';
        }
    } catch (error) {
        registerError.textContent = 'Error de conexión. Asegúrate de que el servidor esté corriendo.';
        registerError.style.display = 'block';
    } finally {
        registerBtn.querySelector('.btn-text').style.display = 'inline';
        registerBtn.querySelector('.btn-loading').style.display = 'none';
        registerBtn.disabled = false;
    }
});

// ================================================
// LOGOUT
// ================================================

document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch(`${API_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
            },
        });
    } catch (error) {
        console.error('Error al cerrar sesión:', error);
    }
    
    // Limpiar sesión
    localStorage.removeItem('sessionToken');
    localStorage.removeItem('currentUser');
    currentUser = null;
    sessionToken = null;
    
    // Volver al login
    showPage('login-page');
    loginForm.reset();
});

// ================================================
// DASHBOARD
// ================================================

async function loadDashboard() {
    // Actualizar información del usuario
    document.getElementById('user-name').textContent = currentUser.full_name || currentUser.username;
    document.getElementById('user-role').textContent = currentUser.role.toUpperCase();
    
    // Cargar historial
    await loadHistory();
}

// ================================================
// ANÁLISIS DE ARCHIVOS
// ================================================

const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const uploadProgress = document.getElementById('upload-progress');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultsSection = document.getElementById('results-section');

// Click para seleccionar archivo
uploadZone.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragging');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragging');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragging');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

async function handleFileUpload(file) {
    // Validar tamaño (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
        alert('El archivo es demasiado grande. Máximo 50MB.');
        return;
    }
    
    // Mostrar progreso
    uploadProgress.style.display = 'block';
    resultsSection.style.display = 'none';
    progressFill.style.width = '0%';
    progressText.textContent = 'Subiendo archivo...';
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Simular progreso de subida
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                progressFill.style.width = progress + '%';
            }
        }, 200);
        
        const response = await fetch(`${API_URL}/analyze/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
            },
            body: formData,
        });
        
        clearInterval(progressInterval);
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Completar progreso
            progressFill.style.width = '100%';
            progressText.textContent = '✓ Análisis completado';
            
            setTimeout(() => {
                uploadProgress.style.display = 'none';
                displayResults(data);
                loadHistory(); // Recargar historial
            }, 1000);
        } else {
            alert('Error al analizar el archivo: ' + (data.error || 'Error desconocido'));
            uploadProgress.style.display = 'none';
        }
    } catch (error) {
        alert('Error de conexión: ' + error.message);
        uploadProgress.style.display = 'none';
    }
    
    // Limpiar input
    fileInput.value = '';
}

function displayResults(data) {
    resultsSection.style.display = 'block';
    
    // Información del archivo
    document.getElementById('result-filename').textContent = data.filename;
    document.getElementById('result-hash').textContent = data.file_hash;
    document.getElementById('result-size').textContent = formatBytes(data.file_size);
    document.getElementById('result-type').textContent = data.file_type;
    
    // Metadatos
    const metadataContainer = document.getElementById('metadata-container');
    metadataContainer.innerHTML = '';
    
    if (data.metadata && Object.keys(data.metadata).length > 0) {
        for (const [category, items] of Object.entries(data.metadata)) {
            if (items.length > 0) {
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'metadata-category';
                
                const header = document.createElement('div');
                header.className = 'category-header';
                header.innerHTML = `
                    ${category}
                    <span class="category-count">${items.length} items</span>
                `;
                
                const itemsDiv = document.createElement('div');
                itemsDiv.className = 'metadata-items';
                
                items.forEach(item => {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'metadata-item';
                    itemDiv.innerHTML = `
                        <div class="metadata-key">${item.key}</div>
                        <div class="metadata-value">${item.value}</div>
                    `;
                    itemsDiv.appendChild(itemDiv);
                });
                
                categoryDiv.appendChild(header);
                categoryDiv.appendChild(itemsDiv);
                metadataContainer.appendChild(categoryDiv);
                
                // Toggle collapse
                header.addEventListener('click', () => {
                    itemsDiv.style.display = itemsDiv.style.display === 'none' ? 'block' : 'none';
                });
            }
        }
    } else {
        metadataContainer.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No se encontraron metadatos</p>';
    }
    
    // Scroll a resultados
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ================================================
// HISTORIAL
// ================================================

async function loadHistory() {
    try {
        const response = await fetch(`${API_URL}/analyze/history`, {
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayHistory(data.files);
            updateStats(data.files);
        }
    } catch (error) {
        console.error('Error al cargar historial:', error);
    }
}

function displayHistory(files) {
    const historyTable = document.getElementById('history-table');
    
    if (files.length === 0) {
        historyTable.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No hay archivos analizados</p>';
        return;
    }
    
    historyTable.innerHTML = '';
    
    files.forEach(file => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="history-header">
                <div class="history-filename">${file.filename}</div>
                <div class="history-date">${formatDate(file.analyzed_at)}</div>
            </div>
            <div class="history-details">
                <div class="detail-item">
                    <strong>Hash:</strong> ${file.file_hash.substring(0, 16)}...
                </div>
                <div class="detail-item">
                    <strong>Tamaño:</strong> ${formatBytes(file.file_size)}
                </div>
                <div class="detail-item">
                    <strong>Tipo:</strong> ${file.file_type}
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => loadFileDetails(file.id));
        historyTable.appendChild(item);
    });
}

async function loadFileDetails(fileId) {
    try {
        const response = await fetch(`${API_URL}/analyze/details/${fileId}`, {
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayResults({
                filename: data.file.filename,
                file_hash: data.file.file_hash,
                file_size: data.file.file_size,
                file_type: data.file.file_type,
                metadata: data.metadata,
            });
        }
    } catch (error) {
        console.error('Error al cargar detalles:', error);
    }
}

function updateStats(files) {
    document.getElementById('total-files').textContent = files.length;
    
    // Contar metadatos totales (estimado)
    const totalMetadata = files.length * 15; // Promedio estimado
    document.getElementById('total-metadata').textContent = totalMetadata;
    
    // Análisis de hoy
    const today = new Date().toDateString();
    const todayAnalysis = files.filter(f => {
        const fileDate = new Date(f.analyzed_at).toDateString();
        return fileDate === today;
    }).length;
    document.getElementById('today-analysis').textContent = todayAnalysis;
}

// ================================================
// UTILIDADES
// ================================================

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('es-ES', options);
}

// ================================================
// INICIALIZACIÓN
// ================================================

window.addEventListener('load', () => {
    // Verificar sesión guardada
    const savedToken = localStorage.getItem('sessionToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        sessionToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showPage('dashboard-page');
        loadDashboard();
    } else {
        showPage('login-page');
    }
});
