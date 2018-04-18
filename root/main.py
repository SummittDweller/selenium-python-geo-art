from webdriver_util import init
import glob
import codecs
import csv

import private


def edit_cache_page_coorinates(driver, posted, final):
  print("Cache edit page is open.  Looking for inputs with id = ctl00_ContentBody_tbPostedCoordinates, class = js-wpt-coords, and id = ctl00_ContentBody_btnSaveAndPreview...")

  c = driver.find_element_by_id('ctl00_ContentBody_tbPostedCoordinates')
  if c:
    c.clear()
    c.send_keys(posted)
  else:
    print("Found NO posted coordinates field.")
    return False

  print("Posted coordinates set to: {}".format(posted))
  driver.refresh()

  f = driver.find_element_by_xpath('//input[@class="js-wpt-coords"]')
  if f:
    f.clear()
    f.send_keys(final)
  else:
    print("Found NO final coordinates field.")
    return False

  print("Final coordinates set to: {}".format(final))
  driver.refresh()

  s = driver.find_element_by_id("ctl00_ContentBody_btnSaveAndPreview")
  if s:
    s.click()
  else:
    print("Found NO 'Save and Preview' button.")
    return False

  return driver



def process_login(driver):
  print("Login page is open.  Looking for inputs with id = Username, Password and Login...")

  u = driver.find_element_by_id('Username')
  if u:
    u.send_keys(private.username)
  else:
    print("Found NO username field.")
    return False

  p = driver.find_element_by_id('Password')
  if p:
    p.send_keys(private.password)
  else:
    print("Found NO password field.")
    return False

  s = driver.find_element_by_id("Login")
  if s:
    s.click()
  else:
    print("Found NO submit button.")
    return False

  return driver



def open_cache_page(url, posted, final):
  clean = url.strip()

  print("Loading Firefox driver...")
  driver, waiter, selector, datapath = init()

  print("Fetching the cache page at {}".format(clean))
  driver.get(clean)

  print("Taking a screenshot...")
  waiter.shoot("First page")

  print("Checking for a Log In button...")
  login_button = driver.find_element_by_xpath(u'//a[text()="Log In"]')
  if login_button:
    print("...found it.  Clicking.")
    login_button.click()

  print("Taking a screenshot...")
  waiter.shoot("Login page")

  login_url = driver.current_url
  print("Login page URL is: {}".format(login_url))

  success = process_login(driver)
  if success:
    print("...success")
    page_url = driver.current_url
    print("New page URL is: {}".format(page_url))
    driver = success

  print("Taking a screenshot...")
  waiter.shoot("Cache page")

  driver.refresh()

  # Look for "Your geocache has not yet been submitted".  If found, look for a link with id = ctl00_ContentBody_uxEditGeocacheLink

  print("Looking for 'Your geocache has not yet been submitted' and a link with id=ctl00_ContentBody_uxEditGeocacheLink...")
  content = driver.find_element_by_css_selector('h5.alert-header')
  if content:
    t1 = "Your geocache has not yet been submitted"
    t2 = "You have a new note from the reviewer"
    if t1 in content.text:   # Look for a button with an id = ctl00_ContentBody_uxEditGeocacheLink
      print("Looking for an edit link (id=ctl00_ContentBody_uxEditGeocacheLink)...")
      link = driver.find_element_by_id('ctl00_ContentBody_uxEditGeocacheLink')
      if link:
        print("...found it.  Clicking.")
        link.click()
    elif t2 in content.text:
      print("Looking for an edit button (id=ctl00_ContentBody_btnEditGeocache)...")
      edit_button = driver.find_element_by_id('ctl00_ContentBody_btnEditGeocache')
      if edit_button:
        print("...found it.  Clicking.")
        edit_button.click()

  print("Taking a screenshot...")
  waiter.shoot("Cache edit page")

  edit_url = driver.current_url
  print("Cache edit page URL is: {}".format(edit_url))

  success = edit_cache_page_coorinates(driver, posted, final)
  if success:
    print("...success")
    page_url = success.current_url
    print("New page URL is: {}".format(page_url))
    driver = success

  print("Taking a screenshot...")
  waiter.shoot("Modified cache edit page")

  return True



# -------------------------------------------------

if __name__ == '__main__':
  print("selenium-python-geo-art starting...")

  done = 0   # How many rows have been processed.
  skip = 0   # How many rows to skip before processing.
  stop = 1   # How many rows to process before stopping.

  for numbers in glob.iglob('/tmp/inputs/*.csv'):

    if numbers.rsplit(".")[-1] != "csv":
      print("ERROR - File must have a .csv extension!  {} found.".format(numbers))
      exit(1)

    print("Processing CSV file {}...".format(numbers))

    with codecs.open(numbers, "rU", encoding='utf-8', errors='ignore') as csvFile:
      reader = csv.DictReader(csvFile)
      for row in reader:
        if not skip and done < stop:
          url = row['GC Code']
          if url:
            posted = row['Posted']
            final = row['Final']
            page = open_cache_page(url, posted, final)
            done += 1
        else:
          print("Skipped.  skip={}".format(skip))
          skip += -1
