# perf script event handlers, generated by perf script -g python
# (c) 2016, Milian Wolff <milian.wolff@kdab.com>
# (c) 2019, Lubos Lunak <l.lunak@kde.org>
# Licensed under the terms of the GNU GPL License version 2
#
# This script converts perf data into the callgrind format.
# The output can then be visualized in kcachegrind.
#
# Usage: perf script -s perf2calltree.py > perf.out
#
# NOTE: This script currently does not support conversion of data files
#       that contain multiple event sources.


# VER http://llunak.blogspot.com/2019/05/linux-perf-and-kcachegrind.html

import os
import sys
import subprocess
from collections import defaultdict
from subprocess import PIPE

sys.path.append(os.environ['PERF_EXEC_PATH'] + \
    '/scripts/python/Perf-Trace-Util/lib/Perf/Trace')

from Core import *
from perf_trace_context import *

try:
  from subprocess import DEVNULL # py3k
except ImportError:
  import os
  DEVNULL = open(os.devnull, 'wb')

class Cost:
  def __init__(self):
    self.cost = 0
    self.calls = 0

  def add(self, cost):
    self.cost += cost
    self.calls += 1

class FileInfo:
  def __init__(self, file, line):
    self.file = file
    self.line = line

class Function:
  def __init__(self, dsoName, name, sym):
    self.cost = Cost()
    self.calls = 0
    self.dso = dsoName
    self.name = name
    self.sym = sym
    self.fileInfo = FileInfo("???", 0)

    self.callees = defaultdict(lambda: Cost())

class DSO:
  def __init__(self):
    self.functions = dict()
    self.name = ""

  def createFileInfo(self):
    # try
    addresses = ""
    for sym, function in self.functions.items():
      try:
        addresses += hex(function.sym['start']) + "\n"
      except:
        addresses += "\n"
    process = subprocess.Popen(["addr2line", "-e", self.name], stdin=PIPE, stdout=PIPE, stderr=DEVNULL, universal_newlines=True)
    output = process.communicate(input=addresses)[0].split('\n')
    pos = 0
    for sym, function in self.functions.items():
      try:
        addressInfo = output[pos].split(':')
        file = addressInfo[0]
      except:
        file = None
      if not function.sym or not file or file == "??":
        file = "???"
      try:
        line = int(addressInfo[1])
      except:
        line = 0
      function.fileInfo = FileInfo(file, line)
      pos = pos + 1

# a map of all encountered dso's and the functions therein
# this is done to prevent name clashes
dsos = defaultdict(lambda: DSO())

def addFunction(dsoName, name, sym):
  global dsos
  dso = dsos[dsoName]
  if not dso.name:
      dso.name = dsoName
  function = dso.functions.get(name, None)
  # create function if it's not yet known
  if not function:
    function = Function(dsoName, name, sym)
    dso.functions[name] = function
  return function

eventsType = "events: Samples"

# write the callgrind file format to stdout
def trace_end():
  global dsos

  print("version: 1")
  print("creator: perf-callgrind 0.1")
  print("part: 1")
  # TODO: get access to command line, it's in the perf data header
  #       but not accessible to the scripting backend, is it?
  print(eventsType)

  for dsoName, dso in dsos.items():
    dso.createFileInfo()

  for dsoName, dso in dsos.items():
    print("ob=%s" % dsoName)
    for sym, function in dso.functions.items():
      print("fl=%s" % function.fileInfo.file)
      print("fn=%s" % sym)
      print("%d %d" % (function.fileInfo.line, function.cost.cost))
      for callee, cost in function.callees.items():
        print("cob=%s" % callee.dso)
        print("cfi=%s" % callee.fileInfo.file)
        print("cfn=%s" % callee.name)
        print("calls=%d %d" % (cost.calls, callee.fileInfo.line))
        print("%d %d" % (function.fileInfo.line, cost.cost))
      print("")

def addSample(event, cost, callchain):
  caller = None
  if not callchain:
    # only add the single symbol where we got the sample, without a backtrace
    dsoName = event.get("dso", "???")
    name = event.get("symbol", "???")
    caller = addFunction(dsoName, name, None)
  else:
    # add a function for every frame in the callchain
    for item in reversed(callchain):
      dsoName = item.get("dso", "???")
      name = "???"
      if "sym" in item:
        name = item["sym"]["name"]
      function = addFunction(dsoName, name, item.get("sym", None))
      # add current frame to parent's callee list
      if caller is not None:
        caller.callees[function].add(cost)
      caller = function

  # increase the self cost of the last frame
  # all other frames include it now and kcachegrind will automatically
  # take care of adapting their inclusive cost
  if caller is not None:
    caller.cost.add(cost)

def process_event(event):
  global eventsType
  caller = addSample(event, 1, event["callchain"])

def trace_unhandled(event_name, context, sample, event):
  global eventsType
  cost = 1
  if sample["period"] > 0:
    cost = sample["period"]
    eventsType = "event: ns: time in ns\nevents: ns"
  caller = addSample(event, cost, event['common_callchain'])
