from flask import Flask, Response
import scrape

app = Flask(__name__)


@app.route('/')
def index():
    return '''
        <html><body>
        Click to download ASCE OC YMF template <a href="/download_data">here.</a>
        </body></html>
        '''


@app.route('/download_data')
def download_html():
    events_html = scrape.get_events()
    jobs_html = scrape.get_jobs()
    file_string = scrape.write_to_template(events_html, jobs_html)
    return Response(
        file_string,
        mimetype="text/html",
        headers={"Content-disposition":
                 "attachment; filename=asce-email.html"})


if __name__ == '__main__':
    app.run()
