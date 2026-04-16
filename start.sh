#!/bin/bash

# ================================================
# ForensicMeta - Script de Inicio Rápido
# ================================================

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║        🚀 FORENSICMETA - INICIANDO SERVICIOS         ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}[*]${NC} Iniciando Backend (Flask API)..."
cd backend
python3 app.py > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

echo -e "${GREEN}[✓]${NC} Backend ejecutándose en http://localhost:5000 (PID: $BACKEND_PID)"

echo -e "${CYAN}[*]${NC} Iniciando Frontend (HTTP Server)..."
cd frontend
python3 -m http.server 8080 > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2

echo -e "${GREEN}[✓]${NC} Frontend ejecutándose en http://localhost:8080 (PID: $FRONTEND_PID)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ ForensicMeta está ejecutándose${NC}"
echo ""
echo -e "${CYAN}🌐 Accede a la aplicación:${NC}"
echo -e "   ${YELLOW}http://localhost:8080${NC}"
echo ""
echo -e "${CYAN}🔑 Credenciales:${NC}"
echo -e "   Usuario:    ${GREEN}admin${NC}"
echo -e "   Contraseña: ${GREEN}admin123${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚠️  Para detener los servicios, presiona Ctrl+C${NC}"
echo ""

# Guardar PIDs en archivo para poder detenerlos después
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Función para limpiar al salir
cleanup() {
    echo ""
    echo -e "${CYAN}[*]${NC} Deteniendo servicios..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    rm -f .backend.pid .frontend.pid
    echo -e "${GREEN}[✓]${NC} Servicios detenidos"
    exit 0
}

# Capturar Ctrl+C
trap cleanup INT TERM

# Mantener el script corriendo
wait
