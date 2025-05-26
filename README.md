<!-- Banner/Logo -->
<p align="center">
  <img src="https://img.shields.io/github/license/FuturoDevJunior/penta?color=blue&style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/github/workflow/status/FuturoDevJunior/penta/CI%20-%20Python%20Lint%20&%20Test/main?style=for-the-badge" alt="CI Status"/>
  <img src="https://img.shields.io/github/languages/top/FuturoDevJunior/penta?style=for-the-badge" alt="Top Language"/>
</p>

<h1 align="center">⚡️ PENTA - Pentest Automation Tool ⚡️</h1>

<p align="center">
  <b>Automação extrema para pentest, dorking, proxies, SQLi e Nmap.</b><br>
  <i>Segurança ofensiva, robustez e criatividade em cada linha de código.</i>
</p>

---

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&pause=1000&color=F70000&center=true&vCenter=true&width=900&lines=Automatize+seu+Pentest+com+Estilo!;Dorking%2C+Proxies%2C+SQLi%2C+Nmap+e+Relat%C3%B3rios+em+1+clique!;Pronto+para+produção+e+colaboração!"/>
</p>

---

## 🚀 Visão Geral

> O **PENTA** é a solução definitiva para automação de pentest, reunindo as melhores práticas de coleta de proxies, dorking, testes SQLi e varredura Nmap em um só lugar. Com interface colorida, relatórios detalhados e integração contínua, é a escolha dos profissionais que buscam eficiência, criatividade e resultados.

---

## ✨ Funcionalidades

- 🔎 **Dorking** avançado (DuckDuckGo + Selenium Stealth)
- 🕵️‍♂️ Busca e validação de proxies elite/anon de múltiplas fontes
- 💥 Testes SQLi automáticos com sqlmap
- 🛰️ Varredura de hosts vulneráveis com Nmap
- 📊 Relatórios JSON completos e prontos para auditoria
- 🎨 Interface colorida com [Rich](https://github.com/Textualize/rich) (fallback para modo texto)
- 🛡️ Fallbacks inteligentes para ambientes sem dependências opcionais
- 🔄 CI automatizado: lint (Ruff) + testes (pytest) em múltiplas versões do Python

---

## 🛠️ Instalação Rápida

```bash
# Clone o repositório
 git clone https://github.com/FuturoDevJunior/penta.git
 cd penta

# Instale as dependências
 pip install -r requirements.txt
```

---

## ⚡️ Como Usar

```bash
python scanner.py
```

- O relatório será salvo em `super_scanner_report.json`.
- Personalize suas buscas editando o arquivo `dorks.txt`.

---

## 🧩 Estrutura do Projeto

```
📁 penta/
 ├── scanner.py              # Script principal
 ├── dorks.txt               # Dorks para busca
 ├── requirements.txt        # Dependências Python
 ├── LICENSE                 # Licença MIT
 └── .github/
      └── workflows/
           └── ci.yml        # Workflow de CI automatizado
```

---

## 🔥 Integração Contínua (CI)

[![CI - Python Lint & Test](https://github.com/FuturoDevJunior/penta/actions/workflows/ci.yml/badge.svg)](https://github.com/FuturoDevJunior/penta/actions/workflows/ci.yml)

- **Lint automático:** [Ruff](https://github.com/astral-sh/ruff)
- **Testes automatizados:** [pytest](https://docs.pytest.org/)
- **Compatibilidade:** Python 3.10 a 3.13
- **Status:** Veja a aba [Actions](https://github.com/FuturoDevJunior/penta/actions)

---

## 🧪 Exemplo de Relatório Gerado

```json
{
  "timestamp": "2025-05-25T22:30:00.123456",
  "proxies_working": ["1.2.3.4:8080", ...],
  "urls_dorked": ["http://exemplo.com/vuln?id=1", ...],
  "urls_sqli_vulnerable": ["http://exemplo.com/vuln?id=1", ...]
}
```

---

## 📋 Requisitos

- Python 3.8+
- Google Chrome instalado (para Selenium)
- sqlmap e nmap instalados no PATH

---

## 🧠 Dicas Profissionais

- Edite o `dorks.txt` para personalizar suas buscas e focar em tecnologias específicas.
- Use ambientes virtuais para isolar dependências.
- Consulte a aba **Actions** para garantir que seu PR passou nos testes e lint.
- Contribua! Pull requests e sugestões são bem-vindos.

---

## 👤 Autor & Contato

- Desenvolvido por [DevFerreiraG](https://linkedin.com/in/devferreirag)
- [![GitHub](https://img.shields.io/badge/GitHub-FuturoDevJunior/penta-181717?style=flat-square&logo=github)](https://github.com/FuturoDevJunior/penta)

---

## 📝 Licença

Distribuído sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🏆 Versão & Changelog

- **Versão:** 1.0.0 (commit inicial)
- **Changelog:**
  - Estrutura inicial do projeto
  - Documentação visual e completa
  - Código limpo, modular e escalável
  - CI automatizado (lint + testes)
  - Pronto para produção e colaboração

---

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=24&pause=1000&color=F70000&center=true&vCenter=true&width=900&lines=Automatize+seu+Pentest+com+Estilo!;Contribua%2C+use%2C+e+inove+com+o+PENTA!"/>
</p>
