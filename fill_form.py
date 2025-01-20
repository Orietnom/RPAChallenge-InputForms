from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv
from Logger.logger import Logger
import os
import pandas as pd
import re
import time
import shutil

load_dotenv()


class FillForms:

    logger = Logger(__name__).get_logger()
    download_path: str = os.path.join(os.getcwd(), 'resources')

    def __init__(self):
        self._chrome_config()

    def _chrome_config(self, wait_time_out: float = 15.0) -> None:
        '''
        Função para configurar o selenium para funcionar com google chrome
        :param wait_time_out: tempo de espera explícito em segundos, 15.0 padrao
        :return: None
        '''

        if os.path.exists(self.download_path):
            shutil.rmtree(self.download_path)
        os.makedirs(self.download_path)

        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.download_path
        }
        chrome_options.add_experimental_option("prefs", prefs)

        #Instanciando selenium para abrir com google chrome
        self.wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        #configurando wait explicito de 15 segundos
        self.wait = WebDriverWait(self.wd, wait_time_out)
        self.action = ActionChains(self.wd)

    def get_sheet(self) -> pd:
        '''
        Função que acessa a URL do website, realiza o download da planilha e retorna um df do excel, caso o download
        tenha sido sucesso, ou None caso contrário
        :return: df or None
        '''

        index: int = 0

        self.logger.info(f"Acessando o portal {os.getenv('URL')}")
        self.wd.get(os.getenv("URL"))
        self.wd.find_element(By.XPATH, '/html/body/app-root/div[2]/app-rpa1/div/div[1]/div[6]/a').click()

        file_path = os.path.join(self.download_path, 'challenge.xlsx')
        while not os.path.exists(file_path):
            time.sleep(1)
            index += 1
            if index > 30:
                return None

        self.logger.info("Arquivo baixado na pasta \"resources\"")

        file = os.listdir(self.download_path)
        if file:
            df = pd.read_excel(os.path.join(self.download_path, file[0]))
            df.columns = df.columns.str.rstrip()
            self.logger.info(f"Arquivo lido como um data frame")
            return df
        return None

    def fill_form(self, df:pd) -> None:
        '''
        Função que preenche o formulário a partir de um df
        :param df: dataFrame
        :return: None
        '''

        self.logger.info("Início do preenchimento do formulário")
        for index, row in df.iterrows():
            self.logger.info(f"Linha {index+1}")
            inputs = self.wd.find_elements(By.TAG_NAME, 'input')

            for input in inputs:
                field = input.get_attribute("ng-reflect-name")
                if not field:
                    self.logger.info(f"Fim do preenchimento, enviando formulário")
                    input.click()
                    break
                field = field.replace("label", "")
                field = re.sub('([a-z])([A-Z])', r'\1 \2', field)
                if field.lower() == 'role':
                    field = "Role in Company"
                elif field.lower() == 'phone':
                    field = "Phone Number"

                self.logger.info(f"Preechendo o campo {field} com o valor {row[field]}")
                input.send_keys(row[field])

        os.remove(os.path.join(self.download_path, 'challenge.xlsx'))

    def run(self):
        '''
        Função que orquesta o processo, chamando outras funções
        :return: None
        '''
        try:
            self.logger.info("Inicio da automação de preenchimento de formularios")
            df = self.get_sheet()
            if not isinstance(df, pd.DataFrame):
                self.logger.error("Problema ao baixar a planilha de entrada")
            self.fill_form(df=df)
            self.logger.info("Fim da Automação")
        except Exception as error:
            self.logger.error(f'Erro não mapeado. Erro => {str(error)}')