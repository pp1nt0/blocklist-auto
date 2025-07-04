import os
import json
import requests
import base64
import re
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
load_dotenv() # Carrega as variáveis do .env
app = Flask(__name__)

# --- Funções de Ajuda (Copiadas do teu script clean_whitelist_duplicates.py) ---
# Certifica-te que estas funções estão atualizadas com a tua última versão!
def clean_and_normalize_domain(domain_line):
    domain = domain_line.strip().lower()
    if domain.startswith(('http://', 'https://')):
        try:
            parsed_url = urlparse(domain)
            domain = parsed_url.netloc
            if not domain: return None
        except ValueError: return None
    if domain.startswith('@@||') and domain.endswith('^'): domain = domain[4:-1]
    elif domain.startswith('||') and domain.endswith('^'): domain = domain[2:-1]
    elif domain.startswith(('0.0.0.0 ', '127.0.0.1 ')):
        parts = domain.split(' ', 1)
        if len(parts) > 1: domain = parts[1].strip()
        else: return None
    if domain.startswith('www.'): domain = domain[4:]
    if domain.endswith('/'): domain = domain[:-1]
    domain_pattern = re.compile(
        r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.[a-z0-9-]{1,63}(?<!-))*(?<!\d)\.[a-z]{2,63}$"
    )
    if not domain or domain.startswith(('#', '!')) or domain.startswith('/') or \
       ' ' in domain or not domain_pattern.match(domain): return None
    return domain
# --- Fim das Funções de Ajuda ---

# Configurações do GitHub (Coloca isto num ficheiro .env ou variáveis de ambiente para produção!)
# Para simplificar aqui, vamos ler do ambiente ou usar placeholders.
# É ALTAMENTE RECOMENDADO USAR VARIÁVEIS DE AMBIENTE OU UM FICHEIRO .env
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'O_TEU_UTILIZADOR' # <--- SUBSTITUI ISTO PELO TEU UTILIZADOR DO GITHUB
REPO_NAME = 'adguard-blocklists' # <--- SUBSTITUI ISTO PELO NOME DO TEU REPOSITÓRIO
FILE_PATH = 'whitelists/personal-whitelist.txt'
BRANCH = 'main' # <--- SUBSTITUI ISTO PELA TUA BRANCH PRINCIPAL (ex: 'main' ou 'master')

@app.route('/')
def index():
    # Serve a página HTML. O Flask procura por templates na pasta 'templates'
    return render_template('index.html')

@app.route('/add_to_whitelist', methods=['POST'])
def add_to_whitelist():
    if not GITHUB_TOKEN:
        return jsonify({'status': 'error', 'message': 'GITHUB_TOKEN not configured on server.'}), 500

    data = request.get_json()
    new_domain_raw = data.get('domain')

    if not new_domain_raw:
        return jsonify({'status': 'error', 'message': 'Dominio é obrigatório.'}), 400

    normalized_domain = clean_and_normalize_domain(new_domain_raw)

    if not normalized_domain:
        return jsonify({'status': 'error', 'message': f'Formato de domínio inválido ou não suportado: {new_domain_raw}'}), 400

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # 1. Obter o conteúdo atual do ficheiro
        get_file_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
        file_response = requests.get(get_file_url, headers=headers)
        file_response.raise_for_status()
        file_data = file_response.json()
        
        current_content_b64 = file_data['content']
        current_content = base64.b64decode(current_content_b64).decode('utf-8')
        sha = file_data['sha']

        # 2. Processar o conteúdo e adicionar o novo domínio
        existing_domains = set()
        for line in current_content.splitlines():
            domain = clean_and_normalize_domain(line)
            if domain:
                existing_domains.add(domain)

        if normalized_domain in existing_domains:
            return jsonify({'status': 'success', 'message': f'"{normalized_domain}" já existe na whitelist.'}), 200

        existing_domains.add(normalized_domain)
        updated_content_lines = sorted(list(existing_domains))
        
        # Adiciona cabeçalho como no teu script clean_personal_whitelist
        updated_content_lines.insert(0, '') # Linha vazia
        updated_content_lines.insert(0, f"! Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime())}")
        updated_content_lines.insert(0, "! Personal Whitelist (Cleaned, Homogenized, and Sorted)")

        updated_content = '\n'.join(updated_content_lines) + '\n' # Adiciona uma nova linha no final
        updated_content_b64 = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')

        # 3. Fazer o PUT para atualizar o ficheiro
        update_file_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        update_payload = {
            'message': f'Add {normalized_domain} to whitelist via Raspberry Pi web UI',
            'content': updated_content_b64,
            'sha': sha,
            'branch': BRANCH
        }
        update_response = requests.put(update_file_url, headers=headers, json=update_payload)
        update_response.raise_for_status()

        return jsonify({'status': 'success', 'message': f'"{normalized_domain}" adicionado à whitelist com sucesso.'}), 200

    except requests.exceptions.HTTPError as e:
        print(f"GitHub API Error: {e.response.status_code} - {e.response.text}")
        return jsonify({'status': 'error', 'message': f'Erro da API GitHub: {e.response.status_code} - {e.response.text}'}), e.response.status_code
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({'status': 'error', 'message': f'Ocorreu um erro interno: {str(e)}'}), 500

if __name__ == '__main__':
    # Em produção, usarias Gunicorn ou similar. Para testar:
    # app.run(host='0.0.0.0', port=5000, debug=True)
    pass
