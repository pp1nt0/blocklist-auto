#!/bin/bash
set -e

# 🔁 Vai para a raiz do projeto
cd "$(dirname "$0")/.."

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
  curl -s "$url" | grep '^||.*\\^$' >> blocklists/consolidated.txt
done

echo "✅ Lista consolidada criada em blocklists/consolidated.txt"
