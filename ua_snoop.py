#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import OrderedDict
import BaseHTTPServer as bh

hostname = "0.0.0.0"
port = 9002

class Headers(object):

  UNKNOWN_HEADER_WEIGHT = 2

  def compare(self, req_headers):
    common_headers, unknown_headers = self.get_union(req_headers)
    score = len(unknown_headers) * self.UNKNOWN_HEADER_WEIGHT
    for index, header in enumerate(common_headers):
      req_index = req_headers.index(header)
      score += abs(index - req_index)
    return score

  def get_union(self, req_headers):
    ordered_common_headers = []
    common_headers = []
    unknown_headers = []
    for req_header in req_headers:
      if req_header in self.headers:
        common_headers.append(req_header)
      else:
        unknown_headers.append(req_header)
    for ref_header in self.headers:
      if ref_header in common_headers:
        ordered_common_headers.append(ref_header)
    return ordered_common_headers, unknown_headers

class FirefoxHeaders(Headers):

  def __init__(self):
    self.headers = ("host",
                    "user-agent",
                    "accept",
                    "accept-language",
                    "accept-encoding",
                    "dnt",
                    "referer",
                    "connection",
                    "if-modified-since",
                    "cache-control")

class HeaderParser(object):

  @staticmethod
  def from_string(headers):
    ordered_headers = OrderedDict()
    if headers is not None:
      for header in headers.splitlines():
        k, v = header.split(':', 1)
        ordered_headers[k.lower().strip()] = v.strip()
    return ordered_headers

class HttpHandler(bh.BaseHTTPRequestHandler):
  
  def do_GET(request):
    rhl = HeaderParser.from_string(str(request.headers))
    os = request.wfile
    print("Headers in request:", file=os)
    [print("\t%s: %s" % (k, v), file=os) for k,v in rhl.items()]
    if "firefox" in rhl.get("user-agent").lower():
      print("Got Firefox user-agent: %s" % rhl.get("user-agent"), file=os)
      ffh = FirefoxHeaders()
      score = ffh.compare(rhl.keys())
      if (score is 0):
        print("Got a score of %d. Browser matches user-agent" % score, file=os)
      else:
        print("Got a score of %d. User-agent spoofing?" % score, file=os)
    else:
      print("User-agent not recognised: %s" % rhl.get("user-agent"), file=os)
      print("Trying anyway", file=os)
      ffh = FirefoxHeaders()
      score = ffh.compare(rhl.keys())
      if (score < 3):
        print("Got a score of %d against firefox. Possible match: firefox" % score, file=os)
      else:
        print("Not a match against firefox. Score too high: %d" % score, file=os)


if __name__ == "__main__":
  server = bh.HTTPServer
  httpd = server((hostname, port), HttpHandler)
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    pass
  finally:
    httpd.server_close()

