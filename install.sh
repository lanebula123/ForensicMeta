#!/bin/bash

# ================================================
# ForensicMeta - Script de Instalación Automatizada
# ================================================

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║        🔍 FORENSICMETA - INSTALACIÓN                 ║"
echo "║        Análisis de Metadatos Forenses                ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${CYAN}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Verificar si estamos en Kali Linux
print_status "Verificando sistema operativo..."
if ! grep -qi "kali" /etc/os-release 2>/dev/null; then
    print_warning "Este script está optimizado para Kali Linux, pero puede funcionar en otras distribuciones Debian/Ubuntu"
fi
print_success "Sistema compatible"

# Actualizar repositorios
print_status "Actualizando repositorios del sistema..."
sudo apt update > /dev/null 2>&1
print_success "Repositorios actualizados"

# Instalar Python 3 y pip
print_status "Instalando Python 3 y pip..."
sudo apt install -y python3 python3-pip > /dev/null 2>&1
print_success "Python 3 instalado: $(python3 --version)"

# Instalar ExifTool
print_status "Instalando ExifTool (herramienta forense)..."
sudo apt install -y libimage-exiftool-perl > /dev/null 2>&1
print_success "ExifTool instalado: $(exiftool -ver)"

# Instalar libmagic
print_status "Instalando libmagic (detección de tipos de archivo)..."
sudo apt install -y libmagic1 > /dev/null 2>&1
print_success "libmagic instalado"

# Instalar dependencias de Python
print_status "Instalando dependencias de Python..."
pip3 install flask flask-cors pyexiftool python-magic --break-system-packages --quiet
print_success "Dependencias de Python instaladas"

# Inicializar base de datos
print_status "Inicializando base de datos..."
cd database
python3 init_db.py
cd ..
print_success "Base de datos inicializada"

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║        ✅ INSTALACIÓN COMPLETADA                      ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

print_success "ForensicMeta está listo para usar"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}📋 PASOS PARA EJECUTAR LA APLICACIÓN:${NC}"
echo ""
echo "1. Iniciar el Backend (en una terminal):"
echo -e "   ${YELLOW}cd backend && python3 app.py${NC}"
echo ""
echo "2. Iniciar el Frontend (en OTRA terminal):"
echo -e "   ${YELLOW}cd frontend && python3 -m http.server 8080${NC}"
echo ""
echo "3. Abrir en el navegador:"
echo -e "   ${YELLOW}http://localhost:8080${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}🔑 CREDENCIALES POR DEFECTO:${NC}"
echo -e "   Usuario:    ${GREEN}admin${NC}"
echo -e "   Contraseña: ${GREEN}admin123${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}💡 TIP:${NC} Lee el archivo README.md para más información"
echo ""
