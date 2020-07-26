import datetime
import json
import operator
import requests
from bs4 import BeautifulSoup


# Custom date formatting from:
# https://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def get_events():
    """
    This function gets the HTML file returned from https://www.eventbrite.com/d/online/asce-oc-ymf/?q=asce+oc+ymf&mode=search
    It uses BeautifulSoup to parse the HTML file and get the information we want.
    The HTML page returned is essentially what you see when you search "asce oc ymf" on eventbrite_potato.
    :return: str
    """
    response = requests.get("https://www.eventbrite.com/d/online/asce-oc-ymf/?q=asce+oc+ymf&mode=search")
    soup = BeautifulSoup(response.text, 'html.parser')
    events = soup.find('script', type='application/ld+json')  # this is where the list of events in JSON format lives
    html_string = ""

    data = json.loads(events.string)
    data.sort(key=operator.itemgetter('startDate'))  # sort the events by date

    # loop through data and format/append it to our HTML string
    for element in data:
        date = datetime.datetime.fromisoformat(element['startDate'])
        custom_date = custom_strftime("%B {S}, %Y", date)
        html_string += f"""
        <h2 style="margin-bottom:5px;"><a href="{element['url']}" target="_blank"> {element['name']} </a></h2>
    <h4 style="margin-bottom:5px;">{custom_date}</h4>
    
         <p style="margin-top: 5px;">
         {element['description']}
         </p>
         <p style="margin-bottom: 30px;"><a href="{element['url']}" target="_blank">View Details and Register</a></p>"""

    return html_string


def get_jobs():
    response = requests.get("http://ymf-oc.org/careers")
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = soup.find('tbody')
    all_job_info = []
    html_string = ""

    for job in jobs.find_all('tr'):
        job_info = []
        job_info.append(job.find('a')['href'])
        for i, info in enumerate(job.find_all('td')):
            if i != 2:
                job_info.append(info.text)
        all_job_info.append(job_info)

    for job in all_job_info:
        html_string += f"""<tr>
          <td style="font-family:Arial;font-size:13px;font-weight:normal;color:#333333;margin-top:0;margin-bottom:14px;margin-right:0;margin-left:0;padding-top:5px;padding-bottom:0;padding-right:0;padding-left:0;"><a href="{job[0]}">{job[1]}</a></td>
          <td style="font-family:Arial;font-size:13px;font-weight:normal;color:#333333;margin-top:0;margin-bottom:14px;margin-right:0;margin-left:0;padding-top:5px;padding-bottom:0;padding-right:0;padding-left:10px;">{job[2]}</td>
          <td style="font-family:Arial;font-size:13px;font-weight:normal;color:#333333;margin-top:0;margin-bottom:14px;margin-right:0;margin-left:0;padding-top:5px;padding-bottom:0;padding-right:0;padding-left:10px;">{job[3]}</td>
     </tr>"""

    return html_string


def write_to_template(event_html, job_html):
    with open("base.html", "r+") as template:
        template_contents = template.read()
        template_soup = BeautifulSoup(template_contents, 'html.parser')
        event_soup = BeautifulSoup(event_html, 'html.parser')  # HTML of events
        job_soup = BeautifulSoup(job_html, 'html.parser')
        upcoming_events = template_soup.find('h2',
                                    style="margin-bottom:5px;font-family:Arial;font-size:16px;font-weight:bold;color:#fd8c25; margin-bottom: 20px; margin-top:0;margin-right:0;margin-left:0;padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;")
        job_opportunities = template_soup.find('tbody')
        upcoming_events.insert_after(event_soup)
        job_opportunities.insert_after(job_soup)

    with open("asce_oc_template.html", "w", encoding='utf-8') as file:
        file.write(str(template_soup))
