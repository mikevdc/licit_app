import json
import logging
import os
import sys
import threading

from app.core.config import settings
from contextvars import ContextVar
from datetime import datetime, timedelta
from loguru import logger
from pathlib import Path


# Variable de contexto segura para hilos y tareas asíncronas
request_id_var: ContextVar[str] = ContextVar("request_id", default = "N/A")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 1. Determinar a qué módulo de Loguru pertenece
        # Si el nombre del logger es 'uvicorn.access', lo marcamos como 'access'
        # Si es cualquier otro de uvicorn o fastapi, lo marcamos como 'system'
        module = "system"
        if record.name == "uvicorn.access":
            module = "access"
        
        # 2. Mapear niveles de logging estándar a Loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 3. Encontrar el origen del mensaje para el traceback
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        if not frame:
            depth = 2

        # 4. Enviar a Loguru con la etiqueta 'module' para que el sink lo capture
        logger.opt(depth = depth, exception = record.exc_info).bind(module = module).log(level, record.getMessage())


def setup_logging():

    current_dir = Path(__file__).resolve().parent
    env = settings.ENV_STATE

    # Cargar configuración
    json_file = "logging_config" if env == "prod" else "logging_config_dev"
    config_path = current_dir / f"{json_file}.json"
    with open(config_path) as f:
        conf = json.load(f)

    logger.remove() # Limpiar la configuración por defecto


    # ==========================================
    # MODO PRODUCCIÓN (Infraestructura / Docker)
    # ==========================================
    if env == "prod":
        # En Prod SOLO queremos JSON a la consola.
        # La infraestructura se encargará de guardar, rotar y buscar.
        logger.add(
            sys.stderr,
            level = "INFO",
            serialize = True, # Convierte todo a JSON estructurado
            enqueue = True,
            backtrace = True,
            diagnose = False
        )
        # Nota: Aquí no configuramos ficheros. Docker capturará el stderr
        print("🚀 Logging configurado en modo PRODUCCIÓN (JSON/Stdout)")


    # ==========================================
    # MODO DESARROLLO (Local / Archivos)
    # ==========================================
    else:

        base_dir = Path(conf["base_path"])
        base_dir.mkdir(exist_ok = True)

        # 1. Lógica de rotación híbrida (Tamaño o Tiempo)
        def hybrid_rotation_logic(message, file):
            # Tamaño
            file.seek(0, 2)
            if file.tell() >= conf["rotation"]["max_size_mb"] * 1024 * 1024:
                return True
            
            # Tiempo
            creation_time = datetime.fromtimestamp(os.path.getctime(file.name))
            if datetime.now() - creation_time >= timedelta(hours = conf["rotation"]["max_age_hours"]):
                return True
            
            return False
        
        # 2. Lógica para inyectar datos dinámicos en cada record
        def patcher(record):
            
            if "request_id" not in record["extra"] or record["extra"]["request_id"] == "N/A":
                record["extra"]["request_id"] = request_id_var.get() or "N/A"

            record["extra"]["thread_name"] = threading.current_thread().name

        logger.configure(patcher = patcher)

        # 3.1. Formatear los logs de Uvicorn y de Sistema
        base_fmt = (
            "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> "
            "<level>[{level}]</level> - "
            "<level>{message}</level>"
        )

        # 3.2. Formatear los logs que no son de Uvicorn ni de Sistema, incluyendo [Thread] y [Request-ID]
        trace_fmt = (
            "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> "
            "<level>[{level}]</level> "
            "<cyan>[{extra[request_id]}]</cyan> "
            "<magenta>[{extra[thread_name]}]</magenta> "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        def create_filter(module_name):
            return lambda record: record["extra"].get("module") == module_name

        # 4. Configurar un sink (archivo) por cada módulo definido
        for module in conf["modules"]:
            log_file = base_dir / f"{module}.log"

            is_domain = module not in ["system", "access"]
            selected_fmt = trace_fmt if is_domain else base_fmt

            # El 'filter' asegura que solo los logs marcados con este módulo lleguen al archivo
            logger.add(
                sink = log_file,
                level = "DEBUG" if settings.ENV_STATE == "dev" else "INFO",
                format = selected_fmt,
                filter = create_filter(module),
                rotation = hybrid_rotation_logic,
                retention = conf["retention"],
                compression = "zip",
                enqueue = conf["enqueue"],
                backtrace = conf["backtrace"],
                diagnose = True,
                delay = conf["delay"]
            )

        # 5. Sink para consola (opcional para desarrollo)
        logger.add(sink = sys.stdout, level = "INFO", colorize = True)
        print("🛠️ Logging configurado en modo DESARROLLO (Ficheros locales)")

        # 6. Silenciar los loggers originales y redirigirlos
        logging.basicConfig(handlers = [InterceptHandler()], level = 0, force = True)

        for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
            _logger = logging.getLogger(name)
            _logger.handlers = [InterceptHandler()]
            _logger.propagate = False


def get_logger(name: str):
    return logger.bind(module = name)
