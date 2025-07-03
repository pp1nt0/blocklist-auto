#!/bin/bash
set -ex

# Vai para a raiz do projeto
cd "$(dirname "$0")/.."

echo "🔧 Verificando pasta blocklists..."
mkdir -p blocklists || { echo "Erro a criar pasta blocklists"; exit 1; }
touch blocklists/teste.txt || { echo "Erro a criar ficheiro teste.txt"; exit 1; }
rm blocklists/teste.txt

echo "🔄 A descarregar blocklists..."

LISTAS=(
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_51.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_5.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_61.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_63.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_60.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_44.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_7.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_8.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_18.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_10.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_9.txt"
  "https://adguardteam.github.io/HostlistsRegistry/assets/filter_11.txt"
)

> blocklists/consolidated.txt

for url in "${LISTAS[@]}"; do
  echo "# Fonte: $url" >> blocklists/consolidated.txt
  curl -s "$url" | grep '^||.*\\^$' >> blocklists/consolidated.txt || { echo "Erro no curl $url"; exit 1; }
done

echo "✅ Lista consolidada criada em blocklists/consolidated.txt"
