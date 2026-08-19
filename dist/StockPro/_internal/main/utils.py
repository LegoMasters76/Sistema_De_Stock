import hashlib

SECRET_SALT = "RENZO_STOCK_SECURE_2026"

def generar_hash(texto):
    """Genera un hash simple a partir de un texto."""
    return hashlib.sha256(f"{texto}{SECRET_SALT}".encode()).hexdigest()[:8].upper()

def validar_serial(serial):
    """
    Valida si un serial tiene el formato correcto.
    El formato esperado es: RZ-XXXX-YYYY
    Donde YYYY es el hash generado a partir de XXXX.
    """
    if not serial or not isinstance(serial, str):
        return False
    
    partes = serial.strip().split('-')
    
    if len(partes) != 3 or partes[0] != "RZ":
        # Formato de backup simple: 'RENZO-STOCK-PRO'
        return serial.strip() == "RENZO-STOCK-PRO"
        
    codigo_base = partes[1]
    hash_esperado = partes[2]
    
    hash_calculado = generar_hash(codigo_base)
    
    return hash_calculado == hash_esperado
