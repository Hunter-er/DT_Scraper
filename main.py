# from seleniumbase import BaseCase
import numpy as np
from selenium import webdriver
import time
from pynput.keyboard import Key, Controller
from selenium.webdriver.common.by import By
from tabulate import tabulate
import http.server

# import pandas as pd

# static variables that may need to be changed in future
PROD_LINES = ['BCP7', 'FCC4', 'FCP2', 'FCP6', 'FUN1', 'PC1', 'TC1', 'TC2', 'TCS3', 'TC4']
CAUSES = ['Unspecified', 'Dark Hours', 'Changeover', 'Planned Maintenance', 'Sanitation', 'Equipment', 'Operation',
          'Materials', 'Warehouse', 'Other']
# CHD_PATH = "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"

RTIME_URL = "http://meswebrosenberg.corp.pep.pvt:8080/Thingworx/Runtime/index.html#master=R-TIME&mashup" \
                "=EventReconciliationReport_Mashup&Entity=undefined&__applyThemeName=RTIME_Theme&_refreshTS" \
                "=1670859251866 "

USR = '71061988'
PSS = 'WTFMate13'
RUN_BUTTON_ELM = "root_pagemashupcontainer-6_ptcsbutton-20"
SEL_TIME_ELM = "root_pagemashupcontainer-6_ptcsbutton-81"
CURRENT_SHIFT_ELM = "root_pagemashupcontainer-6_navigationfunction-365-popup_ptcsbutton-6"
WTD_ELM = "root_pagemashupcontainer-6_navigationfunction-365-popup_ptcsbutton-45"

DT_list = []


# THROUGHPUT_BUTTON_ELM = ""


# Class to hold each downtime event data
class Downtime:
    def __init__(self, line, start, end, duration, product, cause, details, operator):
        self.line = line
        self.start = start
        self.end = end
        self.duration = duration
        self.product = product
        self.cause = cause
        self.details = details
        self.operator = operator


# Function to set up server
def run_server():
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()


# Function to find line (x variable) when sorting array
def sort_line(line):
    x_var = 0

    while x_var <= len(PROD_LINES):
        if PROD_LINES[x_var] == line:
            return x_var
        x_var = x_var + 1
    return x_var


# Function to find cause (y variable) when sorting array
def sort_cause(cause):
    y_var = 0

    while y_var <= len(CAUSES):
        if CAUSES[y_var] == cause:
            return y_var
        y_var = y_var + 1
    return y_var


#Function to collect downtime information and compile into list
def gather_DT(time_chosen, DT_list_comp):
    #variables generating DT List
    value_count = 0
    DT_events_count = 0

    #Click select time button
    select_time_button = driver.find_element(By.ID, SEL_TIME_ELM)
    select_time_button.click()
    time.sleep(1)

    #Select time option
    choose_time = driver.find_element(By.ID, time_chosen)
    choose_time.click()
    time.sleep(1)

    # Click run button to pull up WTD DT data
    run_button = driver.find_element(By.ID, RUN_BUTTON_ELM)
    run_button.click()
    time.sleep(3)

    # Pull DT data from event management
    cell_values = driver.find_elements(By.CSS_SELECTOR, "span")

    # Organize DT data into classes for ease of use
    for values in cell_values:

        # find line name (first value) for downtime organization and organize into Downtime class
        if values.text != "" and values.text[-1].isnumeric() and values.text[0].isalpha() and len(values.text) < 5:
            DT_list_comp.append(Downtime(cell_values[value_count + 0].text, cell_values[value_count + 1].text,
                                         cell_values[value_count + 2].text,
                                         float(cell_values[value_count + 3].text), cell_values[value_count + 4].text,
                                         cell_values[value_count + 5].text,
                                         cell_values[value_count + 6].text, cell_values[value_count + 7].text))
            DT_events_count = DT_events_count + 1
            # print(DT_list[-1].line + " - " + str(DT_list[-1].duration) + " hours due to " + DT_list[-1].cause)

        value_count = value_count + 1


# Open browser and connect to R-Time page
driver = webdriver.Chrome()
driver.get(RTIME_URL)
time.sleep(5)

# Login to R-Time
keyboard = Controller()
keyboard.type(USR)
time.sleep(.1)
# noinspection PyTypeChecker
keyboard.press(Key.tab)
# noinspection PyTypeChecker
keyboard.release(Key.tab)
time.sleep(.1)
keyboard.type(PSS)
time.sleep(.1)
# noinspection PyTypeChecker
keyboard.press(Key.enter)
# noinspection PyTypeChecker
keyboard.release(Key.enter)
time.sleep(6)

#Build downtime event lists by adding current shift and week to date
gather_DT(CURRENT_SHIFT_ELM, DT_list)
gather_DT(WTD_ELM, DT_list)

# Downtime data calculations
# Array for DT hours: PROD_LINES x CAUSES
Sorted_DT = np.zeros((10, 10))
event = 0

# DT duration placement in array
while event < len(DT_list):
    x = sort_line(DT_list[event].line)
    y = sort_cause(DT_list[event].cause)
    Sorted_DT[x][y] = Sorted_DT[x][y] + DT_list[event].duration
    event = event + 1

print(Sorted_DT)


#Create sorted list with titles/descriptions
Titled_DT = []
rows = 0
#Update causes list to correct HTML graph shift
CAUSES.insert(0, '')
Titled_DT.append(CAUSES)

#sort through and place line in front of downtime event on list
for lines in PROD_LINES:
    temp_DT_list = []
    value = 0
    temp_DT_list.append(lines)

    #append each individual dt event into temp list
    while value < 10:
        temp_DT_list.append(float("%.2f" % Sorted_DT[rows][value]))
        value = value + 1
    rows = rows + 1

    #appends temp list to main list to create nested list for grid
    Titled_DT.append(temp_DT_list)

print(Titled_DT)

'''
# Move to throughput page
#throughput_button = driver.find_elements(By.ID, "root_pagemashupcontainer-6_ptcstabset-369")
throughput_button = driver.find_elements(By.CSS_SELECTOR, "#shadow-root")
print(throughput_button)
time.sleep(5)

i = 0
for element in throughput_button:
    print (str(i) + ". " + element.text)
    i = i + 1
    #element.click()

#throughput_button[2].click()

# Collect throughput data
#"//*[text()='Throughput']"
#'//*[@id="root_pagemashupcontainer-6_ptcstabset-369"]//ptcs-tabs/ptcs-tab[3]'
#'ptcs-tabs > ptcs-tab:nth-child(3)'
# '//*[@class="sl"]//*[text()="Throughput"]'
'//*[@id="root_pagemashupcontainer-6_ptcstabset-369-bounding-box"]'

<ptcs-tab part="tabs-tab" visible="" tab-number="3" aria-selected="true" role="tab" orientation="horizontal" 
tabindex="0" style="max-width: 1068px;" selected=""> <ptcs-label part="tabs-tab-label" variant="label" 
selected=""></ptcs-label> </ptcs-tab> '''

#Create and save HTML page for viewing
#Create HMTL file
file_html = open("downtime.html", "w")

#HTML file content
file_html.write('''
<html>
    <head>
        <title>RTime Downtime Data</title>
        <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                text-align: center;
            }
        </style>
    </head> 
    <body>
        <h2>R-Time Week to Data Downtime Data in Hours</h1>
        <table style="width:110%">
            <tbody>''' + tabulate(Titled_DT, tablefmt='html') + '''</tbody> 
        </table>
    </body>
</html>
''')

#Save data into the file
file_html.close()


#Run server
print("Running server")
run_server()
