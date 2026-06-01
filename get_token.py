import json
import urllib.request
import urllib.parse

# Load client secrets
with open('client_secret.json', 'r') as f:
    data = json.load(f)

config = data['installed']
client_id = config['client_id']
client_secret = config['client_secret']
redirect_uri = config['redirect_uris'][0]
scope = "https://www.googleapis.com/auth/youtube.upload"

# Step 1: Generate the URL
params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'scope': scope,
    'response_type': 'code',
    'access_type': 'offline',
    'prompt': 'consent'
}
auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}"
print("\n=== STEP 1 ===")
print("Copy and open this URL in your mobile browser to log in:")
print("\n" + auth_url + "\n")
print("=== STEP 2 ===")
print("After logging in, the page will say 'This site can’t be reached' or show 'localhost' in the address bar. This is completely normal!")
print("Copy that FULL URL from your browser's address bar and paste it below:")

returned_url = input("\nPaste the URL here: ").strip()

try:
    # Extract authorization code
    parsed_url = urllib.parse.urlparse(returned_url)
    code = urllib.parse.parse_qs(parsed_url.query)['code'][0]

    # Step 2: Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    encoded_data = urllib.parse.urlencode(token_data).encode('utf-8')
    req = urllib.request.Request(token_url, data=encoded_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        with open('token.json', 'w') as token_file:
            json.dump(res_data, token_file, indent=4)
        print("\n[+] Success! 'token.json' has been created perfectly.")
except Exception as e:
    print(f"\n[-] Error generating token: {e}")
    print("Make sure you copied the entire URL from the browser link bar.")

