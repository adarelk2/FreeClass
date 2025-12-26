class ControllerBase:
    def __init__(self):
        self.errors = []

    def responseHTML(self, _context=None, _fileHTML="", _status=200):
        _context = _context or {}
        return {
            "template": f"pages/{_fileHTML}.html",
            "context": _context,
            "status": _status,
        }

    def responseJSON(self, _data=None, _status=200):
        _data = _data or {}
        return {
            "json": _data,
            "status": _status,
        }

    def respond(self, params, context, fileHTML="", default="html"):
        """
        Presentation dispatcher: decides HTML vs JSON.
        Keeps controllers thin and prevents HTTP concerns from leaking into services.
        """
        params = params or {}
        rt = (params.get("responseType") or default).strip().lower()
        print(rt)
        status = 200

        # normalize accepted values
        if rt in ("html", "responsehtml", "text/html"):
            return self.responseHTML(context, fileHTML, status)

        if rt in ("json", "responsejson", "application/json"):
            return self.responseJSON(context, status)

        # fallback: be strict or lenient. I'd be strict:
        return self.responseJSON({"error": f"Unsupported responseType: {rt}"}, 400)
