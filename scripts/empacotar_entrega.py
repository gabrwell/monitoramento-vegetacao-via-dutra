"""Cria um ZIP limpo para entrega e execução no Colab ou no VS Code."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
DESTINO = ROOT / "trabalho_faculdade4_colab.zip"
INCLUIR = (
    ROOT / ".gitignore",
    ROOT / "README.md",
    ROOT / "requirements.txt",
    ROOT / "requirements_colab.txt",
    ROOT / "pyproject.toml",
    ROOT / "config",
    ROOT / "data",
    ROOT / "docs",
    ROOT / "notebooks",
    ROOT / "outputs",
    ROOT / "relatorio",
    ROOT / "scripts",
    ROOT / "src",
    ROOT / "tests",
)
IGNORAR_PARTES = {".cache", ".git", ".pytest_cache", ".venv", "__pycache__"}


def arquivos():
    for item in INCLUIR:
        candidatos = [item] if item.is_file() else item.rglob("*")
        for caminho in candidatos:
            if not caminho.is_file():
                continue
            relativo = caminho.relative_to(ROOT)
            if any(parte in IGNORAR_PARTES for parte in relativo.parts):
                continue
            if caminho.suffix.lower() in {".pyc", ".pyo"}:
                continue
            yield caminho, relativo


def main():
    with ZipFile(DESTINO, "w", compression=ZIP_DEFLATED, compresslevel=9) as pacote:
        for caminho, relativo in arquivos():
            destino = Path("trabalho_faculdade4") / relativo
            pacote.write(caminho, destino.as_posix())
    print(DESTINO)


if __name__ == "__main__":
    main()
