#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# https://orteil.dashnet.org/cookieclicker/


# ID = "id"
# XPATH = "xpath"
# LINK_TEXT = "link text"
# PARTIAL_LINK_TEXT = "partial link text"
# NAME = "name"
# TAG_NAME = "tag name"
# CLASS_NAME = "class name"
# CSS_SELECTOR = "css selector"

import re
import time
from datetime import datetime
from datetime import timedelta
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

import threading
from pynput.keyboard import Listener, KeyCode


class ClickMouse(threading.Thread):
  def __init__(self):
    super(ClickMouse, self).__init__()

    self.listZerro = {"million":3, "billion": 6, "trillion": 9,"quadrillion": 12, "quintillion": 15, "sextillion": 18, "septillion": 21, "octillion": 24}
    self.program_running = True
    self.running = False
    self.loadGame = False

    self.indexButtons = 1 # point
    self.spells = 1 # point
    self.buffs = 1
    self.indexGoldenCookie = 1 # point

    self.buffsID = list()# список всех бафов
    self.cookieStorm = '-1056px -288px'
    self.moreClicked = '0px -672px'
    self.clearAllClick = True # клик по сторонним объектам
    self.harvesting = ["-192px 0px", "-192px -48px", "-192px -96px", "-192px -144px", "-192px -192px", "-192px -240px", "-192px -288px", "-192px -336px", "-192px -384px", "-192px -432px", "-192px -480px", "-192px -528px", "-192px -576px", "-192px -624px", "-192px -672px", "-192px -720px"]
    self.saveGame = 0 # datetime
    self.pieceSugarChack = datetime.now() + timedelta(minutes=3)

    caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "normal"  # complete
    caps["pageLoadStrategy"] = "eager"  #  interactive

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    # options.add_argument("--headless") #скрыть браузер
    options.add_argument("--mute-audio")  # выключить звук
    options.add_argument('disable-infobars')
    options.add_argument("–silent")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
  
    self.driver = webdriver.Chrome(desired_capabilities=caps, service=Service("/usr/bin/chromedriver"), options=options)
    self.driver.get("http://orteil.dashnet.org/cookieclicker/beta/")
    time.sleep(0.3)
    with open('/var/www/cookies/CookieClickerGame.txt', 'r') as file:
      data = file.read()
      if len(data) > 0:
        self.driver.execute_script("window.localStorage.setItem('CookieClickerGameBeta', '%s');" % data)

  def start_clicking(self):
    self.running = True

  def stop_clicking(self):
    self.running = False
    self.save_game()

  def exit(self):
    self.stop_clicking()
    time.sleep(1)
    self.program_running = False
    # self.driver.quit()
    self.driver.close()
    print(self.buffsID)

  def get_screen(self, attr):
    sub = datetime.now().strftime("%d-%A  %H:%M:%S") + "-"+attr
    self.driver.save_screenshot(f'/var/www/cookies/screen-{sub}.png')

  def save_game(self):
    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("s").key_up(Keys.CONTROL).perform()
    try:
      CookieClickerGame = str(self.driver.execute_script("return localStorage.getItem('CookieClickerGameBeta')").encode('utf-8'), 'utf-8')
      with open("/var/www/cookies/CookieClickerGame.txt", "w+") as output:
        output.write(CookieClickerGame)
    except:
      pass
    # print("save Game", datetime.now())

  def clickBigCookie(self):# основная большая печенька
    try:
      bigCookie = self.driver.find_element(By.ID, "bigCookie")
      if bigCookie:
        bigCookie.click()

      canvas = self.driver.find_element(By.ID, "bigCookie")
      if canvas:
        location = canvas.location
        size = canvas.size
        x, y = location['x'] + size['width'], location['y'] + size['height']
        # ActionChains(self.driver).reset_actions()
        # ActionChains(self.driver).move_by_offset(x, y).click().perform()

        # js = f"""
        #     console.log('x',{x}, 'y',{y})
        # """
            
            # self.driver.execute_script(js)                    
    except ElementClickInterceptedException:
      pass


  def golden_coocker(self):# золотые печеньки
    try:
      goldenCookie = self.driver.find_elements(By.CLASS_NAME, "shimmer")
      if len(goldenCookie) > 2:
        self.indexGoldenCookie = 19

      for cookie in goldenCookie:
        # cookie.click()
        if cookie.is_displayed(): # and cookie.get_attribute("alt") == "Золотое печенье"
          self.driver.execute_script("arguments[0].click();", cookie)
    except (StaleElementReferenceException, NoSuchElementException, Exception) as e:
      pass
    
    
      # self.get_screen('game')

  def upgrades(self):# Иследование
    techsUpgrades = self.driver.find_element(By.ID, "techUpgrades").find_elements(By.CSS_SELECTOR, ".crate.upgrade.enabled")
    if techsUpgrades:
      for research in techsUpgrades:
         if research:
          self.driver.execute_script("arguments[0].click();", research)
    else:
      return

  def updates(self):# Улучшение
    upgrades = self.driver.find_element(By.ID, "upgrades").find_elements(By.CSS_SELECTOR, ".crate.upgrade.enabled")
    if len(upgrades)>0:
      for upgrade in upgrades:
        try:
          if upgrade:
            self.driver.execute_script("arguments[0].click();", upgrade)
            break
        except NoSuchElementException:
          pass
    else:
      return

  def buildings(self):# Строения
    buttons = self.driver.find_elements(By.CLASS_NAME, "product")
    productPrice = dict()
    if len(buttons) > 0:
      for button in buttons:
        if button.get_attribute("class") == "product unlocked enabled":
          priceProduct = button.find_element(By.CLASS_NAME, "price").text.replace(',', '').replace('.', '').replace(' ', '') #.replace(r"\s\D+", '')
          numberPriceProduct = re.sub(r"\D+", '', priceProduct)
          strPriceProduct = re.sub(r"\d+", '', priceProduct)

          if strPriceProduct:
            line = "%s%s" % (numberPriceProduct, ("0" * self.listZerro[strPriceProduct]))
          elif numberPriceProduct:
            line = priceProduct
          else:
            return
          
          productPrice[int(line)] = button
      
      if productPrice and productPrice.keys():
        self.indexButtons = 99
        self.driver.execute_script("arguments[0].click();", productPrice[min(productPrice.keys())])
    else:
      return

  def grimoire(self, click=False):# Гримуар
    try:
      grimoireBarText = self.driver.find_element(By.ID, "grimoireBarText").text
      BarText = ''.join(grimoireBarText.split(' ')[:-1])
      BarText = BarText if BarText != '' else grimoireBarText
      grimoireText = BarText.split('/')

      if grimoireText[0] and grimoireText[1] and grimoireText[0] == grimoireText[1]:
        # grimoireSpell0Price = self.driver.find_element(By.ID, "grimoireSpell0").find_element(By.CLASS_NAME, "grimoirePrice").text # наколдовать выпечку
        grimoireSpell1Price = self.driver.find_element(By.ID, "grimoireSpell1").find_element(By.CLASS_NAME, "grimoirePrice").text # тянуть руку судбьы
        grimoireSpell2Price = self.driver.find_element(By.ID, "grimoireSpell2").find_element(By.CLASS_NAME, "grimoirePrice").text # замедление времени
             
        grimoireSpell = self.driver.find_elements(By.CLASS_NAME, "grimoireSpell")  
        
        for spell in grimoireSpell:
          if spell.get_attribute("class") == "grimoireSpell titleFont ready":
            if BarText:
              if int(grimoireText[0]) >= int(grimoireSpell2Price) and spell.get_attribute("id") == "grimoireSpell0" and click:# замедление времени
                self.driver.execute_script("arguments[0].click();", spell)

              if int(grimoireText[0]) >= int(grimoireSpell1Price) and spell.get_attribute("id") == "grimoireSpell1":# тянуть руку судбьы
                self.driver.execute_script("arguments[0].click();", spell)
              
      else:
        return
    except NoSuchElementException:
      pass

  def garden(self):# Огород
    try:
      gardenTile = self.driver.find_elements(By.CLASS_NAME, "gardenTile")
      gardenIcon = self.driver.find_elements(By.CLASS_NAME, "gardenTileIcon")
      grid = list()
      if len(gardenIcon) <= 0 and len(gardenTile) <= 0:
        return
      for idx, garden in enumerate(gardenTile):# получаем количество клумб
        if garden.is_displayed():
          grid.append(garden)

      if len(gardenIcon) > 0:
        for icon in gardenIcon: # собирем урожай
          if icon.is_displayed():
            if icon.value_of_css_property('background-position') in self.harvesting:
              gardenParent = icon.find_element(By.XPATH, "..")
              self.driver.execute_script("arguments[0].click();", gardenParent)# click garden

      if len(grid) > 0:
        gardenSeeds = self.driver.find_elements(By.CSS_SELECTOR, "#gardenSeeds > .gardenSeed:not(.locked)")
        random_index = random.randrange(len(gardenSeeds))

        for idx, garden in enumerate(grid):# сожаем семена
          # print(garden.is_displayed(), idx, len(grid), garden.get_attribute("id") )

          if (garden.is_displayed() and len(grid) == 4) and (idx == 0 or idx == 2): # маленькая грядка 2x2
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():              
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 6) and (idx == 1 or idx == 4): # маленькая грядка 3x2
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 9) and (idx == 3 or idx == 4 or idx == 5): # маленькая грядка 3x3
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 12) and (idx == 3 or idx == 4 or idx == 5 or idx == 6): # грядка 4x3
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 16) and (idx == 0 or idx == 3 or idx == 6 or idx == 9 or idx == 12  or idx == 15): # грядка 4x4
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 20) and (idx == 0 or idx == 4 or idx == 6 or idx == 8 or idx == 15  or idx == 17 or idx == 19): # грядка 5x4
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 25) and (idx == 1 or idx == 4 or idx == 6 or idx == 9 or idx == 16  or idx == 19 or idx == 21  or idx == 24): # большая грядка 5x5
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 30) and (idx == 1 or idx == 4 or idx == 7 or idx == 10 or idx == 19  or idx == 22 or idx == 25  or idx == 28): # большая грядка 6x5
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

          if (garden.is_displayed() and len(grid) == 36) and (idx == 1 or idx == 4 or idx == 7 or idx == 10 or idx == 13 or idx == 16 or idx == 25 or idx == 28 or idx == 31 or idx == 34): # большая грядка 6x6
            if not garden.find_element(By.CLASS_NAME, "gardenTileIcon").is_displayed():
              self.driver.execute_script("arguments[0].click();", gardenSeeds[random_index])# click seed
              self.driver.execute_script("arguments[0].click();", garden)# click garden

    except NoSuchElementException:
      pass

  def pieceSugar(self):
    try:
      lumpsAmount = self.driver.find_element(By.ID, "lumpsAmount").text
      if lumpsAmount and int(lumpsAmount) > 0:
        levels = list()
        productLevels = self.driver.find_elements(By.CSS_SELECTOR, "#rows .enabled .productButton.productLevel.lumpsOnly")
        if productLevels:
          for productLevel in productLevels:
            key = int(productLevel.get_attribute('innerText').replace('lvl ', ''))
            _dict = dict()
            _dict["key"] = key
            _dict["el"] = productLevel
            levels.append(_dict)
          if len(levels) > 0:
            self.driver.execute_script("arguments[0].click();", min(levels, key=lambda x:x['key'])["el"])
            self.pieceSugarChack = datetime.now() + timedelta(seconds=60)

    except NoSuchElementException:
      pass
    
    

  def run(self):
    while self.program_running:
      self.saveGame = datetime.now() + timedelta(seconds=60)

      if not self.loadGame:
        try:
          cc_btn_accept_all = self.driver.find_element(By.CLASS_NAME, "cc_btn_accept_all")
          langSelectRU = self.driver.find_element(By.ID, "langSelect-RU")
          if langSelectRU and cc_btn_accept_all:
            self.driver.execute_script("arguments[0].click();", cc_btn_accept_all)
            self.driver.execute_script("arguments[0].click();", langSelectRU)
            time.sleep(3)
            self.loadGame = True
            self.running = True
            self.save_game()
            time.sleep(1)
            print("loaded. Run click?")
        except (ElementClickInterceptedException, NoSuchElementException) as e:
          pass

      if datetime.now() > self.saveGame:
        self.saveGame = datetime.now() + timedelta(seconds=60)
        self.save_game()

      while self.running:
        # time.sleep(0.01)

        # раздаем кусочки сахара строениям
        if datetime.now() > self.pieceSugarChack:
          self.pieceSugarChack = datetime.now() + timedelta(hours=12)
          self.pieceSugar()



        # clickBigCookie
        self.clickBigCookie()

        # бафы
        if self.buffs % 10 == 0:
          self.buffs = 0
          childrenСreateBox = self.driver.find_element(By.CLASS_NAME, "crateBox").find_elements(By.CSS_SELECTOR, "*")
          if len(childrenСreateBox) > 0:
            try:
              for buff in childrenСreateBox:
                position = buff.find_element(By.XPATH, "..")
                if position:
                  pos = position.value_of_css_property('background-position')
                  if pos not in self.buffsID:# test buffs
                    self.buffsID.append(pos)

                  if pos == self.cookieStorm or pos == self.moreClicked:
                    if pos == self.cookieStorm:
                      self.golden_coocker()
                    if pos == self.moreClicked:
                      self.grimoire(True) # включение замедление времение времени гримуар
                      self.grimoire(True) # включение замедление времение времени гримуар
                    self.clearAllClick = False
                  else:
                    self.clearAllClick = True
            except (StaleElementReferenceException, NoSuchElementException, WebDriverException) as e:
              pass
          else:
            self.clearAllClick = True

        

        # Золотое печенье
        if self.indexGoldenCookie % 20 == 0:
          self.indexGoldenCookie = 0
          self.golden_coocker()


        # Клик по строениям
        if self.indexButtons % 100 == 0 and self.clearAllClick:
          self.indexButtons = 0
          # close info
          try:
            close = self.driver.find_element(By.CSS_SELECTOR, ".framed.close.sidenote")
            if close:
              self.driver.execute_script("arguments[0].click();", close)
          except NoSuchElementException:
            pass
          # Иследования улучшения
          self.updates()
          self.upgrades()
          # select build
          self.buildings()
        

        # spells
        if self.spells % 150 == 0 and self.clearAllClick:
          self.spells = 0
          # grimoireSpell
          self.grimoire()
          # gardenSeeds
          self.garden()


        self.indexGoldenCookie += 1
        self.indexButtons += 1
        self.spells += 1
        self.buffs += 1      


click_thread = ClickMouse()
click_thread.start()



pause_key = KeyCode(char='`')
stop_key = KeyCode(char='Q')
save_screen = KeyCode(char='~')


def on_press(key):
  if key == save_screen:
    click_thread.get_screen('touch')

  elif key == pause_key:
    if click_thread.running:
      click_thread.stop_clicking()
    else:
      click_thread.start_clicking()

  elif key == stop_key:
    click_thread.exit()
    listener.stop()


if __name__ == "__main__":
  print(f"run click or stop, press key {pause_key}")
  print(f"close app, press key {stop_key}")
  print(f"save screen brauser window, press key {save_screen}")
  with Listener(on_press=on_press) as listener:
    listener.join()
 
