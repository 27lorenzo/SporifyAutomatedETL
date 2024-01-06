from flask import Flask, request, redirect
import config

app = Flask(__name__)
auth_code = None
auth_url = 'https://accounts.spotify.com/authorize'
redirect_uri = 'http://localhost:8888/callback'
# scope = 'user-read-recently-played'
scope = 'user-library-read'

@app.route('/authorize')
def authorize():
    authorize_url = f'{auth_url}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}'
    return redirect(authorize_url)


@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    print(f"Authorization Code: {auth_code}")
    print(f"Scope: {scope}")

    with open("session/authorization_code.txt", "w") as file:
        file.write(auth_code)
        print("File created")

    return "Authorization Code received. You can close this window."


if __name__ == '__main__':

    c = config.config()
    client_id = c.readh('spotify_token', 'client_id') or 'localhost'
    client_secret = c.readh('spotify_token', 'client_secret') or 'localhost'
    app.run(port=8888)