from mwcleric.wikigg_client import Site


class ImageFetcher:
    def __init__(self, wiki: Site):
        self.wiki = wiki
        self.good_cache = {}
        self.bad_cache = set()

    def get_url(self, file_name: str) -> tuple[bool, str | None]:
        if file_name in self.good_cache:
            return True, self.good_cache[file_name]
        elif file_name in self.bad_cache:
            return False, None
        else:
            image = self.wiki.images[file_name]

            if image.imageinfo == {}:
                self.bad_cache.add(file_name)
                return False, None
            else:
                self.good_cache[file_name] = image.imageinfo["url"]
                return True, self.good_cache[file_name]
