import os
import re
import time

# Função para limpar e normalizar um domínio
def clean_and_normalize_domain(domain_line):
    """
    Limpa e normaliza uma linha de domínio, removendo ||, ^, e @@||
    para obter apenas o domínio puro.
    """
    domain = domain_line.strip().lower()

    # Remover @@|| e ^
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
    
    # Ignorar linhas de comentário, regras que não são domínios puros, ou IPs puros
    if not domain or domain.startswith(('#', '!')) or domain.startswith('/') or \
       ' ' in domain or not re.match(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*\.[a-z]{2,}$", domain):
        return None

    return domain

def clean_personal_whitelist():
    whitelist_file_path = os.path.join('whitelists', 'personal-whitelist.txt')
    
    if not os.path.exists(whitelist_file_path):
        print(f"Erro: O ficheiro '{whitelist_file_path}' não foi encontrado.")
        print("Por favor, certifique-se de que o ficheiro existe na pasta 'whitelists'.")
        return

    unique_domains = set()
    initial_domain_count = 0

    print(f"A processar o ficheiro: {whitelist_file_path}")

    # Passo 1: Ler todos os domínios e adicionar a um conjunto para remover duplicados
    with open(whitelist_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            clean_domain = clean_and_normalize_domain(line)
            if clean_domain:
                unique_domains.add(clean_domain)
                initial_domain_count += 1
    
    # Passo 2: Reescrever o ficheiro com os domínios únicos e ordenados
    with open(whitelist_file_path, 'w', encoding='utf-8') as f:
        # Opcional: Adicionar um cabeçalho ao ficheiro
        f.write("! Personal Whitelist (Cleaned and Sorted)\n")
        f.write(f"! Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime())}\n")
        f.write("!\n")
        
        for domain in sorted(list(unique_domains)):
            f.write(f"{domain}\n") # Escreve o domínio limpo, sem || ^

    final_domain_count = len(unique_domains)
    
    print("\n--- Limpeza Concluída ---")
    print(f"Domínios lidos inicialmente (incluindo duplicados/inválidos): {initial_domain_count}")
    print(f"Domínios únicos e válidos escritos para '{whitelist_file_path}': {final_domain_count}")

    if initial_domain_count > final_domain_count:
        duplicates_removed = initial_domain_count - final_domain_count
        print(f"Foram removidos {duplicates_removed} domínios duplicados/inválidos.")
    else:
        print("Não foram encontrados domínios duplicados ou inválidos. O ficheiro já estava limpo.")

if __name__ == '__main__':
    clean_personal_whitelist()
