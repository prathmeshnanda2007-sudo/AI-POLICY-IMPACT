import re
import requests

text = requests.get('https://ai-policy-impact-pz1y.vercel.app/').text
js_file = re.search(r'src="/assets/(index-[^"]+\.js)"', text).group(1)
js_text = requests.get('https://ai-policy-impact-pz1y.vercel.app/assets/' + js_file).text

urls = re.findall(r'https?://[^\'",]+', js_text)
found = [url for url in urls if 'localhost' in url or 'onrender' in url]
print("FOUND URLS:", found)
