import telegram
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from time import sleep,time
import pytz
from datetime import datetime,timedelta
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, UnexpectedAlertPresentException,TimeoutException,ElementClickInterceptedException,ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import MaxRetryError
from selenium.webdriver.remote.command import Command
from threading import Lock, Thread
import imaplib
import email as email_lib
import socket
import chromedriver_autoinstaller

''' token pode ser pego pelo @BotFather no Telegram // token that can be generated talking with @BotFather on telegram'''
my_token = '123123123:XXXXXXXXXxxxxxxxxxxxxxx'
chat_id = "-123456789"

'''  Quantidade maxima de driver abertos '''
numero_instancia_max = 1

numero_instancia = 0
tentativa_maxima = 3 
tempo_espera = 90
documentos_list=[]
documentos_dados=[]
link_ifood_entrar = "https://www.ifood.com.br/entrar/email"
logins = {}

'''
site baseado:https://medium.com/analytics-vidhya/how-to-login-to-websites-requiring-otp-using-python-6e5339a5c740

links para liberar o acesso imap aos provedores dos emails:
Google: https://mail.google.com/mail/u/0/#settings/fwdandpop e https://myaccount.google.com/lesssecureapps
e case aja verificação em duas etapas :https://myaccount.google.com/apppasswords

yahoo: https://login.yahoo.com/myaccount/security/app-password/
'''

def send(msg, chat_id, token=my_token):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg,parse_mode="markdown",api_kwargs={"comment":True,"reply_to_top_id":4,"reply_to_peer_id":{"user_id":"1956273048","chat_id":"-1001494542764","channel_id":"-1001494542764"},"recent_repliers":{"user_id":"1956273048","chat_id":"-1001494542764","channel_id":"-1001494542764"}})

def acessar_url(driver,url):
    while True:
        try:
            driver.get(url)
            while True:
                carregando = driver.execute_script("return document.readyState")
                if carregando == "complete":
                    break
                else:
                    sleep(1)
            break
        except (TimeoutException,MaxRetryError,UnexpectedAlertPresentException) as exp:
            try:
                driver.execute(Command.STATUS)
            except Exception as erro:
                try:
                    driver.quit()
                except:
                    pass
                return driver,True
            continue
    return driver,False

def codigo_email(email="",senha=""):
    while True:
        try:
            otp = None
            imap = None
            case = email.split('@')[1].split('.')[0]
            if case == "hotmail":
                imap = imaplib.IMAP4_SSL("outlook.office365.com")
            elif case == "outlook":
                imap = imaplib.IMAP4_SSL("outlook.office365.com")
            elif case == "gmail":
                imap = imaplib.IMAP4_SSL("imap.gmail.com")
            elif case == "yahoo":
                imap = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
            else:
                print("Não tem suporte ao provedor "+str(case)+" !")
                return None
            sock=imap.socket()
            sock.settimeout(30)
            imap.login(email, senha)

            continue_cont = 0
            while True:
                break_temp = False
                continue_temp = False
                status, messages = imap.select("Inbox")
                ''' codigo alternativo: status2, messages2 =imap.search( 'UTF-8', '(FROM "naoresponder@login.ifood.com.br" TO "{}" SINCE "{}")'.format(email,(datetime.now(pytz.utc)- timedelta(days=1)).strftime("%d-%b-%Y"))) '''
                status2, messages2 =imap.search( 'US-ASCII', '(FROM "naoresponder@login.ifood.com.br" SINCE "{}")'.format((datetime.now(pytz.utc)- timedelta(days=1)).strftime("%d-%b-%Y")))
                qtd_emails= str(messages2[0]).replace("b","").replace("'","").split(' ')
                if qtd_emails[0] == '':
                    sleep(5)
                    continue_temp = True
                else:
                    if case == "yahoo":
                        res, msg = imap.fetch(str(qtd_emails[len(qtd_emails)-2]), "(RFC822)")
                        '''idk but the last one is empty'''
                    else:
                        res, msg = imap.fetch(str(qtd_emails[len(qtd_emails)-1]), "(RFC822)")
                    for response in msg:
                        if isinstance(response, tuple):
                            msg = email_lib.message_from_bytes(response[1])
                            if msg.is_multipart():
                                for part in msg.walk():
                                    ''' extract content type of email'''
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))
                                    try:
                                        ''' get the email body'''
                                        body = part.get_payload(decode=True).decode()
                                    except:
                                        pass
                                    if content_type == "text/plain" and "attachment" not in content_disposition:
                                        ''' print text/plain emails and skip attachments'''
                                        
                                        ''' depending on your where your OTP is in the email, you will have to modify the string split method'''
                                        dates = msg['Date'].split(' ')
                                        datetime_object = datetime.strptime("{} {} {} {} {}".format(dates[1],dates[2],dates[3],dates[4],dates[5]), '%d %b %Y %H:%M:%S %z')
                                        if( (datetime.now() - timedelta(minutes=1,seconds=30)).astimezone() < datetime_object.astimezone()):
                                            otp = body.split('Seu código de acesso é o seguinte: ')[1]
                                            break_temp = True
                                            break
                                        else:
                                            sleep(5)
                                            continue_temp = True
                                            break
                                if break_temp or continue_temp:
                                    break
                if break_temp:
                    break
                elif continue_temp:
                    continue_cont += 1
                    if continue_cont >= 6:
                        break
                    continue
                            
            imap.close()
            imap.logout()
            break
        except socket.timeout:
            pass
    return otp
    

def verificar_cupons(email="",senha=""):
    banners = []
    cupons = []
    chromedriver_autoinstaller.install(True)
    try:
        options = Options()
        options.add_argument('–profile-directory="Guest Profile"')
        options.add_argument('--disable-extensions')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notification")
        options.add_argument("--width=1024")
        options.add_argument("--height=768")
        options.add_argument("--window-size=1024,768")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")
        '''options.add_argument("--headless")'''
        
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        capabilities = options.to_capabilities()
        capabilities['handlesAlerts'] = False
        capabilities['acceptInsecureCerts'] = True
        PATH_TO_DEV_NULL ='nul'
        driver = webdriver.Chrome( options=options, desired_capabilities=capabilities,service_log_path=PATH_TO_DEV_NULL)
        ''' executable_path="chromedriver.exe" não é mais necessario pois o autoinstaller ja configura o ultimo driver! '''
        acessar_url(driver,link_ifood_entrar)

        cont = 0
        while True:
            try:
                WebDriverWait(driver, 15).until(lambda x: (y:=x.find_element_by_xpath("//input[@name=\"email\"]"), action := ActionChains(driver),action.click(y).perform(),y.send_keys(email)))
                break
            except TimeoutException:
                acessar_url(driver,link_ifood_entrar)
                cont += 1
                if cont >1:
                    driver.quit()
                    return None
                pass
        while True:
            try:
                botao_element = driver.find_element_by_xpath("//div[@class=\"steps-router\"]/div[2]/div/form/button")
                botao_element.click()        
                break
            except NoSuchElementException:
                sleep(1)
        codigo = codigo_email(email,senha)
        if codigo == None:
            driver.quit()
            return None
        otp_split = [str(i) for i in str(codigo)]  
        for i in range(len(otp_split)):
            otp_elem = driver.find_element_by_xpath('//div[@class=\"steps-router\"]/div[4]/div/form/div/input' + str([i + 1]))
            action = ActionChains(driver)
            action.click(otp_elem).perform()

            otp_elem.send_keys(otp_split[i])
        try:
            otp_login_elem = driver.find_element_by_xpath('//div[@class=\"steps-router\"]/div[4]/div/form/button')
            action = ActionChains(driver)
            action.click(otp_login_elem).perform()
        except (NoSuchElementException, StaleElementReferenceException, WebDriverException):
            pass

        try:
            WebDriverWait(driver, 3).until(lambda x: (y:=x.find_element_by_xpath('//div[@class=\"steps-router\"]/div[3]/div/form/button'),EC.element_to_be_clickable((y)) and y.text == 'Continuar'))
            action = ActionChains(driver)
            try:
                otp_login_elem = driver.find_element_by_xpath('//div[@class=\"steps-router\"]/div[3]/div/form/button')
                action.click(otp_login_elem).perform()
            except NoSuchElementException:
                 pass
        except TimeoutException:
            pass


        cont_endereco = 0
        endereco_redirecionado = False
        while True:
            try:
                endereco_element = driver.find_element_by_xpath("//div[@class=\"address-list\"]")
                endereco_branco =0
                while True:
                    try:
                        enderecos = endereco_element.find_elements_by_xpath(".//div[@class=\"btn-address btn-address--default btn-address__container\"]")
                    except NoSuchElementException:
                        driver.quit()
                        return None
                    if len(enderecos)>0:
                        break
                    elif endereco_branco > 5:
                        print("Nenhum endereço cadastrado, ignorar documento")
                        driver.quit()
                        return [[email,senha],["Nenhum Endereço Definido!"],["Nenhum Endereço Definido!"]]
                    else:
                        sleep(1)
                        endereco_branco += 1
                
                action = ActionChains(driver)
                action.click(enderecos[0]).perform()       
                break
            except NoSuchElementException:
                try:
                    action = ActionChains(driver)
                    action.click(driver.find_element_by_xpath('//div[@class=\"steps-router\"]/div[3]/div/form/button')).perform()
                except NoSuchElementException:
                    sleep(1)
                    cont_endereco += 1
                    if cont_endereco >= 10 and endereco_redirecionado == False:
                        acessar_url(driver,"https://www.ifood.com.br/restaurantes")
                        endereco_redirecionado = True
                        cont_endereco = 0
                    elif cont_endereco >= 10 and endereco_redirecionado == True:
                        driver.quit()
                        return None
        cont_banner = 0
        while True:
            try:
                carroseu_banner_element = driver.find_element_by_xpath("//section[@data-card-name=\"BIG_BANNER_CAROUSEL\"] | //div[@class=\"highlights-carousel\"]")
                versao = 0
                try:
                    carroseu_banner_element = driver.find_element_by_xpath("//section[@data-card-name=\"BIG_BANNER_CAROUSEL\"]")
                    versao = 1
                except NoSuchElementException:
                    carroseu_banner_element = driver.find_element_by_xpath("//div[@class=\"highlights-carousel\"]")
                    versao = 2
                if versao == 1:
                    banners_element = carroseu_banner_element.find_elements_by_xpath(".//ul/div/div[1]/div/div[@class=\"carousel__slide\"]")
                    for banner in banners_element:
                        texto_banner = banner.find_element_by_xpath(".//li/a/img").get_attribute("alt")
                        if texto_banner not in banners:
                            banners.append(texto_banner) 
                elif versao == 2:
                    banners_element = carroseu_banner_element.find_elements_by_xpath(".//div/div/div[1]/div/div[@class=\"carousel__slide\"]")
                    for banner in banners_element:
                        texto_banner = banner.find_element_by_xpath(".//div/a/figure/img").get_attribute("alt")
                        if texto_banner not in banners:
                            banners.append(texto_banner) 
                else:
                    print("Algo de errado aconteceu com os banners") 
                break
            except NoSuchElementException as ex:
                sleep(1)
                cont_banner += 1
                if cont_banner >= 10:
                    break
        acessar_url(driver,"https://www.ifood.com.br/cupons")
        while True:
            try:
                try:
                    cards_cupons_element = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//div[@class=\"voucher-wallet-container__card\"]"))
                except TimeoutException:
                    driver.quit()
                    return [[email,senha],banners,[["Nenhum Cupom Definido!","Erro!"]]]
                '''verificar se tem poupup aberto'''
                try:
                    poupup = driver.find_element_by_xpath("//div[starts-with(@class,'marmita-modal__overlay')]")
                    action = ActionChains(driver)
                    action.click(poupup.find_element_by_xpath(".//div/div/div/div[1]/button")).perform()
                except NoSuchElementException:
                    pass
                ver_main_cont = 0
                while True:
                    try:
                        ver_mais_element = driver.find_element_by_xpath("//button[@class=\"btn btn--link btn--size-m voucher-wallet-load-more__btn\"]")
                        ver_main_cont += 1
                        if ver_mais_element.text =="Ver mais" and ver_main_cont <= 2:
                            ver_mais_element.click()
                        elif ver_mais_element.text =="Ver mais" and ver_main_cont > 2:
                            try:
                                ActionChains(driver).move_to_element(ver_mais_element).perform()
                                xy = ver_mais_element.location_once_scrolled_into_view
                                driver.execute_script("window.scrollTo({}, {});".format(xy['x'],xy['y']+20))
                                driver.execute_script("arguments[0].scrollIntoView(true);", ver_mais_element)
                                driver.execute_script("window.scrollBy(0, -60);")
                                action = ActionChains(driver)
                                action.move_to_element(ver_mais_element).click().perform()
                            except:
                                pass
                        ver_mais_element_temp = driver.find_element_by_xpath("//button[@class=\"btn btn--link btn--size-m voucher-wallet-load-more__btn\"]")
                        if (ver_mais_element_temp.text != "Ver mais" and ver_mais_element_temp.text != ''):
                            cards_cupons_element = driver.find_element_by_xpath("//div[@class=\"voucher-wallet-container__card\"]")
                            break
                    except NoSuchElementException:
                        break
                    except (ElementNotInteractableException,ElementClickInterceptedException):
                        pass
                cupons_element = []
                try:
                     cupons_element = cards_cupons_element.find_elements_by_xpath(".//div[@class=\"voucher-card\"]")
                except NoSuchElementException:
                    pass
                finally:
                    if cupons_element == []:
                        cupons_element = cards_cupons_element.find_elements_by_xpath(".//div[3]/div")
                if cupons_element != []:
                     xy = cupons_element[0].location_once_scrolled_into_view
                     driver.execute_script("arguments[0].scrollIntoView(true);", cupons_element[0])
                     ActionChains(driver).move_to_element(cupons_element[0]).perform()
                     driver.execute_script("window.scrollTo({}, {});".format(xy['x'],xy['y']+20))
                for cupon in cupons_element:
                    ver_regras = cupon.find_element_by_xpath(".//div[@class=\"voucher-card__infos\"]/button")
                    try:
                        WebDriverWait(driver, 3).until(lambda x: (y:=cupon.find_element_by_xpath(".//div[@class=\"voucher-card__infos\"]/button"),EC.element_to_be_clickable((y))))
                    except TimeoutException:
                        pass
                    count_click = 0
                    try:
                        ver_regras.click()
                    except ElementClickInterceptedException:
                        try:
                            poupup = driver.find_element_by_xpath("//div[starts-with(@class,'marmita-modal__overlay')]")
                            action = ActionChains(driver)
                            action.click(poupup.find_element_by_xpath(".//div/div/div/div[1]/button")).perform()
                        except NoSuchElementException:
                            pass
                        finally:
                            while True:
                                try:                                    
                                    xy = ver_regras.location_once_scrolled_into_view
                                    driver.execute_script("window.scrollTo({}, {});".format(xy['x'],xy['y']+20))
                                    
                                    if count_click >= 5:
                                        break
                                    elif count_click <= 1:
                                        ver_regras.click()
                                    elif count_click <= 3:
                                        action = ActionChains(driver)
                                        action.click(ver_regras).perform()
                                    else:
                                        driver.execute_script("arguments[0].click();", ver_regras)
                                    try:
                                        WebDriverWait(driver, 1).until(lambda x: x.find_element_by_xpath("//div[@class=\"marmita-modal__inner-content-scroll\"]"))
                                    except TimeoutException:
                                        pass
                                    break
                                except ElementClickInterceptedException:
                                    sleep(1)
                                    ver_regras = cupon.find_element_by_xpath(".//div[@class=\"voucher-card__infos\"]/button")
                                    count_click += 1
                                    pass
                    except ElementNotInteractableException:
                        sleep(1)
                        ver_regras = cupon.find_element_by_xpath(".//div[@class=\"voucher-card__infos\"]/button")
                        action = ActionChains(driver)
                        action.click(ver_regras).perform()
                        count_click = 0
                        while True:
                            try:
                                WebDriverWait(driver, 1).until(lambda x: x.find_element_by_xpath("//div[@class=\"marmita-modal__inner-content-scroll\"]"))
                                break
                            except TimeoutException:
                                count_click += 1
                                xy = ver_regras.location_once_scrolled_into_view
                                driver.execute_script("window.scrollTo({}, {});".format(xy['x'],xy['y']+20))
                                try:
                                    if count_click >= 5:
                                        break
                                    elif count_click <= 1:
                                        ver_regras.click()
                                    elif count_click <= 3:
                                        action = ActionChains(driver)
                                        action.click(ver_regras).perform()
                                    else:
                                        driver.execute_script("arguments[0].click();", ver_regras)
                                except ElementClickInterceptedException:
                                    pass
                    if count_click >= 5:
                        cupons.append(["Erro ao pegar cupom",str(cupon.text)])
                        continue
                    ver_regras_info = 0
                    while True:
                        try:
                            ver_regras_info_element = driver.find_element_by_xpath("//div[@class=\"marmita-modal__inner-content-scroll\"]")
                            break
                        except NoSuchElementException:
                            sleep(1)
                            ver_regras_info += 1
                            if ver_regras_info >=5:
                                break
                    if ver_regras_info >= 5:
                        cupons.append(["Erro ao pegar regra de cupom",str(cupon.text)])
                        continue
                    nome_cupom = "{}: {}".format(ver_regras_info_element.find_element_by_xpath(".//div[2]/h4").text,ver_regras_info_element.find_element_by_xpath(".//div[2]/span[2]").text)
                    regra_cupom = ver_regras_info_element.find_element_by_xpath(".//div[2]/ul/li").text                    
                    cupons.append([nome_cupom,regra_cupom])
                    fechar = None
                    try:
                        fechar = ver_regras_info_element.find_element_by_xpath(".//div[1]/button")
                        fechar.click()
                    except Exception:
                        if fechar != None:
                            try:
                                action = ActionChains(driver)
                                action.move_to_element(fechar).click().perform()
                            except:
                                pass
                            finally:
                                driver.execute_script("arguments[0].click();", fechar)
                        pass
                break
            except NoSuchElementException:
                sleep(1)
        driver.quit()
    except Exception as erro:
        driver.quit()
        print(erro)
        return None
    return [[email,senha],banners,cupons]

def filtro_de_cupom(cupom=""):
    validacao = True

    if cupom == "R$ 10 pra restaurantes selecionados: Válido para pedidos acima de R$ 25.":
        validacao = False

    if cupom == "R$ 5 pra restaurantes selecionados: Válido para pedidos acima de R$ 15.":
        validacao = False

    if cupom == "R$ 30 para Mercado: Válido para o primeiro pedido em Mercado acima de R$80.":
        validacao = False

    if cupom == "R$ 30 pra conhecer mercados: Válido para pedidos acima de R$ 200,00":
        validacao = False

    if cupom == "R$ 25 pra farmácias: Válido para pedidos acima de R$ 70. Somente no primeiro pedido.":
        validacao = False

    #if cupom == "R$ 12 pra conhecer restaurantes: Pra pedidos acima de R$25 nesses restaurantes onde você nunca pediu.":
        #validacao = False

    if cupom == "R$ 20 para Bebidas: Válido para pedidos acima de R$ 45.":
        validacao = False
    
    if cupom == "R$ 20 para Pet: Válido para pedidos acima de R$ 70.":
        validacao = False

    if cupom == "R$ 10 para mercado: Pra pedidos acima de R$100 para os mercados selecionados.":
        validacao = False

    return validacao

def gerenciar_emails(key,emailS):
    try:
        dados = verificar_cupons(emailS[0],emailS[1])
    except Exception as erro:
        print(erro)
        dados = None
    with Lock():
        global documentos_list
        if dados != None:
            documentos_list[key][0] = ""
            global documentos_dados
            documentos_dados.append(dados)
            texto= "-*Conta*-: {}\n".format(dados[0][0])
            texto +="-*Banners*-: "
            for banner in dados[1]:
                texto += "{}, ".format(str(banner))
            texto += "\n"
            texto += "-*CUPONS*-:\n\n"
            for cupon in dados[2]:
                '''Filtro de cupons basicos'''
                if filtro_de_cupom(cupon[0]):
                    texto += "-*{}*- ({})\n\n".format(str(cupon[0]),str(cupon[1]))
            send(texto,chat_id,my_token)
        elif  dados == None:            
            documentos_list[key][2]+= 1
            send("Erro no: {}\nTentativa {}/{}...".format(str(emailS[0]),str(documentos_list[key][2]),str(tentativa_maxima)),chat_id,my_token)
            if documentos_list[key][2] == tentativa_maxima:
                documentos_dados.append([emailS,None,None])
        global numero_instancia
        numero_instancia-= 1

def main():
    if os.path.isfile("login.txt"):
        login = open("login.txt", "rb")
        linhas = login.readlines()
        login.close()
        for emails in range(int("{0:.0f}".format((len(linhas)/2)))):
            username = ""
            password = ""
            if 0 <= ((emails*2)+1) < len(linhas):
                username = linhas[emails*2].decode('utf-8').replace('\r', '').replace('\n', '')
                password = linhas[(emails*2)+1].decode('utf-8').replace('\r', '').replace('\n', '')
                logins.update({username: password})

        global numero_instancia_max 
        global documentos_list
        for email,senha in logins.items():
            documentos_list.append([[email,senha],0,0])

        while (True in [True if y[0]!="" and y[2]<tentativa_maxima else False for y in documentos_list]):
            for i,documento in sorted(enumerate(documentos_list),key=lambda x: x[1][1]):
                with Lock():
                    global numero_instancia            
                    if (numero_instancia < numero_instancia_max):
                        if ((documento[1] == 0 or time() -documento[1]>=tempo_espera) and documento[0]!="" and documento[2]<tentativa_maxima):
                            documentos_list[i][1] = time()
                            numero_instancia+= 1
                            Thread(target=gerenciar_emails,name="emails"+str(documento)+' key:'+str(i), args=(i,documento[0])).start()
                    else:
                        sleep(5)
                        break
            '''if todos tem tempo em recarga mas ainda nao deu os 3 erros esperar 5 seg'''
            if not(True in [True if y[0]!="" and y[2]<tentativa_maxima else False for y in documentos_list]):
                break

            if not(False in [True if y[1] != 0 and time() -y[1]>=tempo_espera and numero_instancia < numero_instancia_max else False for y in documentos_list]):
                sleep(5)
            elif numero_instancia >= numero_instancia_max:
                sleep(1)

        send("Terminado!!!!!",chat_id,my_token)

'''Main do código'''
if __name__ == "__main__":
    main()
