import subprocess

# Pacotes usados segundo pipreqs
usados = {
    "gspread", "gspread_pandas", "jupyter_black", "matplotlib", "numpy",
    "oauth2client", "pandas", "plotly", "protobuf", "seaborn"
}

# Lê todos os pacotes instalados
with open("all.txt") as f:
    instalados = [line.split("==")[0].split("@")[0].strip() for line in f if line.strip()]

# Identifica os que não estão sendo usados
nao_usados = [pkg for pkg in instalados if pkg not in usados]

# Desinstala um por um (com confirmação)
for pkg in nao_usados:
    print(f"Desinstalando: {pkg}")
    subprocess.run(["pip", "uninstall", "-y", pkg])
