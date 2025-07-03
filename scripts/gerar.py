import os

INPUT = "blocklists/consolidated.txt"
WHITELIST = "blocklists/whitelist.txt"
OUTPUT = "blocklists/final.txt"

print("📥 A ler whitelist...")
whitelist = set()
if os.path.exists(WHITELIST):
    with open(WHITELIST) as f:
        whitelist = set(line.strip().lower() for line in f if line.strip())

print(f"✅ {len(whitelist)} domínios na whitelist.")

domains = set()
with open(INPUT) as f:
    for line in f:
        line = line.strip()
        if line.startswith("||") and line.endswith("^"):
            domain = line[2:-1].lower()
            if domain not in whitelist:
                domains.add(domain)

print(f"📦 {len(domains)} domínios únicos após aplicar whitelist.")

# Eliminar subdomínios redundantes
def is_sub(sub, dom):
    return sub != dom and sub.endswith("." + dom)

print("🧹 A remover subdomínios redundantes...")
sorted_domains = sorted(domains, key=lambda x: x[::-1])
result = []

for domain in sorted_domains:
    if not any(is_sub(domain, d) for d in result):
        result.append(domain)

print(f"✅ Blocklist final: {len(result)} domínios")

with open(OUTPUT, "w") as f:
    for d in result:
        f.write(f"||{d}^\n")