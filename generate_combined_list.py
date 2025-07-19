import os
import requests
import glob
import time
import re # Importa a biblioteca de expressões regulares

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

# Função para limpar e normalizar um domínio
def clean_and_normalize_domain(domain_line):
    # Remove espaços em branco do início/fim e converte para minúsculas
    domain = domain_line.strip().lower()

    # Se começar com "@@||" e terminar com "^", é uma regra de whitelist na blocklist
    if domain.startswith('@@||') and domain.endswith('^'):
        return domain[4:-1], 'whitelist' # Retorna o domínio limpo e o tipo 'whitelist'

    # Se começar com "||" e terminar com "^", é uma regra de bloqueio
    elif domain.startswith('||') and domain.endswith('^'):
        return domain[2:-1], 'block' # Retorna o domínio limpo e o tipo 'block'

    # Se começar com "0.0.0.0" ou "127.0.0.1", tenta extrair o domínio
    elif domain.startswith(('0.0.0.0 ', '127.0.0.1 ')):
        parts = domain.split(' ', 1)
        if len(parts) > 1:
            domain_part = parts[1].strip()
            # Certifica-se de que é um domínio válido (não um IP ou outro lixo)
            if re.match(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*\.[a-z]{2,}$", domain_part):
                return domain_part, 'block'
            else:
                return None, 'invalid' # Não é um domínio válido após o IP
        return None, 'invalid' # Não há domínio após o IP

    # Linhas que podem ser domínios diretos, sem || ^
    elif re.match(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*\.[a-z]{2,}$", domain):
        # Verifica se a linha é um domínio válido (ignora IPs puros, comentários, etc.)
        return domain, 'block'

    # Ignorar linhas de comentário, IPs puros, e outras regras complexas ou vazias
    if not domain or domain.startswith(('#', '!')) or domain.startswith('/') or '.' not in domain or ' ' in domain:
        return None, 'invalid'

    # Se chegou aqui, é um formato desconhecido ou inválido para o nosso objetivo
    return None, 'invalid'


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
                domain, domain_type = clean_and_normalize_domain(line)
                if domain and (domain_type == 'block' or domain_type == 'whitelist'): # Considera ambos para a whitelist
                    whitelist_domains.add(domain)

    # 3. Carregar e filtrar domínios das blocklists (descarregadas e personalizadas)
    combined_domains_raw = set()

    # Processar listas descarregadas
    for filepath in glob.glob(os.path.join(downloaded_blocklists_dir, '*.txt')):
        print(f"A processar blocklist descarregada: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                domain, domain_type = clean_and_normalize_domain(line)
                if domain_type == 'block' and domain not in whitelist_domains:
                    combined_domains_raw.add(domain)
                elif domain_type == 'whitelist': # Se uma blocklist tem uma regra @@||^
                    whitelist_domains.add(domain) # Adiciona à nossa whitelist

    # Processar listas personalizadas
    for filepath in glob.glob(os.path.join(custom_blocklists_dir, '*.txt')):
        print(f"A processar blocklist personalizada: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                domain, domain_type = clean_and_normalize_domain(line)
                # Assumimos que custom blocklists são apenas domínios para bloquear, não contêm @@||
                if domain_type == 'block' and domain not in whitelist_domains:
                    combined_domains_raw.add(domain)

    # 4. Escrever para o ficheiro de saída no formato ||domínio^
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("! Title: Combined AdGuard Home Blocklist\n")
        f.write(f"! Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime())}\n") # Usar gmtime para GMT
        f.write("! Expires: 1 day\n")
        f.write("! Homepage: https://github.com/pp1nt0/adguard-blocklists\n")
        f.write("! Version: 1.0\n")
        f.write("!\n")

        count = 0
        for domain in sorted(list(combined_domains_raw)):
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