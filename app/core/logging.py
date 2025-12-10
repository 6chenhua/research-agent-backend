"""日志配置"""
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5)
        ]
    )
    
logger = logging.getLogger(__name__)
