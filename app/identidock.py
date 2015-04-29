from flask import Flask, Response
import requests

app = Flask(__name__)
default_name = 'Dale Bewley'

@app.route('/')
def mainpage():
	name = default_name

	header = '<html><head><title>Identidock</title></head><body>'
	body = '''<form method="POST">
				Hello <input type="text" name="name" value="{}">
				<input type="submit" value="submit">
				</form>
				<p>You look like a:
				<img src="/monster/monster.png"/>
				'''.format(name)
	footer = '</body></html>'

	return header + body + footer

@app.route('/monster/<name>')
def get_identicon(name):
	r = requests.get('http://dnmonster:8080/monster/' + name + '?size=80')
	image = r.content

	return Response(image, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
