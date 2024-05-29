# from playwright.sync_api import sync_playwright
# import csv

# def scrape_google_maps_data():
#     name_sheet = "hamburg.csv"
#     google_url = "https://www.google.com/maps/search/restaurants+in+hamburg/@53.5518777,9.9229594,13z/data=!3m1!4b1?entry=ttu"
    
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()
#         page.goto(google_url)
        
#         try:
#             page.wait_for_selector('[jstcache="3"]', timeout=30000)
#         except Exception as e:
#             print("Initial selector not found within the specified timeout:", e)
#             browser.close()
#             return
        
#         scrollable = page.query_selector("xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]")
#         if not scrollable:
#             print("Scrollable element not found.")
#             browser.close()
#             return
        
#         end_of_list = False
#         while not end_of_list:
#             try:
#                 scrollable.evaluate("node.scrollBy(0, 50000)")
#             except Exception as e:
#                 print("Error while scrolling:", e)
#                 break
            
#             end_of_list = page.evaluate(
#                 'document.body.innerText.includes("You\'ve reached the end of the list")'
#             )
        
#         urls = page.eval_on_selector_all(
#             'a', '(links) => links.map(link => link.href).filter(href => href.startsWith("https://www.google.com/maps/place/"))'
#         )
        
#         async def scrape_page_data(url):
#             new_page = await browser.new_page()
#             try:
#                 await new_page.goto(url)
#                 await new_page.wait_for_selector('[jstcache="3"]', timeout=30000)
#             except Exception as e:
#                 print("Error navigating to", url, ":", e)
#                 await new_page.close()
#                 return None
            
#             name_element = await new_page.query_selector("xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/h1")
#             name = await (name_element.text_content() if name_element else "")
#             name = f'"{name}"'
            
#             rating_element = await new_page.query_selector("xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]")
#             rating = await (rating_element.text_content() if rating_element else "")
#             rating = f'"{rating}"'
            
#             reviews_element = await new_page.query_selector("xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span")
#             reviews = await (reviews_element.text_content().replace("(", "").replace(")", "") if reviews_element else "")
#             reviews = f'"{reviews}"'
            
#             category_element = await new_page.query_selector("xpath=/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/span/span/button")
#             category = await (category_element.text_content() if category_element else "")
#             category = f'"{category}"'
            
#             address_element = await new_page.query_selector('button[data-tooltip="Copy address"]')
#             address = await (address_element.text_content() if address_element else "")
#             address = f'"{address}"'
            
#             website_element = await new_page.query_selector('a[data-tooltip="Open website"]') or await new_page.query_selector('a[data-tooltip="Open menu link"]')
#             website = await (website_element.get_attribute("href") if website_element else "")
#             website = f'"{website}"'
            
#             phone_element = await new_page.query_selector('button[data-tooltip="Copy phone number"]')
#             phone = await (phone_element.text_content() if phone_element else "")
#             phone = f'"{phone}"'
            
#             url = f'"{url}"'
            
#             # Rest of the code for scraping data
            
#             await new_page.close()
#             print(name, rating, reviews, category, address, website, phone, url)
#             return {"name": name, "rating": rating, "reviews": reviews, "category": category, "address": address, "website": website, "phone": phone, "url": url}
        
#         batch_size = 50
#         results = []
#         for i in range(0, len(urls), batch_size):
#             batch_urls = urls[i:i+batch_size]
#             batch_results = []
#             for url in batch_urls:
#                 result = scrape_page_data(url)
#                 batch_results.append(result)

#             results.extend([result for result in batch_results if result is not None])
#             print(f"Batch {i//batch_size + 1} completed.")
        
#         csv_header = "Name,Rating,Reviews,Category,Address,Website,Phone,Url\n"
#         csv_rows = "\n".join([f"{r['name']},{r['rating']},{r['reviews']},{r['category']},{r['address']},{r['website']},{r['phone']},{r['url']}" for r in results])
        
#         with open(name_sheet, "w", newline="") as csvfile:
#             csvfile.write(csv_header + csv_rows)
        
#         browser.close()

# scrape_google_maps_data()



import asyncio
from playwright.async_api import async_playwright
import csv, random

google_url = input("Enter your URL: ")
batch_size = input("Enter your Batch size: ")
try:
    batch_size = int(batch_size)
except:
    batch_size = 5
name_sheet = f"{random.randint(1111111,9999999)}_output.csv"

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

        csv_header = ["Name", "Rating", "Reviews", "Category", "Address", "Website", "Phone", "Url"]
        csv_rows = [csv_header] + [[r["name"], r["rating"], r["reviews"], r["category"], r["address"], r["website"], r["phone"], r["url"]] for r in results]

        with open(name_sheet, mode="w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(csv_rows)

        await browser.close()

    print("Execution Time: Done")

asyncio.run(scrape_google_maps_data(google_url, batch_size, name_sheet))
