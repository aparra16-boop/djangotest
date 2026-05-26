from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

import random
import string
 
class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    #fixtures = ['testdb.json',]
 
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()
 
    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        #cls.selenium.quit()
        super().tearDownClass()
 
    def old_test_login(self):
        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
 
        # comprovem que el títol de la pàgina és el que esperem
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )
 
        # introduïm dades de login i cliquem el botó "Log in" per entrar
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()
 
        # testejem que hem entrat a l'admin panel comprovant el títol de la pàgina
        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )

    def test_17_creacio_massiva_choices_inline(self):
        # 1. Ens loguegem primer (cada test neteja la sessió del navegador)
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.selenium.find_element(By.NAME, "username").send_keys('isard')
        self.selenium.find_element(By.NAME, "password").send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Funció ràpida per generar text aleatori
        def text_aleatori(longitud=10):
            return ''.join(random.choices(string.ascii_letters, k=longitud))

        # =====================================================================
        # PREGUNTA 1: 1 Pregunta amb 1 Choice
        # =====================================================================
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/question/add/'))
        
        # Omplim el text de la pregunta
        q1_text = f"Pregunta_Simple_{text_aleatori()}"
        self.selenium.find_element(By.ID, "id_question_text").send_keys(q1_text)

        # Obrim el desplegable per la data i hora
        self.selenium.find_element(By.ID, "fieldset-0-1-heading").click()
        
        # Omplim la data pulsant TODAY
        self.selenium.find_element(By.LINK_TEXT, "Today").click()

        # Omplim l'hora pulsant NOW
        self.selenium.find_element(By.LINK_TEXT, "Now").click()

        # Omplim la primera inline choice (índex 0)
        self.selenium.find_element(By.NAME, "choice_set-0-choice_text").send_keys(f"Opacio_Unica_{text_aleatori(5)}")
        
        # Cliquem el botó de Desar (_save)
        self.selenium.find_element(By.NAME, "_save").click()

        # =====================================================================
        # PREGUNTA 2: 1 Pregunta amb 100 Choices (Bucle)
        # =====================================================================
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/question/add/'))
        
        q2_text = f"Pregunta_Massiva_{text_aleatori()}"
        self.selenium.find_element(By.ID, "id_question_text").send_keys(q2_text)

        # Obrim el desplegable per la data i hora
        self.selenium.find_element(By.ID, "fieldset-0-1-heading").click()
        
        # Omplim la data pulsant TODAY
        self.selenium.find_element(By.LINK_TEXT, "Today").click()

        # Omplim l'hora pulsant NOW
        self.selenium.find_element(By.LINK_TEXT, "Now").click()

        
        # Bucle per crear les 100 choices
        for i in range(100):
            # Per defecte, Django Admin sol mostrar 3 formularis inline buits (índexs 0, 1 i 2).
            # A partir del tercer (índex 3), hem de clicar dinàmicament el botó "Add another Choice"
            if i >= 3:
                botó_afegir = self.selenium.find_element(By.CSS_SELECTOR, ".add-row a")
                botó_afegir.click()
            
            # Generem el text aleatori de la opció i la introduïm al seu input corresponent
            c_text = f"Opció_{i}_{text_aleatori(5)}"
            input_choice = self.selenium.find_element(By.NAME, f"choice_set-{i}-choice_text")
            input_choice.send_keys(c_text)
            
        # Desem la segona pregunta amb les seves 100 opcions
        self.selenium.find_element(By.NAME, "_save").click()

        # =====================================================================
        # VERIFICACIÓ: Comprovar que hi ha 101 Choices al menú
        # =====================================================================
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/choice/'))
        
        # Per defecte Django Admin només mostra 100 files per pàgina.
        # Si comptéssim les files de la taula, en sortirien 100 i el test fallaria (en falta 1).
        # Per solucionar-ho, llegim el text del comptador oficial de Django (class="paginator")
        paginator_element = self.selenium.find_element(By.CSS_SELECTOR, "p.paginator")
        text_comptador = paginator_element.text  # Sol dir quelcom com "101 results" o "101 de un total de 101"
        print(f"--- TEXT DETECTAT AL PAGINADOR: '{text_comptador}' ---")
        # Validem que el número 101 apareix en el text del comptador
        self.assertIn("101", text_comptador)