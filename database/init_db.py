#!/usr/bin/env python3
"""
ForensicMeta - Database Initialization
Crea la base de datos SQLite con todas las tablas necesarias
"""
 
import sqlite3
import hashlib
import os
from datetime import datetime
 
DB_PATH = 'forensicmeta.db'
 
def init_database():
    """Inicializa la base de datos con todas las tablas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role VARCHAR(20) DEFAULT 'analyst',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabla de sesiones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla de archivos analizados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyzed_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_hash VARCHAR(64) NOT NULL,
            file_size INTEGER,
            file_type VARCHAR(50),
            upload_path TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla de metadatos extraídos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            metadata_key VARCHAR(100),
            metadata_value TEXT,
            category VARCHAR(50),
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES analyzed_files(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla de logs de actividad
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR(100) NOT NULL,
            description TEXT,
            ip_address VARCHAR(45),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    
    # Crear usuario administrador por defecto
    create_default_admin(cursor, conn)
    
    conn.close()
    print(f"✓ Base de datos inicializada: {DB_PATH}")
 
def create_default_admin(cursor, conn):
    """Crea un usuario administrador por defecto"""
    # Verificar si ya existe un admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        # Crear hash de contraseña (admin123)
        password = "admin123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@forensicmeta.local', password_hash, 
              'Administrator', 'admin'))
        
        conn.commit()
        print("✓ Usuario admin creado (username: admin, password: admin123)")
    else:
        print("✓ Usuario admin ya existe")
 
if __name__ == '__main__':
    init_database()
 
