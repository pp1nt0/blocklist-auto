import os
import requests
import glob
import time

def download_file(url, destination_path):
    """Descarrega um ficheiro de uma URL para um caminho de destino."""
    try:
        print(f"A descarregar: {url} para {destination_path}")
        response = requests.get(url, stream=True, timeout=10) # Adicionado timeout
        response.raise_for_status() # Lança um erro para códigos de status HTTP maus

        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Descarregado com sucesso: {url}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao descarregar {url}: {e}")
        return False

def generate_combined_list():
    sources_file = 'sources.txt'
    downloaded_blocklists_dir = 'blocklists/downloaded'
    custom_blocklists_dir = 'blocklists/custom'
    whitelists_dir = 'whitelists'
    output_file = 'combined-blocklist.txt'

    # 1. Descarregar listas de bloqueio externas
    os.makedirs(downloaded_blocklists_dir, exist_ok=True) # Garante que a pasta existe

    if os.path.exists(sources_file):
        with open(sources_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        for url in urls:
            # Usa o nome do ficheiro da URL para guardar
            filename = os.path.basename(url.split('?')[0]) # Remove parâmetros de query
            if not filename.endswith('.txt'):
                filename += '.txt' # Garante que tem extensão .txt
            destination_path = os.path.join(downloaded_blocklists_dir, filename)
            download_file(url, destination_path)
            time.sleep(1) # Pequeno atraso para evitar sobrecarregar servidores

    # 2. Carregar domínios da whitelist
    whitelist_domains = set()
    for filepath in glob.glob(os.path.join(whitelists_dir, '*.txt')):
        print(f"A carregar whitelist de: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                domain = line.strip().lower()
                if domain and not domain.startswith('#'):
                    whitelist_domains.add(domain)

    # 3. Carregar e filtrar domínios das blocklists (descarregadas e personalizadas)
    combined_domains = set()

    # Processar listas descarregadas
    for filepath in glob.glob(os.path.join(downloaded_blocklists_dir, '*.txt')):
        print(f"A processar blocklist descarregada: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                domain = line.strip().lower()
                # Tenta extrair o domínio se a linha for uma regra de AdGuard/Adblock Plus
                if domain.startswith('||') and domain.endswith('^'):
                    domain = domain[2:-1]
                elif domain.startswith('@@||') and domain.endswith('^'): # Linhas de whitelist em algumas listas
                    domain = domain[4:-1]
                    if domain in whitelist_domains: # Se já for whitelist, não precisamos adicionar
                        continue
                    else: # Se for uma whitelist na blocklist, adiciona à nossa whitelist temporariamente
                        whitelist_domains.add(domain)
                        continue # E não adiciona à blocklist combinada
                
                # Ignorar linhas de comentário, IPs, e outras regras complexas por simplicidade
                if not domain or domain.startswith('#') or domain.startswith('!') or \
                   domain.startswith('/') or domain.startswith('127.0.0.1') or \
                   domain.startswith('0.0.0.0') or '.' not in domain:
                    continue

                if domain not in whitelist_domains:
                    combined_domains.add(domain)

    # Processar listas personalizadas
    for filepath in glob.glob(os.path.join(custom_blocklists_dir, '*.txt')):
        print(f"A processar blocklist personalizada: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                domain = line.strip().lower()
                if domain and not domain.startswith('#') and '.' in domain: # Filtro básico
                    if domain not in whitelist_domains:
                        combined_domains.add(domain)

    # 4. Escrever para o ficheiro de saída
    with open(output_file, 'w', encoding='utf-8') as f:
        # Adiciona um cabeçalho para o AdGuard Home
        f.write("! Title: Combined AdGuard Home Blocklist\n")
        f.write(f"! Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S GMT')}\n")
        f.write("! Expires: 1 day\n") # AdGuard Home pode usar isto para gerir atualizações
        f.write("! Homepage: https://github.com/O_TEU_UTILIZADOR/adguard-blocklists\n") # Opcional
        f.write("! Version: 1.0\n") # Opcional

        for domain in sorted(list(combined_domains)):
            f.write(domain + '\n')

    print(f"Lista consolidada gerada em '{output_file}' com {len(combined_domains)} domínios.")

if __name__ == '__main__':
    # Instala a biblioteca requests se ainda não a tiveres: pip install requests
    try:
        import requests
    except ImportError:
        print("A biblioteca 'requests' não está instalada. Por favor, instala-a com: pip install requests")
        exit(1)
    generate_combined_list()