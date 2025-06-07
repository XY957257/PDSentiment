import os
import sys

def bro():
    abspath = sys.path[0]
    mycommamd = "streamlit run "+abspath.replace("\\",'/') +"/webtest.py"
    print(mycommamd)
    os.system(mycommamd)

bro()