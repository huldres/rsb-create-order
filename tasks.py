from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.Assistant import Assistant


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=200,
    )
    user_input_task()
    get_orders()
    archive_receipts()

def open_robot_order_website(url):
    """Navigates to the given URL"""
    """browser.goto("https://robotsparebinindustries.com/#/robot-order")"""
    browser.goto(url)

def user_input_task():
    assistant = Assistant()
    assistant.add_heading("Input from user")
    assistant.add_text_input("text_input", placeholder="Please enter URL")
    assistant.add_submit_buttons("Submit", default="Submit")
    result = assistant.run_dialog()
    url = result.text_input
    open_robot_order_website(url)

def close_annoying_modal():
    """Closes pop-up on the webpage"""
    page = browser.page()
    page.click("text=OK")

def get_orders():
    '''Downloads the orders file, reads it as a table, and returns the result'''
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    table=Tables()
    orders = table.read_table_from_csv("orders.csv", header=True)
    
    """gdzie powinna być poniższa część kodu???"""
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        store_receipt_as_pdf(row["Order number"])
        screenshot_robot(row["Order number"])
        pdf_file=store_receipt_as_pdf(row["Order number"])
        screenshot_path=screenshot_robot(row["Order number"])
        embed_screenshot_to_receipt(screenshot_path, pdf_file)
        click_another_order()
        """TUTAJ WSZYSTKIE KOLEJNE AKCJE KTORE SA DO ZROBIENIA NA POJEDYNCZYM ZAMOWIENIU"""

    return orders

def fill_the_form(order):
    """Fills in the form for ordering a robot"""
    page = browser.page()

    page.select_option("#head", order["Head"])
    page.locator(f"input[type='radio'][value='{order['Body']}']").check()
    page.fill("input[type='number']", (order["Legs"]))
    page.fill("#address", order["Address"])

    page.click("#preview")
    page.click("#order")

    while page.is_visible("div[class='alert alert-danger']") == True:
        page.click("#order")

def store_receipt_as_pdf(order_number):
    """Export the receipt to a pdf file"""
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_file = "output/receipts/receipt_" + order_number + ".pdf"
    pdf.html_to_pdf(receipt, pdf_file)

    return pdf_file

def screenshot_robot(order_number):
    """Takes a screenshot of the robot"""
    page = browser.page()
    robot_image_locator = page.locator("#robot-preview-image")
    screenshot_path = f"output/image_{order_number}.png"
    robot_image_locator.screenshot(path=screenshot_path)
    
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_file):
    """Adds the screenshot to the receipt pdf"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot_path], target_document=pdf_file, append=True)

def click_another_order():
    """Clicks button Order Another Robot"""
    page = browser.page()
    page.click("#order-another")

def archive_receipts():
    """Creates a ZIP file of receipt PDF files"""  
    source_directory = "output/receipts/"
    output_zip_file = "output/archived_receipts.zip"
    archive = Archive()
    archive.archive_folder_with_zip(source_directory, output_zip_file)