from selenium import webdriver

browser1 = webdriver.Chrome()
browser2 = webdriver.Chrome()
browser1.get('http://localhost:5000')
browser2.get('http://localhost:5000')
# assert browser1.title == 'Login Page'
# assert browser1.title == 'Login Page'


# Testing Login 
browser1.get('http://localhost:5000')
browser1.find_element_by_name('email').send_keys('yao@yao.com')
browser1.find_element_by_name('password').send_keys('123456')
browser1.find_element_by_id('submit').click()
browser1.find_element_by_id('textarea').send_keys('This is cool!')
browser1.find_element_by_id('sendbutton').click()

# assert browser1.title == "Welcome to Fuji Chat!"

browser2.get('http://localhost:5000')
browser2.find_element_by_name('email').send_keys('mei@mei.com')
browser2.find_element_by_name('password').send_keys('123456')
browser2.find_element_by_id('submit').click()
# browser2.find_element_by_id('textarea').send_keys('Bra bra!')
# browser2.find_element_by_id('sendbutton').click()

