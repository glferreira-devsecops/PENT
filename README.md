# Penta - Ferramenta de Automação de Pentest (v1.0.0)

[![GitHub license](https://img.shields.io/github/license/FuturoDevJunior/PENT)](https://github.com/FuturoDevJunior/PENT/blob/FuturoDevJunior-v2.1/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/FuturoDevJunior/PENT)](https://github.com/FuturoDevJunior/PENT)
[![GitHub forks](https://img.shields.io/github/forks/FuturoDevJunior/PENT)](https://github.com/FuturoDevJunior/PENT)
[![GitHub issues](https://img.shields.io/github/issues/FuturoDevJunior/PENT)](https://github.com/FuturoDevJunior/PENT/issues)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
<a href="https://buymeacoffee.com/devferreirag" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

<p align="center">
  <img src="https://raw.githubusercontent.com/FuturoDevJunior/PENT/FuturoDevJunior-v2.1/docs/penta_logo.png" alt="Penta Logo" width="200"/>
</p>

<p align="center">
  <strong>Uma ferramenta de código aberto e automatizada para acelerar as fases iniciais de um Pentest, focada na coleta de informações e identificação de vulnerabilidades comuns.</strong>
</p>

<p align="center">
  <a href="#-funcionalidades">Funcionalidades</a> •
  <a href="#-requisitos">Requisitos</a> •
  <a href="#-instalação">Instalação</a> •
  <a href="#-uso">Uso</a> •
  <a href="#-configuração">Configuração</a> •
  <a href="#-saída">Saída</a> •
  <a href="#-apoie-o-projeto">Apoie</a> •
  <a href="#-licença">Licença</a> •
  <a href="#-aviso-legal">Aviso Legal</a>
</p>

---

`Penta` (anteriormente SuperScanner) é uma ferramenta de **código aberto**, desenvolvida em Python 3 para auxiliar profissionais de segurança ofensiva e entusiastas. Ela automatiza tarefas repetitivas como a busca e validação de proxies, a execução de *Google Dorks* (via DuckDuckGo com Selenium Stealth para evitar bloqueios), testes básicos de *SQL Injection* usando o `sqlmap` e varreduras de portas e serviços com `Nmap` em hosts identificados como potencialmente vulneráveis.

**Autor:** [linkedin.com/in/devferreirag](https://linkedin.com/in/devferreirag)
**Repositório:** [https://github.com/FuturoDevJunior/PENT](https://github.com/FuturoDevJunior/PENT)

**Este é um projeto de código aberto sob a [Licença MIT](https://github.com/FuturoDevJunior/PENT/blob/FuturoDevJunior-v2.1/LICENSE). Sinta-se à vontade para contribuir, reportar issues e explorar o código! Se gostar do projeto, considere apoiar seu desenvolvimento.**

---

## ✨ Funcionalidades

* **🌐 Coleta e Validação de Proxies:** Baixa listas de proxies HTTP de múltiplas fontes públicas e testa sua funcionalidade, mantendo um cache dos proxies ativos para reutilização.
* **🔎 Dorking Automatizado:** Utiliza o DuckDuckGo através do Selenium com `selenium-stealth` para realizar buscas com *dorks* customizáveis, minimizando a chance de bloqueios por CAPTCHA. Possui fallback para `duckduckgo_search` caso o Selenium não esteja configurado.
* **💉 Testes de SQL Injection:** Integra-se com a poderosa ferramenta `sqlmap` para testar as URLs encontradas no dorking em busca de vulnerabilidades de SQL Injection.
* **📡 Varredura Nmap:** Para cada host identificado como vulnerável a SQLi, realiza uma varredura Nmap (`-sV -T4`) para identificar portas abertas e versões de serviços.
* **📊 Relatórios Detalhados:** Gera um relatório final em formato JSON (`super_scanner_report.json`) contendo os proxies funcionais, URLs coletadas e URLs vulneráveis.
* **🖥️ Interface Amigável:** Utiliza a biblioteca `rich` para uma exibição colorida e organizada no terminal, com *fallback* para modo texto simples caso a `rich` não esteja instalada.

---

## 📋 Requisitos

### Software:

* **Python 3.8+**
* **Google Chrome:** Necessário para o Dorking via Selenium.
* **sqlmap:** Deve estar instalado e acessível através do `PATH` do sistema. ([Instalação](http://sqlmap.org/))
* **Nmap:** Deve estar instalado e acessível através do `PATH` do sistema. ([Instalação](https://nmap.org/download.html))

### Bibliotecas Python:

As dependências estão listadas no arquivo `requirements.txt`. As principais são:

* `requests`
* `rich` (Opcional, para interface melhorada)
* `selenium`
* `selenium-stealth` (Opcional, mas recomendado para Dorking)
* `duckduckgo_search` (Fallback para Dorking)
* `beautifulsoup4`

---

## 🚀 Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/FuturoDevJunior/PENT.git](https://github.com/FuturoDevJunior/PENT.git)
    cd PENT
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # venv\Scripts\activate    # No Windows
    ```

3.  **Instale as dependências Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Instale `sqlmap` e `Nmap`:** Siga as instruções de instalação para o seu sistema operacional nos links fornecidos na seção [Requisitos](#-requisitos) e garanta que ambos estejam no `PATH`.

---

## 🏃 Uso

Para iniciar a ferramenta, basta executar o script principal:

```bash
python scanner.py
