from selenium import webdriver


def screenshot(url, path):
    """renders html and takes a screenshot"""
    # open in webpage
    driver = webdriver.PhantomJS()
    driver.set_window_size(1080, 800)
    driver.get(url)
    driver.save_screenshot(path)
    driver.quit()
