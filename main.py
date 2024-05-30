from flask import (Flask, render_template, request, session, send_file, redirect, flash)
import os
from flask_cors import CORS
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
import random
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "sdfsf65416534sdfsdf4653"
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["apikey"] = "ghasvdhgasdgvaghdsvahgdvahg"

def token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        login_dict = session.get("login_dict", "available")
        # token = app.config["mapping_user_dict"].get(login_dict.get("id", "nothing"), {}).get("token", False)
        if login_dict == "available":
            app.logger.debug("Please first login in your app...")
            flash("Please login first...", "danger")
            return redirect("/")
        return func(*args, **kwargs)
    return decorated

async def scrape_google_maps_data(google_url, batch_size, name_sheet):
    # name_sheet = "hamburg.csv"
    # google_url = "https://www.google.com/maps/search/restaurants+in+hamburg/@53.5518777,9.9229594,13z/data=!3m1!4b1?entry=ttu"
    
    print("Execution Time:")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(google_url)

        # Wait for the initial selector or increase timeout if necessary
        try:
            await page.wait_for_selector('[jstcache="3"]', timeout=30000)
        except Exception as error:
            print("Initial selector not found within the specified timeout")
            await browser.close()
            return

        scrollable = await page.query_selector(
            "xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]"
        )

        if not scrollable:
            print("Scrollable element not found.")
            await browser.close()
            return

        end_of_list = False
        while not end_of_list:
            # Wrap the scrollable.evaluate in a try-catch block to handle navigation errors
            try:
                await scrollable.evaluate("(node) => node.scrollBy(0, 50000)")
            except Exception as error:
                print("Error while scrolling:", error.message)
                break  # Exit the loop in case of an error

            end_of_list = await page.evaluate(
                "() => document.body.innerText.includes(\"You've reached the end of the list\")"
            )

        urls = await page.eval_on_selector_all("a", "(links) => links.map(link => link.href).filter(href => href.startsWith('https://www.google.com/maps/place/'))")

        async def scrape_page_data(url):
            new_page = await browser.new_page()
            # Wait for the new page to load or increase timeout if necessary
            try:
                await new_page.goto(url, wait_until='load', timeout=60000)
                await new_page.wait_for_selector('[jstcache="3"]', timeout=30000)
            except Exception as error:
                print("Error navigating to", url, ":", error.message)
                await new_page.close()
                return None  # Return null in case of an error

            name_element = await new_page.query_selector(
                "xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/h1"
            )
            name = await name_element.text_content() if name_element else ""
            name = f'"{name}"'

            rating_element = await new_page.query_selector(
                "xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]"
            )
            rating = await rating_element.text_content() if rating_element else ""
            rating = f'"{rating}"'

            reviews_element = await new_page.query_selector(
                "xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span"
            )
            reviews = await reviews_element.text_content() if reviews_element else ""
            reviews = reviews.replace("(", "").replace(")", "") if reviews else ""
            reviews = f'"{reviews}"'

            category_element = await new_page.query_selector(
                "xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/span/span/button"
            )
            category = await category_element.text_content() if category_element else ""
            category = f'"{category}"'

            address_element = await new_page.query_selector(
                'button[data-tooltip="Copy address"]'
            )
            address = await address_element.text_content() if address_element else ""
            address = f'"{address}"'

            website_element = await new_page.query_selector(
                'a[data-tooltip="Open website"]'
            ) or await new_page.query_selector('a[data-tooltip="Open menu link"]')
            website = await website_element.get_attribute("href") if website_element else ""
            website = f'"{website}"'

            phone_element = await new_page.query_selector(
                'button[data-tooltip="Copy phone number"]'
            )
            phone = await phone_element.text_content() if phone_element else ""
            phone = f'"{phone}"'

            url = f'"{url}"'

            await new_page.close()
            print(name, rating, reviews, category, address, website, phone, url)
            return { "name": name, "rating": rating, "reviews": reviews, "category": category, "address": address, "website": website, "phone": phone, "url": url }

        results = []
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            batch_results = await asyncio.gather(*[scrape_page_data(url) for url in batch_urls])
            results.extend([result for result in batch_results if result is not None])
            print(f"Batch {i // batch_size + 1} completed.")

        # csv_header = ["Name", "Rating", "Reviews", "Category", "Address", "Website", "Phone", "Url"]
        csv_rows = [{"Name": r["name"], "Rating": r["rating"], "Reviews": r["reviews"], "Category": r["category"], "Address": r["address"], "Website": r["website"], "Phone":r["phone"], "Url": r["url"]} for r in results]

        # with open(name_sheet, mode="w", newline='', encoding='utf-8') as file:
        #     writer = csv.writer(file)
        #     writer.writerows(csv_rows)

        df = pd.DataFrame(csv_rows)
        df.to_csv(name_sheet, index=False)

        await browser.close()

    print("Execution Time: Done")


@app.route("/", methods=["GET", "POST"])
def login():
    try:
        if request.method=="POST":
            apikey = request.form["apikey"]
            if apikey==app.config["apikey"]:
                flash("Login Successfully...", "success")
                session["login_dict"] = {"api_key": apikey}
                return redirect("/dashboard")
            else:
                flash("Your api key is wrong...", "danger")
                return render_template("index.html")
        else:
            return render_template("index.html")

    except Exception as e:
        print(e)
        return render_template("index.html")
    
@app.route("/dashboard", methods=["GET", "POST"])
@token_required
def dashboard():
    try:
        if request.method=="POST":
            google_url = request.form.get("url", "")
            keyword = request.form.get("keyword", "")
            if google_url and keyword:
                flash("At least 1 input google url needed", "danger")
            else:
                if keyword:
                    google_url = f"https://www.google.com/maps/search/{keyword}/"
                
                batch_size = request.form["batch"]
                try:
                    batch_size = int(batch_size)
                except:
                    batch_size = 5
                print("process started")
                name_sheet = f"static/uploads/{random.randint(1111111,9999999)}_output.csv"

                asyncio.run(scrape_google_maps_data(google_url, batch_size, name_sheet))
                file = os.path.abspath(name_sheet)
                return send_file(file, as_attachment=True)
        else:
            return render_template("dashboard.html")

    except Exception as e:
        print(e)
        return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)