import os
import requests
import glob
import time

def download_file(url, destination_path):
    """Descarrega um ficheiro de uma URL para um caminho de destino."""
    try:
        print(f"A descarregar: {url} para {destination_path}")
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

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
    os.makedirs(downloaded_blocklists_dir, exist_ok=True)

    if os.path.exists(sources_file):
        with open(sources_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        for url in urls:
            filename = os.path.basename(url.split('?')[0])
            if not filename.endswith('.txt'):
                filename += '.txt'
            destination_path = os.path.join(downloaded_blocklists_dir, filename)
            download_file(url, destination_path)
            time.sleep(1)

    # 2. Carregar domínios da whitelist
    whitelist_domains = set()
    for filepath in glob.glob(os.path.join(whitelists_dir, '*.txt')):
        print(f"A carregar whitelist de: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                domain = line.strip().lower()
                if domain and not domain.startswith('#'):
                    # Armazenamos a whitelist no formato "limpo" (sem || ^) para comparação
                    if domain.startswith('||') and domain.endswith('^'):
                        domain = domain[2:-1]
                    whitelist_domains.add(domain)

    # 3. Carregar e filtrar domínios das blocklists (descarregadas e personalizadas)
    combined_domains_raw = set() # Vamos armazenar domínios "limpos" aqui primeiro

    # Função auxiliar para processar linhas e extrair domínios
    def extract_and_add_domain(line, target_set, is_whitelist_check=False):
        domain = line.strip().lower()

        # Remove || e ^ se já existirem
        if domain.startswith('||') and domain.endswith('^'):
            domain = domain[2:-1]
        elif domain.startswith('@@||') and domain.endswith('^'):
            domain = domain[4:-1]
            if is_whitelist_check: # Se estivermos a processar uma linha de whitelist (@@)
                whitelist_domains.add(domain) # Adiciona à whitelist
            return # Não adicionamos domínios de whitelist à lista de bloqueio

        # Ignorar linhas de comentário, IPs, e outras regras complexas
        if not domain or domain.startswith('#') or domain.startswith('!') or \
           domain.startswith('/') or domain.startswith('127.0.0.1') or \
           domain.startswith('0.0.0.0') or '.' not in domain or \
           ' ' in domain: # Ignorar linhas com espaços no domínio (não é um domínio válido)
            return

        # Verificar se o domínio está na whitelist
        if domain not in whitelist_domains:
            target_set.add(domain) # Adiciona apenas o domínio "limpo"

    # Processar listas descarregadas
    for filepath in glob.glob(os.path.join(downloaded_blocklists_dir, '*.txt')):
        print(f"A processar blocklist descarregada: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                extract_and_add_domain(line, combined_domains_raw, is_whitelist_check=True) # Verificar @@||^

    # Processar listas personalizadas
    for filepath in glob.glob(os.path.join(custom_blocklists_dir, '*.txt')):
        print(f"A processar blocklist personalizada: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                extract_and_add_domain(line, combined_domains_raw, is_whitelist_check=False) # Não esperamos @@||^ aqui

    # 4. Escrever para o ficheiro de saída no formato ||domínio^
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("! Title: Combined AdGuard Home Blocklist\n")
        f.write(f"! Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S GMT')}\n")
        f.write("! Expires: 1 day\n")
        f.write("! Homepage: https://github.com/O_TEU_UTILIZADOR/adguard-blocklists\n")
        f.write("! Version: 1.0\n")
        f.write("!\n") # Linha vazia para clareza

        count = 0
        for domain in sorted(list(combined_domains_raw)):
            # Formata cada domínio com || e ^
            f.write(f"||{domain}^\n")
            count += 1

    print(f"Lista consolidada gerada em '{output_file}' com {count} domínios no formato AdGuard/Adblock Plus.")

if __name__ == '__main__':
    try:
        import requests
    except ImportError:
        print("A biblioteca 'requests' não está instalada. Por favor, instala-a com: pip install requests")
        exit(1)
    generate_combined_list()