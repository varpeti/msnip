import re
from io import StringIO
from pathlib import Path

import sublime
import sublime_plugin
from sublime_lib import ResourcePath

SUFFIX = ".msnip"
SUFFIX_SUBLIME = ".sublime-completions"

def read(path):
    with path.open('r', encoding='utf-8') as f:
        text = f.read()
    return iter(text.splitlines())  #lines

def mine(lines):

    currentKey = ""
    currentValue = ""

    def append():

        if currentKey!="" and currentValue!="":
            if currentKey not in ret: # single value
                ret[currentKey]=currentValue
                pass
            elif type(ret[currentKey])==str: # another value? -> list
                ret[currentKey] = [currentValue]
                pass
            else:   # append to the list
                ret[currentKey].append(currentValue)

    line = next(lines, None)
    state = "nothing" # | ### key | --- value |
    ret = {}
    while line:
        if line == "###":
            state="key"
            line = next(lines, None)
            append()
            currentKey=""
            currentValue=""
        elif line == "---":
            state="value"
            line = next(lines, None)
            append()
            currentValue=""

        if state=="key":
            if currentKey=="":
                currentKey=line
            else:
                currentKey+="\n"+line
        elif state=="value":
            if currentValue=="":
                currentValue=line
            else:
                currentValue+="\n"+line

        line = next(lines, None)
    append()
    return ret

def write(path,data):
    with path.open('w', encoding='utf-8') as f:
        print(data, file=f)

def dump(obj):
    #print(obj)
    if "scope" in obj:
        return '''\
{{
   "scope": "{scope}",
   "completions":
   [
      {{ "trigger": "{trigger}", "contents": "{content}" }}
   ]
}}'''.format(scope=obj["scope"],trigger=obj["trigger"],content=obj["content"].replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\""))
    else: 
        return '''\
{{
   "completions":
   [
      {{ "trigger": "{trigger}", "contents": "{content}" }}
   ]
}}'''.format(trigger=obj["trigger"],content=obj["content"].replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\""))



def start(path):
    write(path.with_suffix(SUFFIX_SUBLIME),dump(mine(read(path))))
    


class msnipListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        str_path = view.file_name()
        if not str_path:
            return
        path = Path(str_path)
        if path.suffix == SUFFIX:
            start(path)