"""Minimal reader for a public SharePoint folder share link (used for MVImgNet).

Same method as the dataset authors' download_tool.py (open the share link to get a session
cookie, then list folders with SharePoint's RenderListDataAsStream API), without its
auto-installing of packages and with working subfolder navigation.

    venv\\Scripts\\python.exe scripts\\sharepoint.py <share-link> [sub/folder/path]
    (password from the MVImgNet form in the environment variable MVIMGNET_PASSWORD)
"""
import os
import json
import re
import sys
import urllib.parse

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _submit_password(session, page, password):
    """Fill in SharePoint's guest-access password form (all hidden fields + the password)."""
    action = re.search(r'<form[^>]*action="([^"]+)"', page.text).group(1).replace("&amp;", "&")
    fields = {}
    for tag in re.findall(r"<input[^>]*>", page.text):
        name = re.search(r'name="([^"]*)"', tag)
        if not name:
            continue
        kind = re.search(r'type="([^"]*)"', tag)
        if kind and kind.group(1) in ("submit", "button") and "Password" not in name.group(1):
            continue
        value = re.search(r'value="([^"]*)"', tag)
        fields[name.group(1)] = value.group(1) if value else ""
    fields["txtPassword"] = password
    url = urllib.parse.urljoin(page.url, action)
    r = session.post(url, data=fields, headers={"user-agent": UA, "referer": page.url}, timeout=60)
    r.raise_for_status()
    return r


class Share:
    def __init__(self, link, password=None):
        self.s = requests.session()
        r = self.s.get(link, headers={"user-agent": UA}, timeout=60)
        r.raise_for_status()
        if 'name="txtPassword"' in r.text:
            if password is None:
                raise SystemExit("this link needs a password (--password)")
            r = _submit_password(self.s, r, password)
            if 'name="txtPassword"' in r.text:
                raise SystemExit("password rejected")
        self.root = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(r.url).query))["id"]
        ctx = re.search(r"var _spPageContextInfo\s*=\s*({.*?});", r.text, re.DOTALL)
        info = json.loads(re.sub(r",\s*([}\]])", r"\1", ctx.group(1))) if ctx else {}
        self.site = info.get("webAbsoluteUrl") or "/".join(r.url.split("/")[:5])
        self.list_url = info.get("listUrl") or "/" + "/".join(self.root.strip("/").split("/")[:3])
        self.digest = info.get("formDigestValue")

    def list(self, rel=""):
        """Items in root/rel: list of dicts with name, folder?, size, url (download link)."""
        folder = self.root.rstrip("/") + ("/" + rel.strip("/") if rel else "")
        headers = {"Accept": "application/json;odata=verbose",
                   "Content-Type": "application/json;odata=verbose", "user-agent": UA}
        if self.digest:
            headers["X-RequestDigest"] = self.digest
        items, query = [], (f"?@a1='{urllib.parse.quote(self.list_url)}'"
                            f"&RootFolder={urllib.parse.quote(folder)}&TryNewExperienceSingle=TRUE")
        body = {"parameters": {"__metadata": {"type": "SP.RenderListDataParameters"},
                               "RenderOptions": 5707527, "AllowMultipleValueFilterForTaxonomyFields": True,
                               "AddRequiredFields": True}}
        while True:
            url = (f"{self.site.rstrip('/')}/_api/web/GetListUsingPath(DecodedUrl=@a1)"
                   f"/RenderListDataAsStream{query}")
            r = self.s.post(url, data=json.dumps(body), headers=headers, timeout=60)
            r.raise_for_status()
            data = r.json()
            node = data.get("ListData", data)
            for row in node.get("Row", []):
                items.append(dict(name=row.get("FileLeafRef"), folder=row.get("FSObjType") == "1",
                                  size=int(row.get("File_x0020_Size") or 0),
                                  url=row.get("@content.downloadUrl") or row.get(".spItemUrl")))
            nxt = node.get("NextHref")
            if not nxt:
                return items
            query = f"{nxt}&@a1='{urllib.parse.quote(self.list_url)}'&TryNewExperienceSingle=TRUE"

    def download_url(self, item):
        """A direct download URL for a file item (resolving .spItemUrl when needed)."""
        if item["url"] and "download" in item["url"].lower() and "tempauth" in item["url"].lower():
            return item["url"]
        r = self.s.get(item["url"], headers={"user-agent": UA}, timeout=60)
        r.raise_for_status()
        return r.json().get("@content.downloadUrl")


if __name__ == "__main__":
    share = Share(sys.argv[1], os.environ.get("MVIMGNET_PASSWORD"))
    for it in share.list(sys.argv[2] if len(sys.argv) > 2 else ""):
        print(("[dir] " if it["folder"] else f"{it['size'] / 2**20:9.1f} MB ") + it["name"])
