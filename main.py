from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import os
import time
import csv


def dexNavigate(driver):
    # Landing Page
    driver.get('https://clarity.dexcom.eu/')
    driver.switch_to.frame(driver.find_element(By.CLASS_NAME, "eu-cookie-prompt"))  # switch to cookies frame
    driver.find_element(By.XPATH, '/html/body/div/div[3]/div/button[1]').click()  # allow cookies button
    driver.switch_to.default_content()  # switch to main page
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[1]/div/div[3]/div/nav/ul/li[2]/div/a').click()  # click health portal


def dexHealthLog(driver, dexUser, dexPass):
    # Login Into System
    email = driver.find_element(By.XPATH, '//*[@id="ember40"]')  # select email field
    password = driver.find_element(By.XPATH, '//*[@id="ember41"]')  # select pass field
    email.send_keys(str(dexUser))
    password.send_keys(str(dexPass))
    driver.find_element(By.XPATH,
                        '/html/body/clarity-application/clarity-application-content/div/main/section/md-card/div/div/div/form/fieldset/button').click()  # Login
    time.sleep(1)
    try:
        if driver.find_element(By.CSS_SELECTOR, '.alert--danger').is_displayed():
            print('Login Failed. Please Retry')
            email.clear()
            password.clear()
            return False
    except:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ember115")))  # Wait till patient page loads
        return True


def dexPatientAddShare(driver, pInfo):  # pInfo = [fname, lname, year, month, date, email]
    time.sleep(2)
    driver.get('https://clarity.dexcom.eu/professional/patients/add')  # Go to add patient page
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ember48")))
    fname = driver.find_element(By.ID, 'patient-form-firstname')  # select required fields
    lname = driver.find_element(By.ID, 'patient-form-lastname')
    DOBY = driver.find_element(By.ID, 'ember56')
    DOBM = Select(driver.find_element(By.ID, 'ember57'))
    DOBD = driver.find_element(By.ID, 'ember83')
    # ID = driver.find_element(By.ID, 'patient-form-patient-id')
    fname.send_keys(str(pInfo[0]))
    lname.send_keys(str(pInfo[1]))
    DOBY.send_keys(str(pInfo[2]))
    DOBM.select_by_visible_text((str(pInfo[3])).capitalize())  # Make sure capitalized
    DOBD.send_keys(str(pInfo[4]))
    # ID.send_keys(str(pID))
    driver.find_element(By.XPATH,
                        '/html/body/clarity-application/clarity-application-content/div/clarity-content-row/clarity-content-row-content/main/md-card/div/div/div[3]/ul/li[1]/button').click()  # save button
    time.sleep(1)
    try:
        if driver.find_element(By.XPATH, '/html/body/clarity-application/clarity-application-content/div/clarity-content-row/clarity-content-row-content/main/md-card/div/div/div[1]').is_displayed():
            driver.get('https://clarity.dexcom.eu/professional/patients')
            return False
    except:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[5]/div[2]/div[6]/p[2]/button[2]")))  # Wait for finish dialog to pop out
        driver.find_element(By.XPATH,
                            '/html/body/div[5]/div[2]/div[6]/p[2]/button[2]').click()  # autocomplete share data request
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ember-radio-button  ')))  # select share data
        driver.find_element(By.XPATH, '/html/body/div[7]/div/div/div/div/div[2]/fieldset/div[2]/label').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ember-text-field')))  # select email
        time.sleep(1)
        email = driver.find_element(By.CLASS_NAME, 'ember-text-field')  # select email field
        email.send_keys(str(pInfo[5]))
        driver.find_element(By.XPATH, '/html/body/div[7]/div/div/div/div/fieldset/button[1]').click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[5]/div[2]/button[1]')))  # Click okay button on end dialog
        driver.get('https://clarity.dexcom.eu/professional/patients')
        return True



def main():
    print("Welcome to patient addition")
    browser = webdriver.Firefox()
    dexNavigate(browser)

    LoginSuccess = False
    while LoginSuccess == False:  # Logging In
        dUser = str(input('Dexcom Account Username: '))
        dPass = str(input('Dexcom Account Password: '))
        LoginSuccess = dexHealthLog(browser, dUser, dPass)


    if os.path.exists("patientadded.txt"):
        os.remove("patientadded.txt")
    f = open("patientadded.txt", "x")
    with open('dpdcgm.tsv') as file:
        tsv_file = csv.reader(file, delimiter='\t')
        count = 1
        for line in tsv_file:
            print(f'Adding patient {count} ({line[0]} {line[1]}) to Dexcom ...')
            count += 1
            patientAdd = dexPatientAddShare(browser, line)
            if patientAdd == True:
                print('Success!')
                line.append('True')
                f.write('\t'.join(line) + '\n')

            else:
                print(f'Failed to add {line[0]} {line[1]}')
                line.append('False')
                f.write('\t'.join(line) + '\n')
    print("Process Finished")
    f.close()
    browser.quit()

if __name__ == '__main__':
    main()







