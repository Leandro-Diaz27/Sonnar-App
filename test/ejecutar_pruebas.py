#!/usr/bin/env python
"""
Script para ejecutar todas las pruebas del proyecto Sonnar
Genera reportes detallados y estadísticas de cobertura
"""
import subprocess
import sys
import os
from datetime import datetime


def print_header(text):
    """Imprime un encabezado con formato"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔄 {description}...")
    print(f"   Comando: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        print(result.stdout)
        if result.stderr:
            print("⚠️  Advertencias/Errores:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error al ejecutar: {e}")
        return False


def main():
    """Función principal para ejecutar todas las pruebas"""
    
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print_header("🧪 EJECUCIÓN DE PRUEBAS - SONNAR APP")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Directorio: {script_dir}\n")
    
    # Verificar que pytest está instalado
    try:
        import pytest
        print(f"✅ pytest versión: {pytest.__version__}")
    except ImportError:
        print("❌ pytest no está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    resultados = {}
    
    # 1. Ejecutar todas las pruebas con detalle
    print_header("1️⃣  EJECUTANDO TODAS LAS PRUEBAS")
    success = run_command(
        [sys.executable, "-m", "pytest", "-v", "--tb=short"],
        "Ejecutar suite completa de pruebas"
    )
    resultados["todas"] = success
    
    # 2. Ejecutar pruebas unitarias
    print_header("2️⃣  EJECUTANDO PRUEBAS UNITARIAS")
    success = run_command(
        [sys.executable, "-m", "pytest", "-v", "-m", "unit", "--tb=short"],
        "Ejecutar solo pruebas unitarias"
    )
    resultados["unitarias"] = success
    
    # 3. Ejecutar pruebas de integración
    print_header("3️⃣  EJECUTANDO PRUEBAS DE INTEGRACIÓN")
    success = run_command(
        [sys.executable, "-m", "pytest", "-v", "-m", "integration", "--tb=short"],
        "Ejecutar solo pruebas de integración"
    )
    resultados["integracion"] = success
    
    # 4. Ejecutar pruebas funcionales
    print_header("4️⃣  EJECUTANDO PRUEBAS FUNCIONALES")
    success = run_command(
        [sys.executable, "-m", "pytest", "-v", "-m", "functional", "--tb=short"],
        "Ejecutar solo pruebas funcionales"
    )
    resultados["funcionales"] = success
    
    # 5. Generar reporte de cobertura
    print_header("5️⃣  GENERANDO REPORTE DE COBERTURA")
    run_command(
        [sys.executable, "-m", "pytest", "--cov=../main", "--cov-report=term", 
         "--cov-report=html:coverage_html"],
        "Generar reporte de cobertura de código"
    )
    
    # 6. Guardar resultados en archivo
    print_header("6️⃣  GUARDANDO RESULTADOS EN ARCHIVO")
    result_file = "resultados_testing.txt"
    with open(result_file, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("  RESULTADOS DE PRUEBAS - SONNAR APP\n")
        f.write("="*70 + "\n")
        f.write(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Directorio: {script_dir}\n\n")
        
        # Ejecutar pytest y capturar salida
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            capture_output=True,
            text=True
        )
        f.write(result.stdout)
        if result.stderr:
            f.write("\n\nAdvertencias/Errores:\n")
            f.write(result.stderr)
    
    print(f"✅ Resultados guardados en: {result_file}")
    
    # 7. Resumen final
    print_header("📊 RESUMEN DE EJECUCIÓN")
    
    print("Resultados por categoría:")
    print(f"  {'Todas las pruebas':<25} {'✅ EXITOSO' if resultados.get('todas') else '❌ FALLÓ'}")
    print(f"  {'Pruebas unitarias':<25} {'✅ EXITOSO' if resultados.get('unitarias') else '❌ FALLÓ'}")
    print(f"  {'Pruebas de integración':<25} {'✅ EXITOSO' if resultados.get('integracion') else '❌ FALLÓ'}")
    print(f"  {'Pruebas funcionales':<25} {'✅ EXITOSO' if resultados.get('funcionales') else '❌ FALLÓ'}")
    
    print("\nArchivos generados:")
    print(f"  📄 {result_file}")
    print(f"  📊 coverage_html/index.html (reporte visual de cobertura)")
    
    # Determinar código de salida
    all_passed = all(resultados.values())
    
    if all_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        return 0
    else:
        print("\n⚠️  ALGUNAS PRUEBAS FALLARON. Revisa los detalles arriba.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

