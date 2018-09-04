from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

browser1 = webdriver.Chrome()
browser2 = webdriver.Chrome()
browser1.get('http://localhost:5000')
browser2.get('http://localhost:5000')
assert browser1.title == 'Login Page'

# Doest the testing go by order: Create function.

# Testing Login
def login_test():
    """Test log in page"""
    browser1.find_element_by_name('email').send_keys('yao@yao.com')
    browser1.find_element_by_name('password').send_keys('654321')
    browser1.find_element_by_id('submit').click()
    browser1.find_element_by_name('email').send_keys('yao@yao.com')
    browser1.find_element_by_name('password').send_keys('123456')
    browser1.find_element_by_id('submit').click()
    assert browser1.title == 'Fuji Chat'

    addmember_test()

def addmember_test():
    """Testing add user page."""
    browser1.get('http://localhost:5000/feedpage')
    browser1.find_element_by_id('addmember').click()
    browser1.find_element_by_name('email').send_keys('emma@emma.com')
    browser1.find_element_by_name('password').send_keys('654321')
    browser1.find_element_by_name('fname').send_keys('Emma')
    browser1.find_element_by_name('lname').send_keys('Bergner')
    select = Select(browser1.find_element_by_name('language')) # dropdowns to select
    select.select_by_visible_text('Swedish') 
    browser1.find_element_by_id('submit').click()
    assert browser1.title == 'Fuji Chat'


    new_user()

def new_user():
    """Log in new user for chat testing."""
    browser2.find_element_by_name('email').send_keys('emma@emma.com')
    browser2.find_element_by_name('password').send_keys('654321')
    browser2.find_element_by_id('submit').click()
    assert browser1.title == 'Fuji Chat'

    chat_testing()

def chat_testing():
    """Chat testing."""
    browser2.find_element_by_id('textarea').send_keys('This is cool!')
    browser2.find_element_by_id('sendbutton').click()
    browser1.get('http://localhost:5000/feedpage')
    browser1.find_element_by_id('textarea').send_keys('I think so too!')
    browser1.find_element_by_id('sendbutton').click()
    assert browser2.find_element((By.CLASS_NAME, 'texttesting :last-child')) == 'This is cool!'

    logout_testing()

def logout_testing():
    """Log out testing."""
    browser1.find_element_by_id('logout').click()
    browser1.find_element_by_id('logout').click()

login_test()



