class ControllerBase:         
    def responseHTML(self, _context={}, _fileHTML="", _status=200):
        return {
            "template": f"pages/{_fileHTML}.html",
            "context": _context,
            "status": _status
        }

    def responseJSON(self, _msg={},_flag=True, _status=200):
          return {
            "json":{
                "msg":_msg,
                "flag" : _flag
            },
            "status": _status
          }