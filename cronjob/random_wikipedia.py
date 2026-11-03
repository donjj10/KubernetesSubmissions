import json
import urllib.error
import urllib.request
import urllib.parse

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/Special:Random"

TODO_BACKEND_URL = "http://todo-backend-svc:3000/todos"


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def get_random_wikipedia_url():
    opener = urllib.request.build_opener(NoRedirectHandler())

    request = urllib.request.Request(
        WIKIPEDIA_URL,
        headers={"User-Agent": "KubernetesTodoCronJob/1.0"}
    )

    try:
        opener.open(request, timeout=30)

    except urllib.error.HTTPError as response:
        location = response.headers.get("Location")

        if response.code in (301, 302, 303, 307, 308) and location:
            return urllib.parse.urljoin(WIKIPEDIA_URL, location)

        raise RuntimeError(
            f"Unexpected Wikipedia response: {response.code}"
        )

    raise RuntimeError("Wikipedia did not redirect to an article")


def create_todo(article_url):
    todo = f"Read {article_url}"

    payload = json.dumps({"todo": todo}).encode("utf-8")

    request = urllib.request.Request(
        TODO_BACKEND_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"Created todo: {todo}", flush=True)
        print(f"Backend response: {response.status}", flush=True)


if __name__ == "__main__":
    article_url = get_random_wikipedia_url()

    print(f"Random Wikipedia article: {article_url}", flush=True)

    create_todo(article_url)