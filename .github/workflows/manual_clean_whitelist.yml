import os
import re
import time
from urllib.parse import urlparse # Importar para analisar URLs

# Função para limpar e normalizar um domínio
def clean_and_normalize_domain(domain_line):
    """
    Limpa e normaliza uma linha de domínio, removendo ||, ^, e @@||,
    bem como paths, query parameters, e URLs completas,
    para obter apenas o domínio raiz ou subdomínio mais relevante.
    """
    domain = domain_line.strip().lower()

    # Se a linha for uma URL completa, vamos analisá-la primeiro
    # Verifica se começa com um protocolo comum (http/https)
    if domain.startswith(('http://', 'https://')):
        try:
            parsed_url = urlparse(domain)
            domain = parsed_url.netloc # Obtém apenas o 'host' (ex: www.example.com ou example.com)
            if not domain: # Se não conseguiu extrair, pode ser um problema
                return None
        except ValueError: # URL mal formatado
            return None

    # Remover @@|| e ^ (se ainda existirem após a análise de URL)
    if domain.startswith('@@||') and domain.endswith('^'):
        domain = domain[4:-1]
    # Remover || e ^
    elif domain.startswith('||') and domain.endswith('^'):
        domain = domain[2:-1]
    # Remover 0.0.0.0 ou 127.0.0.1 e o espaço
    elif domain.startswith(('0.0.0.0 ', '127.0.0.1 ')):
        parts = domain.split(' ', 1)
        if len(parts) > 1:
            domain = parts[1].strip()
        else:
            return None # Não há domínio após o IP
    
    # Remover "www." se existir no início
    if domain.startswith('www.'):
        domain = domain[4:]

    # Remover barra final se existir
    if domain.endswith('/'):
        domain = domain[:-1]

    # Expressão regular para validar um domínio.
    # Esta regex é um pouco mais abrangente, permitindo subdomínios e TLDs comuns.
    # Exclui IPs puros e comentários aqui.
    domain_pattern = re.compile(
        r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.[a-z0-9-]{1,63}(?<!-))*(?<!\d)\.[a-z]{2,63}$"
    )
    
    # Ignorar linhas que são comentários, vazias, ou não correspondem a um formato de domínio válido
    if not domain or domain.startswith(('#', '!')) or domain.startswith('/') or \
       ' ' in domain or not domain_pattern.match(domain):
        return None

    return domain

def clean_personal_whitelist():
    whitelist_file_path = os.path.join('whitelists', 'personal-whitelist.txt')
    
    if not os.path.exists(whitelist_file_path):
        print(f"Erro: O ficheiro '{whitelist_file_path}' não foi encontrado.")
        print("Por favor, certifique-se de que o ficheiro existe na pasta 'whitelists'.")
        return

    unique_domains = set()
    initial_line_count = 0 # Contagem de linhas iniciais, incluindo comentários/lixo

    print(f"A processar o ficheiro: {whitelist_file_path}")

    # Passo 1: Ler todos os domínios e adicionar a um conjunto para remover duplicados
    with open(whitelist_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            initial_line_count += 1
            clean_domain = clean_and_normalize_domain(line)
            if clean_domain:
                unique_domains.add(clean_domain)
    
    # Passo 2: Reescrever o ficheiro com os domínios únicos e ordenados
    with open(whitelist_file_path, 'w', encoding='utf-8') as f:
        f.write("! Personal Whitelist (Cleaned, Homogenized, and Sorted)\n")
        f.write(f"! Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime())}\n")
        f.write("!\n") # Linha vazia para clareza
        
        for domain in sorted(list(unique_domains)):
            f.write(f"{domain}\n")

    final_domain_count = len(unique_domains)
    
    print("\n--- Limpeza e Homogeneização Concluída ---")
    print(f"Linhas processadas inicialmente: {initial_line_count}")
    print(f"Domínios únicos, válidos e homogeneizados escritos para '{whitelist_file_path}': {final_domain_count}")

    if initial_line_count > final_domain_count:
        removed_items_count = initial_line_count - final_domain_count
        print(f"Foram removidos {removed_items_count} entradas duplicadas, inválidas ou simplificadas.")
    else:
        print("Não foram encontrados domínios para remover ou simplificar. O ficheiro já estava limpo e homogéneo.")

if __name__ == '__main__':
    clean_personal_whitelist()
