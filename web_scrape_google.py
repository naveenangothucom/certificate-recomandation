import urllib.request
from bs4 import BeautifulSoup
import re
import csv
url = 'https://google.com/search?q=Top+network+security+certifications'

# Perform the request
request = urllib.request.Request(url)

# Set a normal User Agent header, otherwise Google will block the request.
request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
raw_response = urllib.request.urlopen(request).read()

# Read the repsonse as a utf-8 string
html = raw_response.decode("utf-8")

# The code to get the html contents here.

soup = BeautifulSoup(html, 'html.parser')

# Find all the search result divs
divs = soup.select("#search div.g")

scraped_content = {}
for div in divs:
    # Search for a h3 tag
    results = div.select("h3")

    # Check if we have found a result
    if (len(results) >= 1):

        # Print the title
        title = results[0]
        print(title.get_text())
        for a in div.find_all('a', href=True):
            hyperlinks = a['href']
            # Perform the request
            if "http" in hyperlinks[:5]:
                print(hyperlinks)
                sub_request = urllib.request.Request(hyperlinks)

                # Set a normal User Agent header, otherwise Google will block the request.
                sub_request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
                sub_raw_response = urllib.request.urlopen(sub_request).read()

                # Read the repsonse as a utf-8 string
                sub_html = sub_raw_response.decode("utf-8")

                # The code to get the html contents here.
                sub_soup = BeautifulSoup(sub_html, 'html.parser')
                text = sub_soup.find_all(text=True)
                page_text = []
                blacklist = [
                    '[document]',
                    'noscript',
                    'header',
                    'html',
                    'meta',
                    'head', 
                    'input',
                    'script',
                    'style',
                    # there may be more elements you don't want, such as "style", etc.
                ]
                order = 0
                head = False
                certification = None
                message = None
                for t in text:
                    if t.parent.name not in blacklist:
                        search_text = t.lower()
                        if (len(search_text.strip()) > 0) and ("ceh" in search_text or 'certified ethical hacker' in search_text or 'comptia' in search_text or 'cnd' in search_text or 'certified network defender' in search_text or head is True):
                            if head:
                                message = search_text
                            else:
                                certification = search_text
                            page_text .append({"certification": certification, "message": message, "order":order})
                            head = not head
                            order += 1
                scraped_content[hyperlinks] = {"Title": title, "page_text": page_text}


# Now that we have obtained the contents from all webpages, its time to analyze the messages and 
# Consolidate the results

#Cleaning the messages
def cleanhtml(raw_html):
    if raw_html:
        print(raw_html)
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    return ""

for hyperlinks in scraped_content:
    for index in range(len(scraped_content[hyperlinks]["page_text"])):
        cleaned_message = cleanhtml(scraped_content[hyperlinks]["page_text"][index]["message"])
        scraped_content[hyperlinks]["page_text"][index]["message"] = cleaned_message


print(scraped_content)
# Creating a readable dataframe from the content acquired.
with open('writeData.csv', mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['hyperlink', 'title', 'certification', 'message', 'order'])
    for hyperlinks in scraped_content:
        title = scraped_content[hyperlinks]["Title"]
        for index in range(len(scraped_content[hyperlinks]["page_text"])):
            certification =  scraped_content[hyperlinks]["page_text"][index]["certification"]
            message = scraped_content[hyperlinks]["page_text"][index]["message"]
            order = scraped_content[hyperlinks]["page_text"][index]["order"]
            writer.writerow([hyperlinks, title, certification, message, order])