from types import SimpleNamespace
import toml


class ChoculaConfig(SimpleNamespace):
    @classmethod
    def from_file(cls, file_path="sources.toml", sources_dir="data/"):

        # TODO: can we just pass _dict=SimpleNamespace here?
        sources = toml.load(file_path)

        # convert all sub-tables to SimpleNamespace
        for k in list(sources.keys()):
            if isinstance(sources[k], dict):
                if "filename" in sources[k]:
                    sources[k]["filepath"] = sources_dir + sources[k]["filename"]
                sources[k] = SimpleNamespace(**sources[k])

        # conver the whole thing to SimpleNamespace
        return ChoculaConfig(**sources)
