import sqlite3
from sqlite3 import Error

sql_crear_plan_cuentas = """
        CREATE TABLE IF NOT EXISTS plan_cuentas (
            id_plan_cuenta INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plan_cuentas TEXT NOT NULL UNIQUE
            );
        """ 

sql_crear_productos_cuenta_contable = """
        CREATE TABLE IF NOT EXISTS cuenta_contable (
            id_cuenta_contable INTEGER PRIMARY KEY AUTOINCREMENT,
            id_generico INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            nombre_cuenta TEXT NOT NULL,
            codigo_cuenta TEXT NOT NULL,
            foreign key (id_generico) references generico(id_generico)
        );
        """

# CORREGIDO: Agregar coma después de total_haber
sql_crear_productos_libro_diario = """
        CREATE TABLE IF NOT EXISTS libro_diario (
            id_libro_diario INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            contador TEXT NOT NULL,
            nombre_empresa TEXT NOT NULL,
            total_debe REAL NOT NULL,
            total_haber REAL NOT NULL,  -- CORREGIDO: coma agregada
            id_plan_cuenta INTEGER,
            origen TEXT NOT NULL DEFAULT 'creado',
            fecha_importacion TEXT,
            foreign key (id_mes) references mes(id_mes)
        );
        """

sql_crear_productos_mes = """
        CREATE TABLE IF NOT EXISTS mes (
            id_mes INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_mes TEXT NOT NULL
        );
        """

sql_crear_productos_tipo_cuenta = """
        CREATE TABLE IF NOT EXISTS tipo_cuenta (
            id_tipo_cuenta INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tipo_cuenta TEXT NOT NULL,
            numero_cuenta TEXT NOT NULL,
            id_plan_cuenta INTEGER DEFAULT 0,
            foreign key (id_plan_cuenta) references plan_cuentas(id_plan_cuenta)
        );
        """

sql_crear_productos_rubro = """
        CREATE TABLE IF NOT EXISTS rubro (
            id_rubro INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tipo_cuenta INTEGER NOT NULL,
            numero_cuenta TEXT NOT NULL,
            nombre_rubro TEXT NOT NULL,  -- CORREGIDO: coma agregada
            foreign key (id_tipo_cuenta) references tipo_cuenta(id_tipo_cuenta)
        );
        """

# CORREGIDO: Agregar coma después de nombre_generico
sql_crear_productos_generico = """
        CREATE TABLE IF NOT EXISTS generico (
            id_generico INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rubro INTEGER NOT NULL,
            numero_cuenta TEXT NOT NULL,
            nombre_generico TEXT NOT NULL,  -- CORREGIDO: coma agregada
            foreign key (id_rubro) references rubro(id_rubro)
        );
        """

# CORREGIDO: Agregar coma después de descripcion
sql_crear_productos_asiento = """
        CREATE TABLE IF NOT EXISTS asiento (
            id_asiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_libro_diario INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            numero_asiento INTEGER NOT NULL,
            descripcion TEXT NOT NULL,  -- CORREGIDO: coma agregada
            foreign key (id_libro_diario) references libro_diario(id_libro_diario)
        );
        """

# CORREGIDO: Agregar coma después de id_cuenta_contable
sql_crear_productos_linea_asiento = """
        CREATE TABLE IF NOT EXISTS linea_asiento (
            id_linea_asiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_asiento INTEGER NOT NULL,
            debe REAL NOT NULL,
            haber REAL NOT NULL,
            id_cuenta_contable INTEGER NOT NULL,  -- CORREGIDO: coma agregada
            foreign key (id_asiento) references asiento(id_asiento),
            foreign key (id_cuenta_contable) references cuenta_contable(id_cuenta_contable)
        );
        """

# el nombre de la base de datos
nombre_db = "libro_facil.db"
# el path de la base de datos
ruta_db = "./Base de datos/"
# el path completo de la base de datos
path_db = ruta_db + nombre_db   

def crear_estructura_db(nombre_db):
    """Crea la conexión a la base de datos y las tablas necesarias."""
    conn = None
    try:
        # 1. Conexión a la base de datos
        conn = sqlite3.connect(nombre_db)
        print(f"✅ Conexión a SQLite establecida: {nombre_db}")

        # 2. Creación de las tablas
        cursor = conn.cursor()

        # Ejecutar las sentencias CORREGIDAS
        cursor.execute(sql_crear_plan_cuentas)
        cursor.execute(sql_crear_productos_mes)  # Primero crear mes (por las FK)
        cursor.execute(sql_crear_productos_tipo_cuenta)
        cursor.execute(sql_crear_productos_rubro)
        cursor.execute(sql_crear_productos_generico)
        cursor.execute(sql_crear_productos_cuenta_contable)
        cursor.execute(sql_crear_productos_libro_diario)
        cursor.execute(sql_crear_productos_asiento)
        cursor.execute(sql_crear_productos_linea_asiento)

        # Migraciones ligeras: agregar columnas si faltan
        def ensure_column(table: str, column: str, ddl: str):
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
            if column not in cols:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")
                    print(f"✅ Columna agregada: {table}.{column}")
                except Error as e:
                    print(f"❌ No se pudo agregar columna {table}.{column}: {e}")

        ensure_column("libro_diario", "origen", "TEXT NOT NULL DEFAULT 'creado'")
        ensure_column("libro_diario", "fecha_importacion", "TEXT")
        ensure_column("tipo_cuenta", "numero_cuenta", "TEXT DEFAULT ''")
        ensure_column("tipo_cuenta", "id_plan_cuenta", "INTEGER DEFAULT 0")
        ensure_column("rubro", "numero_cuenta", "TEXT DEFAULT ''")
        ensure_column("generico", "numero_cuenta", "TEXT DEFAULT ''")

        # Confirmar los cambios
        conn.commit()
        print("🛠 Estructura de todas las tablas creada exitosamente.")

    except Error as e:
        print(f"❌ Ocurrió un error: {e}")

    finally:
        # 3. Cerrar la conexión
        if conn:
            conn.close()
            print("➡ Conexión a SQLite cerrada.")

def poblar_tablas_catalogo(nombre_db):
    """Poblar las tablas catálogo (tipo_cuenta, rubro, generico)"""
    conn = None
    try:
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        
        cursor.execute("INSERT OR IGNORE INTO plan_cuentas (id_plan_cuenta, nombre_plan_cuentas) VALUES (0, 'General')")
        print("✅ Tabla PLAN_CUENTAS poblada")
        
        # 1. Poblar tabla MES
        meses = [
            ('Enero',), ('Febrero',), ('Marzo',), ('Abril',), ('Mayo',), ('Junio',),
            ('Julio',), ('Agosto',), ('Septiembre',), ('Octubre',), ('Noviembre',), ('Diciembre',)
        ]
        cursor.executemany("INSERT OR IGNORE INTO mes (nombre_mes) VALUES (?)", meses)
        print("✅ Tabla MES poblada")
        
        # 2. Poblar tabla TIPO_CUENTA
        tipos_cuenta = [
            ('Activo', '1.0.0.000', 0),
            ('Pasivo', '2.0.0.000', 0),
            ('Patrimonio', '3.0.0.000', 0),
            ('Ingresos', '4.0.0.000', 0),
            ('Costos y Gastos', '5.0.0.000', 0),
            ('Cuentas de Orden', '6.0.0.000', 0)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO tipo_cuenta (nombre_tipo_cuenta, numero_cuenta, id_plan_cuenta) VALUES (?, ?, ?)",
            tipos_cuenta,
        )
        print("✅ Tabla TIPO_CUENTA poblada")
        
        # 3. Poblar tabla RUBRO
        rubros = [
            # Activo (id_tipo_cuenta = 1)
            (1, '1.1.0.000', 'Activo Corriente'),
            (1, '1.2.0.000', 'Activo No Corriente'),
            # Pasivo (id_tipo_cuenta = 2)
            (2, '2.1.0.000', 'Pasivo Corriente'),
            (2, '2.2.0.000', 'Pasivo No Corriente'),
            # Patrimonio (id_tipo_cuenta = 3)
            (3, '3.1.0.000', 'Capital Social'),
            (3, '3.2.0.000', 'Reservas'),
            (3, '3.3.0.000', 'Resultados del Ejercicio'),
            (3, '3.4.0.000', 'Otros Resultados Integrales'),
            # Ingresos (id_tipo_cuenta = 4)
            (4, '4.1.0.000', 'Ingresos por Ventas'),
            (4, '4.2.0.000', 'Otros Ingresos Operacionales'),
            (4, '4.3.0.000', 'Ingresos No Operacionales'),
            # Costos y Gastos (id_tipo_cuenta = 5)
            (5, '5.1.0.000', 'Costo de Ventas'),
            (5, '5.2.0.000', 'Gastos de Operación'),
            (5, '5.3.0.000', 'Otros Gastos y Pérdidas'),
            # Cuentas de Orden (id_tipo_cuenta = 6)
            (6, '6.1.0.000', 'Cuentas de Orden Deudoras'),
            (6, '6.2.0.000', 'Cuentas de Orden Acreedoras')
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO rubro (id_tipo_cuenta, numero_cuenta, nombre_rubro) VALUES (?, ?, ?)",
            rubros,
        )
        print("✅ Tabla RUBRO poblada")
        
        # 4. Poblar tabla GENERICO
        genericos = [
            # ACTIVO CORRIENTE (id_rubro = 1)
            (1, '1.1.1.000', 'Efectivo y Equivalentes de Efectivo'),
            (1, '1.1.2.000', 'Inversiones a Corto Plazo'),
            (1, '1.1.3.000', 'Cuentas por Cobrar Comerciales'),
            (1, '1.1.4.000', 'Otras Cuentas por Cobrar'),
            (1, '1.1.5.000', 'Inventarios'),
            (1, '1.1.6.000', 'Gastos Pagados por Anticipado'),
            
            # ACTIVO NO CORRIENTE (id_rubro = 2)
            (2, '1.2.1.000', 'Propiedades, Planta y Equipo'),
            (2, '1.2.2.000', 'Activos Intangibles'),
            (2, '1.2.3.000', 'Inversiones a Largo Plazo'),
            (2, '1.2.4.000', 'Otros Activos No Corrientes'),
            
            # PASIVO CORRIENTE (id_rubro = 3)
            (3, '2.1.1.000', 'Obligaciones Financieras a Corto Plazo'),
            (3, '2.1.2.000', 'Cuentas por Pagar Comerciales'),
            (3, '2.1.3.000', 'Otras Cuentas por Pagar'),
            (3, '2.1.4.000', 'Impuestos por Pagar'),
            (3, '2.1.5.000', 'Provisiones a Corto Plazo'),
            (3, '2.1.6.000', 'Ingresos Diferidos'),
            
            # PASIVO NO CORRIENTE (id_rubro = 4)
            (4, '2.2.1.000', 'Obligaciones Financieras a Largo Plazo'),
            (4, '2.2.2.000', 'Otros Pasivos a Largo Plazo'),
            
            # CAPITAL SOCIAL (id_rubro = 5)
            (5, '3.1.1.000', 'Capital Social'),
            
            # RESERVAS (id_rubro = 6)
            (6, '3.2.1.000', 'Reservas'),
            
            # RESULTADOS DEL EJERCICIO (id_rubro = 7)
            (7, '3.3.1.000', 'Resultados del Ejercicio'),
            
            # OTROS RESULTADOS INTEGRALES (id_rubro = 8)
            (8, '3.4.1.000', 'Otros Resultados Integrales'),
            
            # INGRESOS POR VENTAS (id_rubro = 9)
            (9, '4.1.1.000', 'Ingresos por Ventas'),
            
            # OTROS INGRESOS OPERACIONALES (id_rubro = 10)
            (10, '4.2.1.000', 'Otros Ingresos Operacionales'),
            
            # INGRESOS NO OPERACIONALES (id_rubro = 11)
            (11, '4.3.1.000', 'Ingresos No Operacionales'),
            
            # COSTO DE VENTAS (id_rubro = 12)
            (12, '5.1.1.000', 'Costo de Ventas'),
            
            # GASTOS DE OPERACIÓN (id_rubro = 13)
            (13, '5.2.1.000', 'Gastos de Ventas'),
            (13, '5.2.2.000', 'Gastos de Administración'),
            
            # OTROS GASTOS Y PÉRDIDAS (id_rubro = 14)
            (14, '5.3.1.000', 'Otros Gastos y Pérdidas'),
            
            # CUENTAS DE ORDEN DEUDORAS (id_rubro = 15)
            (15, '6.1.1.000', 'Cuentas de Orden Deudoras'),
            
            # CUENTAS DE ORDEN ACREEDORAS (id_rubro = 16)
            (16, '6.2.1.000', 'Cuentas de Orden Acreedoras')
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO generico (id_rubro, numero_cuenta, nombre_generico) VALUES (?, ?, ?)",
            genericos,
        )
        print("✅ Tabla GENERICO poblada")
        
        conn.commit()
        print("🎉 Tablas catálogo pobladas exitosamente")
        
    except Error as e:
        print(f"❌ Error al poblar tablas catálogo: {e}")
    finally:
        if conn:
            conn.close()

def poblar_cuentas_contables(nombre_db):
    """Poblar la tabla cuenta_contable con el plan de cuentas venezolano"""
    conn = None
    try:
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        
        # Obtener IDs de los genéricos para referencia
        cursor.execute("SELECT id_generico, nombre_generico FROM generico")
        genericos = {row[1]: row[0] for row in cursor.fetchall()}
        
        # CUENTAS CONTABLES - Plan Venezolano
        cuentas = [
            # ACTIVO CORRIENTE
            # Efectivo y Equivalentes de Efectivo (id_generico = 1)
            (genericos['Efectivo y Equivalentes de Efectivo'], 'Caja General', 'Caja General', '1.1.1.001'),
            (genericos['Efectivo y Equivalentes de Efectivo'], 'Caja Chica', 'Caja Chica', '1.1.1.002'),
            (genericos['Efectivo y Equivalentes de Efectivo'], 'Fondos Fijos', 'Fondos Fijos', '1.1.1.003'),
            (genericos['Efectivo y Equivalentes de Efectivo'], 'Bancos (Cuenta Corriente Bolívares)', 'Bancos Bolívares', '1.1.1.004'),
            (genericos['Efectivo y Equivalentes de Efectivo'], 'Bancos (Cuenta Moneda Extranjera $)', 'Bancos Dólares', '1.1.1.005'),
            (genericos['Efectivo y Equivalentes de Efectivo'], 'Equivalentes de Efectivo', 'Equivalentes de Efectivo', '1.1.1.006'),
            
            # Inversiones a Corto Plazo (id_generico = 2)
            (genericos['Inversiones a Corto Plazo'], 'Instrumentos Financieros Corto Plazo', 'Inversiones Corto Plazo', '1.1.2.001'),
            (genericos['Inversiones a Corto Plazo'], 'Depósitos a Plazo Fijo Corto Plazo', 'Depósitos Corto Plazo', '1.1.2.002'),
            
            # Cuentas por Cobrar Comerciales (id_generico = 3)
            (genericos['Cuentas por Cobrar Comerciales'], 'Clientes (Cuentas por Cobrar)', 'Clientes', '1.1.3.001'),
            (genericos['Cuentas por Cobrar Comerciales'], 'Documentos por Cobrar', 'Documentos por Cobrar', '1.1.3.002'),
            (genericos['Cuentas por Cobrar Comerciales'], '(-) Provisión para Cuentas de Cobranza Dudosa', 'Provisión Cobranza Dudosa', '1.1.3.003'),
            
            # Otras Cuentas por Cobrar (id_generico = 4)
            (genericos['Otras Cuentas por Cobrar'], 'Funcionarios y Empleados', 'Cuentas por Cobrar Empleados', '1.1.4.001'),
            (genericos['Otras Cuentas por Cobrar'], 'Anticipos a Proveedores', 'Anticipos a Proveedores', '1.1.4.002'),
            (genericos['Otras Cuentas por Cobrar'], 'IVA Crédito Fiscal', 'IVA Crédito Fiscal', '1.1.4.003'),
            
            # Inventarios (id_generico = 5)
            (genericos['Inventarios'], 'Mercancías Disponibles para la Venta', 'Inventario Mercancías', '1.1.5.001'),
            (genericos['Inventarios'], 'Materias Primas', 'Inventario Materias Primas', '1.1.5.002'),
            (genericos['Inventarios'], 'Productos en Proceso', 'Inventario Productos en Proceso', '1.1.5.003'),
            (genericos['Inventarios'], 'Productos Terminados', 'Inventario Productos Terminados', '1.1.5.004'),
            (genericos['Inventarios'], 'Materiales y Suministros', 'Inventario Materiales', '1.1.5.005'),
            (genericos['Inventarios'], '(-) Provisión para Inventarios Obsoletos', 'Provisión Inventarios Obsoletos', '1.1.5.006'),
            
            # Gastos Pagados por Anticipado (id_generico = 6)
            (genericos['Gastos Pagados por Anticipado'], 'Seguros Pagados por Anticipado', 'Seguros Pagados', '1.1.6.001'),
            (genericos['Gastos Pagados por Anticipado'], 'Intereses Pagados por Anticipado', 'Intereses Pagados', '1.1.6.002'),
            (genericos['Gastos Pagados por Anticipado'], 'Arrendamientos Pagados por Anticipado', 'Arrendamientos Pagados', '1.1.6.003'),
            
            # ACTIVO NO CORRIENTE
            # Propiedades, Planta y Equipo (id_generico = 7)
            (genericos['Propiedades, Planta y Equipo'], 'Terrenos', 'Terrenos', '1.2.1.001'),
            (genericos['Propiedades, Planta y Equipo'], 'Edificaciones', 'Edificaciones', '1.2.1.002'),
            (genericos['Propiedades, Planta y Equipo'], 'Maquinaria y Equipo', 'Maquinaria y Equipo', '1.2.1.003'),
            (genericos['Propiedades, Planta y Equipo'], 'Mobiliario y Enseres', 'Mobiliario y Enseres', '1.2.1.004'),
            (genericos['Propiedades, Planta y Equipo'], 'Equipos de Computación', 'Equipos de Computación', '1.2.1.005'),
            (genericos['Propiedades, Planta y Equipo'], 'Vehiculos', 'Vehículos', '1.2.1.006'),
            (genericos['Propiedades, Planta y Equipo'], '(-) Depreciación Acumulada', 'Depreciación Acumulada', '1.2.1.007'),
            
            # Activos Intangibles (id_generico = 8)
            (genericos['Activos Intangibles'], 'Marcas y Patentes', 'Marcas y Patentes', '1.2.2.001'),
            (genericos['Activos Intangibles'], 'Licencias de Software', 'Licencias Software', '1.2.2.002'),
            (genericos['Activos Intangibles'], 'Goodwill (Fondo de Comercio)', 'Goodwill', '1.2.2.003'),
            (genericos['Activos Intangibles'], '(-) Amortización Acumulada', 'Amortización Acumulada', '1.2.2.004'),
            
            # Inversiones a Largo Plazo (id_generico = 9)
            (genericos['Inversiones a Largo Plazo'], 'Inversiones en Subsidiarias', 'Inversiones Subsidiarias', '1.2.3.001'),
            (genericos['Inversiones a Largo Plazo'], 'Bonos a Largo Plazo', 'Bonos Largo Plazo', '1.2.3.002'),
            
            # Otros Activos No Corrientes (id_generico = 10)
            (genericos['Otros Activos No Corrientes'], 'Depósitos en Garantía a Largo Plazo', 'Depósitos Garantía L/P', '1.2.4.001'),
            
            # PASIVO CORRIENTE
            # Obligaciones Financieras a Corto Plazo (id_generico = 11)
            (genericos['Obligaciones Financieras a Corto Plazo'], 'Sobregiros Bancarios', 'Sobregiros Bancarios', '2.1.1.001'),
            (genericos['Obligaciones Financieras a Corto Plazo'], 'Préstamos Bancarios a Corto Plazo', 'Préstamos Corto Plazo', '2.1.1.002'),
            (genericos['Obligaciones Financieras a Corto Plazo'], 'Parte Corriente de Préstamos a Largo Plazo', 'Parte Corriente Préstamos L/P', '2.1.1.003'),
            
            # Cuentas por Pagar Comerciales (id_generico = 12)
            (genericos['Cuentas por Pagar Comerciales'], 'Proveedores Nacionales', 'Proveedores Nacionales', '2.1.2.001'),
            (genericos['Cuentas por Pagar Comerciales'], 'Proveedores del Exterior', 'Proveedores Exterior', '2.1.2.002'),
            (genericos['Cuentas por Pagar Comerciales'], 'Documentos por Pagar', 'Documentos por Pagar', '2.1.2.003'),
            
            # Otras Cuentas por Pagar (id_generico = 13)
            (genericos['Otras Cuentas por Pagar'], 'Cuentas por Pagar a Accionistas', 'Cuentas por Pagar Accionistas', '2.1.3.001'),
            (genericos['Otras Cuentas por Pagar'], 'Acreedores Varios', 'Acreedores Varios', '2.1.3.002'),
            (genericos['Otras Cuentas por Pagar'], 'Retenciones por Pagar (ISLR, IVA, etc.)', 'Retenciones por Pagar', '2.1.3.003'),
            (genericos['Otras Cuentas por Pagar'], 'IVA Débito Fiscal', 'IVA Débito Fiscal', '2.1.3.004'),
            
            # Impuestos por Pagar (id_generico = 14)
            (genericos['Impuestos por Pagar'], 'Impuesto sobre la Renta por Pagar', 'ISLR por Pagar', '2.1.4.001'),
            (genericos['Impuestos por Pagar'], 'Impuesto Municipal a la Actividad Económica por Pagar', 'IMAE por Pagar', '2.1.4.002'),
            
            # Provisiones a Corto Plazo (id_generico = 15)
            (genericos['Provisiones a Corto Plazo'], 'Provisión para Gastos Legales', 'Provisión Gastos Legales', '2.1.5.001'),
            (genericos['Provisiones a Corto Plazo'], 'Provisión para Indemnizaciones', 'Provisión Indemnizaciones', '2.1.5.002'),
            
            # Ingresos Diferidos (id_generico = 16)
            (genericos['Ingresos Diferidos'], 'Ingresos por Servicios No Prestados', 'Ingresos Diferidos', '2.1.6.001'),
            
            # PASIVO NO CORRIENTE
            # Obligaciones Financieras a Largo Plazo (id_generico = 17)
            (genericos['Obligaciones Financieras a Largo Plazo'], 'Préstamos Bancarios a Largo Plazo', 'Préstamos Largo Plazo', '2.2.1.001'),
            (genericos['Obligaciones Financieras a Largo Plazo'], 'Hipotecas por Pagar', 'Hipotecas por Pagar', '2.2.1.002'),
            
            # Otros Pasivos a Largo Plazo (id_generico = 18)
            (genericos['Otros Pasivos a Largo Plazo'], 'Provisiones para Jubilaciones', 'Provisiones Jubilaciones', '2.2.2.001'),
            
            # PATRIMONIO
            # Capital Social (id_generico = 19)
            (genericos['Capital Social'], 'Capital Social Suscrito y Pagado', 'Capital Social', '3.1.1.001'),
            (genericos['Capital Social'], '(-) Capital Social Suscrito por Cobrar', 'Capital por Cobrar', '3.1.1.002'),
            
            # Reservas (id_generico = 20)
            (genericos['Reservas'], 'Reserva Legal', 'Reserva Legal', '3.1.2.001'),
            (genericos['Reservas'], 'Reservas Voluntarias', 'Reservas Voluntarias', '3.1.2.002'),
            (genericos['Reservas'], 'Ajuste por Inflación y Dévaluación', 'Ajuste por Inflación', '3.1.2.003'),
            
            # Resultados del Ejercicio (id_generico = 21)
            (genericos['Resultados del Ejercicio'], 'Resultados del Ejercicio (Utilidad o Pérdida Neta)', 'Resultado Ejercicio', '3.1.3.001'),
            (genericos['Resultados del Ejercicio'], 'Resultados Acumulados de Ejercicios Anteriores', 'Resultados Acumulados', '3.1.3.002'),
            (genericos['Resultados del Ejercicio'], 'Resultados de Ejercicios Anteriores', 'Resultados Ejercicios Anteriores', '3.1.3.003'),
            
            # Otros Resultados Integrales (id_generico = 22)
            (genericos['Otros Resultados Integrales'], 'Ajustes por Conversión Monetaria', 'Ajuste Conversión Monetaria', '3.1.4.001'),
            
            # INGRESOS
            # Ingresos por Ventas (id_generico = 23)
            (genericos['Ingresos por Ventas'], 'Ventas de Productos / Servicios', 'Ventas', '4.1.1.001'),
            (genericos['Ingresos por Ventas'], '(-) Devoluciones en Ventas', 'Devoluciones en Ventas', '4.1.1.002'),
            (genericos['Ingresos por Ventas'], '(-) Descuentos Comerciales', 'Descuentos Comerciales', '4.1.1.003'),
            
            # Otros Ingresos Operacionales (id_generico = 24)
            (genericos['Otros Ingresos Operacionales'], 'Ingresos por Servicios Técnicos', 'Ingresos Servicios Técnicos', '4.1.2.001'),
            (genericos['Otros Ingresos Operacionales'], 'Ingresos por Alquileres', 'Ingresos por Alquileres', '4.1.2.002'),
            
            # Ingresos No Operacionales (id_generico = 25)
            (genericos['Ingresos No Operacionales'], 'Ganancias por Diferencia Cambiaria', 'Ganancias Diferencia Cambiaria', '4.1.3.001'),
            (genericos['Ingresos No Operacionales'], 'Ingresos por Intereses', 'Ingresos por Intereses', '4.1.3.002'),
            
            # COSTOS Y GASTOS
            # Costo de Ventas (id_generico = 26)
            (genericos['Costo de Ventas'], 'Costo de Mercancías Vendidas', 'Costo de Ventas', '5.1.1.001'),
            (genericos['Costo de Ventas'], 'Costo de Servicios Prestados', 'Costo Servicios', '5.1.1.002'),
            (genericos['Costo de Ventas'], '(-) Devoluciones en Compras', 'Devoluciones en Compras', '5.1.1.003'),
            
            # Gastos de Operación - Gastos de Ventas (id_generico = 27)
            (genericos['Gastos de Ventas'], 'Sueldos y Salarios (Ventas)', 'Sueldos Ventas', '5.1.2.001'),
            (genericos['Gastos de Ventas'], 'Comisiones sobre Ventas', 'Comisiones Ventas', '5.1.2.002'),
            (genericos['Gastos de Ventas'], 'Publicidad y Propaganda', 'Publicidad', '5.1.2.003'),
            (genericos['Gastos de Ventas'], 'Gastos de Transporte y Fletes', 'Gastos Transporte', '5.1.2.004'),
            
            # Gastos de Operación - Gastos de Administración (id_generico = 28)
            (genericos['Gastos de Administración'], 'Sueldos y Salarios (Administración)', 'Sueldos Administración', '5.1.2.005'),
            (genericos['Gastos de Administración'], 'Servicios Públicos (Agua, Luz, Teléfono)', 'Servicios Públicos', '5.1.2.006'),
            (genericos['Gastos de Administración'], 'Gastos de Arrendamiento', 'Arrendamientos', '5.1.2.007'),
            (genericos['Gastos de Administración'], 'Gastos de Seguros', 'Seguros', '5.1.2.008'),
            (genericos['Gastos de Administración'], 'Depreciación - Gastos de Administración', 'Depreciación Administración', '5.1.2.009'),
            (genericos['Gastos de Administración'], 'Amortización - Gastos de Administración', 'Amortización Administración', '5.1.2.010'),
            
            # Otros Gastos y Pérdidas (id_generico = 29)
            (genericos['Otros Gastos y Pérdidas'], 'Gastos por Intereses', 'Gastos por Intereses', '5.1.3.001'),
            (genericos['Otros Gastos y Pérdidas'], 'Pérdida por Diferencia Cambiaria', 'Pérdidas Diferencia Cambiaria', '5.1.3.002'),
            (genericos['Otros Gastos y Pérdidas'], 'Gastos No Operacionales Varios', 'Gastos No Operacionales', '5.1.3.003'),
            
            # CUENTAS DE ORDEN
            # Cuentas de Orden Deudoras (id_generico = 30)
            (genericos['Cuentas de Orden Deudoras'], 'Mercancías en Consignación', 'Mercancías Consignación', '6.1.1.001'),
            (genericos['Cuentas de Orden Deudoras'], 'Bienes Recibidos en Arrendamiento', 'Bienes Arrendamiento', '6.1.1.002'),
            
            # Cuentas de Orden Acreedoras (id_generico = 31)
            (genericos['Cuentas de Orden Acreedoras'], 'Obligaciones por Garantías Otorgadas', 'Garantías Otorgadas', '6.1.2.001')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO cuenta_contable 
            (id_generico, descripcion, nombre_cuenta, codigo_cuenta) 
            VALUES (?, ?, ?, ?)
        """, cuentas)
        
        conn.commit()
        print(f"✅ Tabla CUENTA_CONTABLE poblada con {len(cuentas)} cuentas")
        
    except Error as e:
        print(f"❌ Error al poblar cuentas contables: {e}")
    finally:
        if conn:
            conn.close()

def inicializar_base_datos():
    """Función principal para crear y poblar la base de datos."""
    crear_estructura_db(nombre_db)
    poblar_tablas_catalogo(nombre_db)
    poblar_cuentas_contables(nombre_db)
    print("🎉 Base de datos completamente poblada y lista para usar!")
    
if __name__ == "__main__":
    inicializar_base_datos()