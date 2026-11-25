# [IA] Gemini – script para download e descompactação do Bitcoin OTC (SNAP) em data/dataset_parte2/.
import gzip
import shutil
import urllib.request
from pathlib import Path

PASTA = Path(__file__).parent
PASTA.mkdir(parents=True, exist_ok=True)

URL = "https://snap.stanford.edu/data/soc-sign-bitcoinotc.csv.gz"
ARQUIVO_GZ = PASTA / "soc-sign-bitcoinotc.csv.gz"
ARQUIVO_CSV = PASTA / "soc-sign-bitcoinotc.csv"

print(f"Baixando {URL}...")
urllib.request.urlretrieve(URL, ARQUIVO_GZ)

with gzip.open(ARQUIVO_GZ, "rb") as f_in, open(ARQUIVO_CSV, "wb") as f_out:
    shutil.copyfileobj(f_in, f_out)

ARQUIVO_GZ.unlink()
print(f"Dataset salvo com sucesso em: {ARQUIVO_CSV}")