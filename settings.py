import re
from os import getenv
from dotenv import load_dotenv

load_dotenv()
LISTOFNODES = re.sub(r' ','',getenv('LISTOFNODES','')).split(',')
MemoryForOs = int(getenv('MemoryForOs'))
CpuForOs = int(getenv('CpuForOs'))