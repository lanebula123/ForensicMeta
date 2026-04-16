#!/usr/bin/env python3
"""
ForensicMeta - Backend API
API REST con Flask para análisis de metadatos forenses
"""
 
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import exiftool
import magic
 
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True, origins=['http://localhost:8080', 'http://127.0.0.1:8080'])
 
# Configuración
DB_PATH = '../database/forensicmeta.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'docx', 'xlsx', 'mp4', 'avi', 'mp3'}
 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
 
# ============================================
# UTILIDADES
# ============================================
 
def get_db():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
def hash_password(password):
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()
 
def generate_session_token():
    """Genera un token de sesión seguro"""
    return secrets.token_urlsafe(32)
 
def log_activity(user_id, action, description, ip_address):
    """Registra actividad del usuario"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity_logs (user_id, action, description, ip_address)
        VALUES (?, ?, ?, ?)
    ''', (user_id, action, description, ip_address))
    conn.commit()
    conn.close()
 
def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
# ============================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================
 
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validación básica
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
        
        # Buscar usuario
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
        user = cursor.fetchone()
        
        if not user:
            log_activity(None, 'LOGIN_FAILED', f'Intento fallido: {username}', request.remote_addr)
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Verificar contraseña
        password_hash = hash_password(password)
        if user['password_hash'] != password_hash:
            log_activity(user['id'], 'LOGIN_FAILED', 'Contraseña incorrecta', request.remote_addr)
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Crear sesión
        session_token = generate_session_token()
        expires_at = datetime.now() + timedelta(hours=24)
        
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, ip_address, user_agent, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user['id'], session_token, request.remote_addr, 
              request.headers.get('User-Agent'), expires_at))
        
        # Actualizar last_login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                      (datetime.now(), user['id']))
        
        conn.commit()
        conn.close()
        
        log_activity(user['id'], 'LOGIN_SUCCESS', 'Login exitoso', request.remote_addr)
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Endpoint de logout"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET is_active = 0 WHERE session_token = ?', (token,))
            conn.commit()
            conn.close()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Endpoint de registro de nuevos usuarios"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validaciones
        if not all([username, email, password]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        # Verificar si el usuario ya existe
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        
        if cursor.fetchone():
            return jsonify({'error': 'Usuario o email ya existe'}), 409
        
        # Crear usuario
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, 'analyst'))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        log_activity(user_id, 'USER_REGISTERED', 'Nuevo usuario registrado', request.remote_addr)
        
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
# ============================================
# ENDPOINTS DE ANÁLISIS DE METADATOS
# ============================================
 
@app.route('/api/analyze/upload', methods=['POST'])
def upload_file():
    """Endpoint para subir y analizar archivo"""
    try:
        # Verificar token de sesión
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token de sesión requerido'}), 401
        
        # Validar sesión
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, u.username FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? AND s.is_active = 1 AND s.expires_at > ?
        ''', (token, datetime.now()))
        
        session_data = cursor.fetchone()
        
        if not session_data:
            return jsonify({'error': 'Sesión inválida o expirada'}), 401
        
        user_id = session_data['user_id']
        
        # Verificar archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Calcular hash del archivo
        with open(filepath, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        file_size = os.path.getsize(filepath)
        
        # Detectar tipo MIME
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(filepath)
        
        # Guardar en base de datos
        cursor.execute('''
            INSERT INTO analyzed_files (user_id, filename, file_hash, file_size, file_type, upload_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, filename, file_hash, file_size, file_type, filepath))
        
        file_id = cursor.lastrowid
        conn.commit()
        
        # Extraer metadatos usando ExifTool
        metadata = extract_metadata(filepath, file_id, cursor, conn)
        
        conn.close()
        
        log_activity(user_id, 'FILE_ANALYZED', f'Archivo analizado: {filename}', request.remote_addr)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'file_hash': file_hash,
            'file_size': file_size,
            'file_type': file_type,
            'metadata': metadata
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
def extract_metadata(filepath, file_id, cursor, conn):
    """Extrae metadatos del archivo usando ExifTool"""
    try:
        metadata = {}
        
        # Usar ExifTool para extraer metadatos
        with exiftool.ExifToolHelper() as et:
            meta_list = et.get_metadata(filepath)
            
            if meta_list:
                meta_dict = meta_list[0]
                
                # Categorizar metadatos
                categories = {
                    'File': [],
                    'EXIF': [],
                    'GPS': [],
                    'ICC_Profile': [],
                    'XMP': [],
                    'Other': []
                }
                
                for key, value in meta_dict.items():
                    # Determinar categoría
                    if key.startswith('File:'):
                        category = 'File'
                    elif key.startswith('EXIF:'):
                        category = 'EXIF'
                    elif key.startswith('GPS:'):
                        category = 'GPS'
                    elif key.startswith('ICC_Profile:'):
                        category = 'ICC_Profile'
                    elif key.startswith('XMP:'):
                        category = 'XMP'
                    else:
                        category = 'Other'
                    
                    # Guardar en base de datos
                    cursor.execute('''
                        INSERT INTO metadata_results (file_id, metadata_key, metadata_value, category)
                        VALUES (?, ?, ?, ?)
                    ''', (file_id, key, str(value), category))
                    
                    categories[category].append({
                        'key': key,
                        'value': str(value)
                    })
                
                conn.commit()
                metadata = categories
        
        return metadata
        
    except Exception as e:
        print(f"Error extrayendo metadatos: {e}")
        return {}
 
@app.route('/api/analyze/history', methods=['GET'])
def get_analysis_history():
    """Obtiene el historial de análisis del usuario"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token de sesión requerido'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Validar sesión
        cursor.execute('''
            SELECT user_id FROM sessions
            WHERE session_token = ? AND is_active = 1 AND expires_at > ?
        ''', (token, datetime.now()))
        
        session_data = cursor.fetchone()
        
        if not session_data:
            return jsonify({'error': 'Sesión inválida'}), 401
        
        user_id = session_data['user_id']
        
        # Obtener historial
        cursor.execute('''
            SELECT id, filename, file_hash, file_size, file_type, analyzed_at
            FROM analyzed_files
            WHERE user_id = ?
            ORDER BY analyzed_at DESC
            LIMIT 50
        ''', (user_id,))
        
        files = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'files': [dict(f) for f in files]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/api/analyze/details/<int:file_id>', methods=['GET'])
def get_file_details(file_id):
    """Obtiene detalles completos de un archivo analizado"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token de sesión requerido'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Validar sesión
        cursor.execute('''
            SELECT user_id FROM sessions
            WHERE session_token = ? AND is_active = 1 AND expires_at > ?
        ''', (token, datetime.now()))
        
        session_data = cursor.fetchone()
        
        if not session_data:
            return jsonify({'error': 'Sesión inválida'}), 401
        
        user_id = session_data['user_id']
        
        # Obtener información del archivo
        cursor.execute('''
            SELECT * FROM analyzed_files
            WHERE id = ? AND user_id = ?
        ''', (file_id, user_id))
        
        file_data = cursor.fetchone()
        
        if not file_data:
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Obtener metadatos
        cursor.execute('''
            SELECT metadata_key, metadata_value, category
            FROM metadata_results
            WHERE file_id = ?
        ''', (file_id,))
        
        metadata_rows = cursor.fetchall()
        conn.close()
        
        # Organizar metadatos por categoría
        metadata = {}
        for row in metadata_rows:
            category = row['category']
            if category not in metadata:
                metadata[category] = []
            metadata[category].append({
                'key': row['metadata_key'],
                'value': row['metadata_value']
            })
        
        return jsonify({
            'success': True,
            'file': dict(file_data),
            'metadata': metadata
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
# ============================================
# ENDPOINT DE ESTADO
# ============================================
 
@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint de verificación de estado"""
    return jsonify({
        'status': 'online',
        'service': 'ForensicMeta API',
        'version': '1.0.0'
    }), 200
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 
