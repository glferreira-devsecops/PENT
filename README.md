# penta

SuperScanner - Ferramenta de automação para pentest e coleta de vulnerabilidades.

## Visão Geral
O penta automatiza buscas dorking, testes de proxies, SQL Injection (SQLi) e varreduras Nmap, gerando relatórios detalhados para profissionais de segurança.

## Funcionalidades
- Busca proxies elite/anon de múltiplas fontes
- Testa proxies em paralelo
- Busca URLs vulneráveis via dorking (DuckDuckGo + Selenium Stealth)
- Testa SQLi em URLs usando sqlmap
- Varre hosts vulneráveis com Nmap
- Gera relatório JSON
- Interface colorida com Rich (fallback para modo texto)

## Requisitos
- Python 3.8+
- Google Chrome instalado (para Selenium)
- sqlmap e nmap instalados no PATH

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/FuturoDevJunior/penta.git
   cd penta
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
Execute o scanner principal:
```bash
python scanner.py
```

- O relatório será salvo em `super_scanner_report.json`.
- Edite o arquivo `dorks.txt` para personalizar as buscas.

## Estrutura do Projeto
- `scanner.py`: script principal
- `dorks.txt`: dorks para busca
- `requirements.txt`: dependências Python
- `LICENSE`: licença MIT

## Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Contato
Desenvolvido por [DevFerreiraG](https://linkedin.com/in/devferreirag)

## Versão
- 1.0.0 (commit inicial)

## Changelog
- Estrutura inicial do projeto
- Documentação completa
- Código limpo, modular e escalável
- Pronto para produção e colaboração
