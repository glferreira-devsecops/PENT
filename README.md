# Penta - Ferramenta de Automação de Pentest (v1.0.0)

<p align="center">
  <a href="https://github.com/FuturoDevJunior/PENT/blob/FuturoDevJunior-v2.1/LICENSE" target="_blank"><img src="https://img.shields.io/github/license/FuturoDevJunior/PENT" alt="Licença GitHub"></a>
  <a href="https://github.com/FuturoDevJunior/PENT" target="_blank"><img src="https://img.shields.io/github/stars/FuturoDevJunior/PENT?style=social" alt="Estrelas GitHub"></a>
  <a href="https://github.com/FuturoDevJunior/PENT" target="_blank"><img src="https://img.shields.io/github/forks/FuturoDevJunior/PENT?style=social" alt="Forks GitHub"></a>
  <a href="https://github.com/FuturoDevJunior/PENT/issues" target="_blank"><img src="https://img.shields.io/github/issues/FuturoDevJunior/PENT" alt="Issues GitHub"></a>
  <a href="https://www.python.org/downloads/" target="_blank"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"></a>
  <br>
  <a href="https://buymeacoffee.com/devferreirag" target="_blank"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Pague-me um Café"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/FuturoDevJunior/PENT/FuturoDevJunior-v2.1/penta_logo.png" alt="Logo Penta" width="200"/>
</p>

<p align="center">
  <strong>Uma ferramenta de código aberto e automatizada para acelerar as fases iniciais de um Pentest, focada na recolha de informações e identificação de vulnerabilidades comuns.</strong>
</p>

<p align="center">
  <a href="#-funcionalidades">Funcionalidades</a> •
  <a href="#-estrutura-do-repositório">Estrutura</a> •
  <a href="#-requisitos">Requisitos</a> •
  <a href="#-instalação">Instalação</a> •
  <a href="#-uso">Uso</a> •
  <a href="#-configuração">Configuração</a> •
  <a href="#-saída">Saída</a> •
  <a href="#-apoie-o-projeto">Apoie</a> •
  <a href="#-contribuição">Contribuição</a> •
  <a href="#-licença">Licença</a> •
  <a href="#-aviso-legal">Aviso Legal</a>
</p>

---

`Penta` (anteriormente SuperScanner) é uma ferramenta de **código aberto**, desenvolvida em Python 3 para auxiliar profissionais de segurança ofensiva e entusiastas. Ela automatiza tarefas repetitivas como a busca e validação de proxies, a execução de *Google Dorks* (via DuckDuckGo com Selenium Stealth para evitar bloqueios), testes básicos de *SQL Injection* usando o `sqlmap` e varreduras de portas e serviços com `Nmap` em hosts identificados como potencialmente vulneráveis.

**Autor:** [linkedin.com/in/devferreirag](https://linkedin.com/in/devferreirag)

**Repositório:** [https://github.com/FuturoDevJunior/PENT](https://github.com/FuturoDevJunior/PENT)

**Este é um projeto de código aberto sob a [Licença MIT](https://github.com/FuturoDevJunior/PENT/blob/FuturoDevJunior-v2.1/LICENSE). Sinta-se à vontade para contribuir, reportar issues e explorar o código! Se gostar do projeto, considere apoiar o seu desenvolvimento.**

---

## ✨ Funcionalidades

* **🌐 Recolha e Validação de Proxies:** Baixa listas de proxies HTTP de múltiplas fontes públicas e testa a sua funcionalidade, mantendo uma cache dos proxies ativos para reutilização.
* **🔎 Dorking Automatizado:** Utiliza o DuckDuckGo através do Selenium com `selenium-stealth` para realizar buscas com *dorks* personalizáveis, minimizando a chance de bloqueios por CAPTCHA. Possui fallback para `duckduckgo_search` caso o Selenium não esteja configurado.
* **💉 Testes de SQL Injection:** Integra-se com a poderosa ferramenta `sqlmap` para testar as URLs encontradas no dorking em busca de vulnerabilidades de SQL Injection.
* **📡 Varredura Nmap:** Para cada host identificado como vulnerável a SQLi, realiza uma varredura Nmap (`-sV -T4`) para identificar portas abertas e versões de serviços.
* **📊 Relatórios Detalhados:** Gera um relatório final em formato JSON (`super_scanner_report.json`) contendo os proxies funcionais, URLs recolhidas e URLs vulneráveis.
* **🖥️ Interface Amigável:** Utiliza a biblioteca `rich` para uma exibição colorida e organizada no terminal, com *fallback* para modo texto simples caso a `rich` não esteja instalada.

---


## 📋 Requisitos

### Software:

* **Python 3.8+**
* **Google Chrome:** Necessário para o Dorking via Selenium.
* **sqlmap:** Deve estar instalado e acessível através do `PATH` do sistema. ([Instalação](http://sqlmap.org/))
* **Nmap:** Deve estar instalado e acessível através do `PATH` do sistema. ([Instalação](https://nmap.org/download.html))

### Bibliotecas Python:

As dependências estão listadas no arquivo `requirements.txt`. Para instalá-las, use:

```bash
pip install -r requirements.txt
```



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


Para iniciar a ferramenta, basta executar o script `scanner.py` na raiz do projeto:


```bash
python scanner.py
```
O script seguirá o fluxo:


1.  Verificará a presença de `sqlmap` e `Nmap`.
2.  Carregará proxies de uma cache ou baixará e testará novos proxies.
3.  Lerá as *dorks* do arquivo `dorks.txt`.
4.  Executará as buscas no DuckDuckGo.
5.  Testará as URLs encontradas com `sqlmap`.
6.  Escaneará os hosts vulneráveis com `Nmap`.
7.  Gerará o relatório final.


---


## ⚙️ Configuração


* **Dorks:** Você pode personalizar as *dorks* a serem utilizadas editando o arquivo `dorks.txt`. Adicione uma *dork* por linha. Linhas iniciadas com `#` são ignoradas. Se o arquivo não existir, a ferramenta usará algumas *dorks* padrão.


* **Constantes Globais:** Diversas configurações (como número de threads, timeouts, fontes de proxy, etc.) podem ser ajustadas diretamente nas variáveis globais no início do arquivo `scanner.py`. *Modifique com cautela.*


---


## 📄 Saída


A ferramenta gera os seguintes artefactos:


* **`super_scanner_report.json`:** Um arquivo JSON contendo um resumo da execução, incluindo proxies, URLs encontradas e URLs vulneráveis.


* **`.working_proxies_cache.json`:** Uma cache dos proxies funcionais para acelerar execuções futuras (válido por 24 horas por padrão).


* **`nmap_output/`:** Um diretório contendo os resultados das varreduras Nmap (um arquivo `.txt` para cada host escaneado).


* **`sqlmap_output/`:** (Pode ser gerado pelo sqlmap) Potencialmente, diretórios de saída do sqlmap.


---


## ☕ Apoie o Projeto


Gostou do Penta? Se esta ferramenta foi útil para você, considere pagar um café para o desenvolvedor! A sua contribuição ajuda a manter o projeto ativo e motiva o desenvolvimento de novas funcionalidades.


<p align="center">
  <a href="https://buymeacoffee.com/devferreirag" target="_blank">
    <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Pague-me um Café">
  </a>
</p>


---


## 🤝 Contribuição


Contribuições são sempre bem-vindas! Se você tem ideias para melhorias, novas funcionalidades ou encontrou algum bug, sinta-se à vontade para:


1.  Fazer um *Fork* do projeto.
2.  Criar uma nova *Branch* (`git checkout -b feature/SuaFeature`).
3.  Fazer o *Commit* das suas mudanças (`git commit -m 'Adiciona SuaFeature'`).
4.  Fazer o *Push* para a Branch (`git push origin feature/SuaFeature`).
5.  Abrir um *Pull Request*.


Por favor, tente manter um estilo de código consistente e documente as suas mudanças.


---


## 📜 Licença


Este projeto é distribuído sob a licença [MIT](https://github.com/FuturoDevJunior/PENT/blob/FuturoDevJunior-v2.1/LICENSE). Consulte o arquivo `LICENSE` para obter mais informações.


---


## ⚠️ Aviso Legal


Esta ferramenta foi desenvolvida para **fins educacionais e de pesquisa em segurança**. O uso desta ferramenta para atacar alvos sem consentimento prévio e explícito é **ilegal** e **antiético**. O autor **não se responsabiliza** por qualquer mau uso ou dano causado por esta ferramenta. **Use por sua conta e risco e sempre dentro da legalidade.**

