from __future__ import annotations

from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt


OUTPUT_PATH = Path(__file__).resolve().parent / "Informe_Tercer_Corte_MES_Software.docx"


def configure_document(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)

    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    for style_name, size in (("Heading 1", 14), ("Heading 2", 12)):
        style = document.styles[style_name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True


def add_paragraph(document: Document, text: str, *, bold: bool = False, center: bool = False) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.space_after = Pt(6)
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)


def add_bullet(document: Document, text: str) -> None:
    paragraph = document.add_paragraph(style="List Bullet")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.line_spacing = 1.5
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)


def add_heading(document: Document, text: str, level: int = 1) -> None:
    heading = document.add_heading(text, level=level)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT


def add_table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for idx, header in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = header
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)

    for row_values in rows:
        cells = table.add_row().cells
        for idx, value in enumerate(row_values):
            cells[idx].text = value
            for run in cells[idx].paragraphs[0].runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(10)


def build_document() -> None:
    document = Document()
    configure_document(document)

    for _ in range(4):
        add_paragraph(document, "", center=True)
    add_paragraph(document, "DOCUMENTO TÉCNICO DEL TERCER CORTE", bold=True, center=True)
    add_paragraph(
        document,
        "Escalamiento del Sistema MES de Control de Producción hacia una solución de software",
        bold=True,
        center=True,
    )
    for _ in range(3):
        add_paragraph(document, "", center=True)
    add_paragraph(document, "Asignatura: Patrones de Software", center=True)
    add_paragraph(document, "Programa: Ingeniería de Sistemas", center=True)
    add_paragraph(
        document,
        "Integrantes: Juan Sebastian Rubiano Romero - Angie Lucero Vargas Amado",
        center=True,
    )
    add_paragraph(document, "Proyecto: Sistema de Control de Producción (MES)", center=True)
    add_paragraph(document, f"Fecha de elaboración: {datetime.now().strftime('%Y-%m-%d')}", center=True)
    document.add_page_break()

    add_heading(document, "1. Introducción")
    add_paragraph(
        document,
        "El presente documento expone la evolución del proyecto académico Sistema de Control de Producción "
        "(MES) hacia una propuesta más cercana a software real. Durante los cortes anteriores el trabajo se "
        "centró en comprender y demostrar patrones de software desde una perspectiva conceptual y funcional. "
        "En este último corte se incorporan elementos propios de una solución escalable, tales como base de "
        "datos, usuarios, seguridad mínima, persistencia de resultados, trazabilidad operativa y consultas con "
        "filtros por fecha, hora, turno, línea y estado.",
    )
    add_paragraph(
        document,
        "El valor del proyecto ya no radica únicamente en mostrar clases que cumplen con un patrón de diseño, "
        "sino en evidenciar cómo dichas decisiones arquitectónicas resuelven problemas concretos dentro del "
        "dominio MES: planificación de órdenes, ejecución de producción, integración con sistemas legacy, "
        "auditoría, telemetría, control de acceso, transición de estados y análisis de consultas.",
    )

    add_heading(document, "2. Justificación del escalamiento")
    add_paragraph(
        document,
        "Aunque la versión funcional previa del proyecto ya permitía demostrar el flujo end-to-end de una orden "
        "de producción, la evaluación del tercer corte exige acercar la solución a un escenario de software "
        "utilizable y defendible. En ese contexto, surgió la necesidad de incorporar persistencia, control de "
        "usuarios, seguridad básica y consultas de negocio mejor definidas. Adicionalmente, se atendió la "
        "recomendación docente de enriquecer las consultas con filtros temporales y operativos, de modo que el "
        "sistema no solo simule resultados, sino que almacene y recupere información con mayor utilidad.",
    )

    add_heading(document, "3. Alcance del proyecto")
    add_paragraph(
        document,
        "El alcance de esta fase comprende la transformación del proyecto en una base de software funcional "
        "orientada a la gestión de órdenes MES, manteniendo la coherencia con los patrones de software "
        "trabajados en la asignatura.",
    )
    for item in [
        "Registrar, cargar y reutilizar plantillas de producción para distintas líneas y tipos de máquina.",
        "Ejecutar órdenes de producción con trazabilidad desde la planificación hasta el cierre.",
        "Persistir usuarios, órdenes, historial de estados, telemetría, auditoría y lotes de consultas en SQLite.",
        "Aplicar autenticación mínima con protección de contraseñas mediante hash y salt.",
        "Restringir acceso a reportes y consultas según rol y línea autorizada.",
        "Generar y almacenar consultas filtrables por fecha, hora, turno, línea, producto, protocolo y estado.",
        "Integrar patrones creacionales, estructurales y de comportamiento en un mismo flujo de negocio.",
    ]:
        add_bullet(document, item)

    add_heading(document, "4. Fuera de alcance")
    for item in [
        "Despliegue del sistema en ambiente productivo web o móvil.",
        "Integración con PLC físicos, sensores reales o infraestructura industrial de planta.",
        "Implementación de mecanismos de seguridad avanzados como OAuth, JWT, MFA o cifrado empresarial.",
        "Arquitectura distribuida basada en microservicios o balanceo de carga real.",
        "Analítica predictiva, reportería BI o dashboards en tiempo real con herramientas externas.",
    ]:
        add_bullet(document, item)

    add_heading(document, "5. Objetivos")
    add_heading(document, "5.1 Objetivo general", level=2)
    add_paragraph(
        document,
        "Desarrollar la evolución del Sistema de Control de Producción MES hacia una solución de software más "
        "escalable, segura y trazable, mediante la integración de persistencia, usuarios, consultas filtradas y "
        "patrones de software alineados con el flujo operativo del proceso productivo.",
    )
    add_heading(document, "5.2 Objetivos específicos", level=2)
    for item in [
        "Implementar una base de datos ligera para persistir la información operativa y analítica del sistema.",
        "Gestionar usuarios y permisos mínimos para controlar el acceso a órdenes, líneas y reportes.",
        "Aplicar el patrón State para modelar el ciclo de vida de la orden de producción.",
        "Aplicar el patrón Observer para notificar y auditar cambios de estado sin acoplar la lógica principal.",
        "Integrar una interfaz gráfica profesional que unifique autenticación, operación, consultas y evidencias.",
        "Optimizar las consultas del proyecto mediante filtros por fecha, hora, turno, línea, protocolo y estado.",
        "Persistir lotes de consultas para fortalecer la trazabilidad y la defensa del sistema como software.",
        "Documentar el alcance, los resultados y el papel de cada patrón dentro del proyecto.",
    ]:
        add_bullet(document, item)

    add_heading(document, "6. Descripción general de la solución")
    add_paragraph(
        document,
        "La solución construida se organiza en una capa de interfaz, una capa de aplicación, una capa de "
        "persistencia y un conjunto de módulos de patrones funcionales. La interfaz principal permite iniciar "
        "sesión, ejecutar órdenes, consultar resultados, visualizar patrones y exportar evidencia. La capa de "
        "servicio orquesta la ejecución del flujo MES, gestiona el acceso del usuario autenticado y coordina la "
        "persistencia. La base de datos SQLite almacena la información estructural y operativa del sistema. "
        "Finalmente, los módulos de patrones conservan la demostración arquitectónica del proyecto y la conectan "
        "con los requerimientos reales de la aplicación.",
    )

    add_heading(document, "7. Componentes principales del software")
    add_table(
        document,
        ["Componente", "Responsabilidad"],
        [
            ["UI_MES_Software_Pro.py", "Interfaz principal del sistema. Integra login, dashboard, operación, consultas y evidencias."],
            ["software_mes_service.py", "Orquestación de la capa software y coordinación del flujo MES con seguridad y persistencia."],
            ["software_mes_persistence.py", "Gestión de SQLite, creación de esquema y almacenamiento de entidades clave."],
            ["software_mes_security.py", "Autenticación, hash de contraseñas y control de acceso por rol y línea."],
            ["software_mes_queries.py", "Construcción de consultas filtrables por fecha, hora y contexto operativo."],
            ["software_mes_behavioral.py", "Implementación de patrones State y Observer para el tercer corte."],
            ["mes_functional_app.py", "Base funcional previa sobre la cual se mantiene el flujo de patrones del proyecto."],
        ],
    )

    add_heading(document, "8. Persistencia, base de datos y seguridad mínima")
    add_paragraph(
        document,
        "Con el fin de escalar el proyecto hacia una solución más defendible como software, se implementó una "
        "base de datos SQLite que centraliza la información del sistema. La persistencia ya no se limita a la "
        "ejecución en memoria, sino que registra órdenes, historial de estados, auditoría, telemetría y lotes "
        "de consultas.",
    )
    add_table(
        document,
        ["Tabla", "Propósito"],
        [
            ["users", "Almacenar credenciales, roles, líneas autorizadas y estado del usuario."],
            ["orders", "Persistir órdenes ejecutadas, producto, turno, protocolo, ventana horaria y estado final."],
            ["order_history", "Registrar las transiciones de estado de cada orden para mantener trazabilidad."],
            ["telemetry_events", "Guardar eventos asociados a telemetría y producción por orden."],
            ["audit_events", "Conservar evidencia de login, proxy, seguridad y cambios relevantes."],
            ["consultation_batches", "Registrar cada lote de consultas generado desde la interfaz."],
            ["consultation_results", "Persistir el detalle de cada consulta, su SQL, filtros y resultados."],
        ],
    )
    add_paragraph(
        document,
        "En materia de seguridad mínima, el sistema incorpora autenticación basada en usuario y contraseña, "
        "protección de contraseñas con hash y salt, roles diferenciados y restricción de acceso por línea de "
        "producción. Este nivel de seguridad no pretende cubrir un entorno empresarial completo, pero sí "
        "constituye un avance coherente respecto a una práctica puramente teórica.",
    )

    add_heading(document, "9. Consultas de negocio y mejora analítica")
    add_paragraph(
        document,
        "Una de las observaciones principales sobre la fase previa del proyecto fue la necesidad de mejorar las "
        "consultas para que su valor de negocio resultara más evidente. En respuesta a ello, la nueva versión "
        "del sistema soporta filtros por fecha, hora, turno, línea, protocolo, usuario, producto y estado. "
        "Adicionalmente, los lotes de consultas quedan almacenados en base de datos, lo que permite rastrear "
        "quién las generó, cuándo se ejecutaron, bajo qué condiciones y cuántos registros devolvieron.",
    )
    add_table(
        document,
        ["ID", "Consulta", "Utilidad"],
        [
            ["SQ1", "Planificación de órdenes", "Recuperar órdenes registradas por fecha, hora, turno, línea y producto."],
            ["SQ2", "Despacho técnico", "Verificar cómo se despacharon las órdenes y bajo qué protocolo industrial."],
            ["SQ3", "Capacidad vs carga", "Comparar unidades planificadas frente a la capacidad disponible de planta."],
            ["SQ4", "Ejecución y OEE", "Analizar producción real, paradas, eficiencia y estado de cierre."],
            ["SQ5", "Trazabilidad y telemetría", "Relacionar historial, auditoría, telemetría y evidencia de seguridad."],
        ],
    )

    add_heading(document, "10. Patrones aplicados dentro del proyecto")
    add_table(
        document,
        ["Patrón", "Categoría", "Aplicación en el proyecto", "Aporte principal"],
        [
            ["Singleton", "Creacional", "Centralizar el estado global del MES y la instancia de base de datos.", "Evitar duplicidad de control y mantener consistencia."],
            ["Factory Method", "Creacional", "Crear máquinas concretas según el tipo de orden.", "Reducir acoplamiento entre cliente y clases concretas."],
            ["Abstract Factory", "Creacional", "Construir familias compatibles de línea, máquina y asistente.", "Garantizar coherencia entre componentes relacionados."],
            ["Builder", "Creacional", "Construir reportes y estructuras de consulta paso a paso.", "Mejorar claridad en objetos complejos."],
            ["Prototype", "Creacional", "Clonar plantillas de producción reutilizables.", "Acelerar el registro y disminuir configuración repetitiva."],
            ["Adapter", "Estructural", "Integrar la capa MES con un gateway legacy.", "Permitir compatibilidad con sistemas heredados."],
            ["Bridge", "Estructural", "Separar el tipo de orden del protocolo industrial.", "Permitir variar protocolos y órdenes sin romper el cliente."],
            ["Composite", "Estructural", "Modelar planta, líneas y estaciones como jerarquía.", "Calcular capacidad total de forma uniforme."],
            ["Decorator", "Estructural", "Enriquecer reportes con calidad, trazabilidad y OEE.", "Agregar responsabilidades sin modificar el objeto base."],
            ["Facade", "Estructural", "Simplificar el punto de entrada del flujo operativo.", "Disminuir complejidad para el cliente de la aplicación."],
            ["Flyweight", "Estructural", "Compartir perfiles de máquina en telemetría repetitiva.", "Ahorrar memoria y mejorar escalabilidad en eventos."],
            ["Proxy", "Estructural", "Proteger reportes sensibles con autorización, caché y auditoría.", "Controlar acceso y reforzar la seguridad mínima."],
            ["State", "Comportamiento", "Modelar las transiciones CREATED, PLANNED, DISPATCHED, RUNNING y COMPLETED.", "Evitar condicionales frágiles y mejorar mantenibilidad."],
            ["Observer", "Comportamiento", "Notificar y auditar cambios de estado de la orden.", "Desacoplar reacciones del flujo principal."],
        ],
    )

    add_heading(document, "11. Resultados obtenidos")
    for item in [
        "Se consolidó una interfaz profesional para autenticación, dashboard, operación y consultas del sistema MES.",
        "Se implementó una base SQLite con persistencia de usuarios, órdenes, historial, telemetría, auditoría y lotes de consultas.",
        "Se incorporó seguridad mínima basada en hash, salt, roles y líneas autorizadas.",
        "Se mejoraron las consultas con filtros por fecha, hora, turno, línea, estado y protocolo.",
        "Se almacenaron los lotes de consultas para fortalecer la trazabilidad analítica del sistema.",
        "Se integraron State y Observer como patrones de comportamiento alineados con las orientaciones del tercer corte.",
        "Se mantuvo la demostración de los patrones previos sin perder la funcionalidad ya construida en cortes anteriores.",
        "Se verificó el flujo principal mediante pruebas end-to-end del escalamiento del sistema.",
    ]:
        add_bullet(document, item)

    add_heading(document, "12. Conclusiones")
    add_paragraph(
        document,
        "La evolución del proyecto evidencia que los patrones de software no deben entenderse como ejercicios "
        "aislados, sino como herramientas concretas para resolver problemas reales de diseño. En este caso, la "
        "aplicación de los patrones permitió transformar una demostración funcional en una base de software con "
        "persistencia, seguridad mínima, trazabilidad y consultas defendibles desde una perspectiva de negocio.",
    )
    add_paragraph(
        document,
        "El proyecto resultante conserva el valor académico de la asignatura, pero al mismo tiempo incorpora "
        "criterios propios de una solución informática: almacenamiento de información, gestión de usuarios, "
        "control de acceso, historial de cambios, visualización de resultados y soporte a consultas. Esto "
        "fortalece la sustentación técnica, ya que cada patrón puede explicarse tanto por su teoría como por su "
        "aporte verificable dentro del sistema MES.",
    )

    add_heading(document, "13. Recomendaciones y trabajo futuro")
    for item in [
        "Extender la gestión de turnos para permitir configuración paramétrica de horarios desde la interfaz.",
        "Agregar reportes históricos más avanzados y comparativos entre líneas, productos y períodos.",
        "Integrar exportaciones adicionales a PDF o reportes tabulares automatizados.",
        "Explorar autenticación reforzada y bitácoras más detalladas si el proyecto evoluciona a un escenario institucional.",
        "Conectar la persistencia actual con servicios externos o APIs industriales en una fase posterior.",
    ]:
        add_bullet(document, item)

    add_heading(document, "14. Cierre")
    add_paragraph(
        document,
        "En conclusión, el Sistema MES desarrollado en la asignatura demuestra una transición clara desde la "
        "comprensión conceptual de los patrones hasta su aplicación coordinada en una solución de software. El "
        "tercer corte consolida ese avance al incorporar persistencia, seguridad, consultas filtradas y patrones "
        "de comportamiento, logrando un proyecto más robusto, más argumentable y más cercano a un caso real de "
        "ingeniería de software.",
    )

    document.save(str(OUTPUT_PATH))
    print(f"Documento generado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_document()
