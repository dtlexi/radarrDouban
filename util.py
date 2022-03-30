import logging;

DEFAULT_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
DEFAULT_REQUEST_TIME_OUT=20

def logHtml(msg,html):
    try:
        html=html.strip().replace(" ","").replace('\n','').replace('\t','').replace('\r','') 
    except:
        html=html
    logging.info(msg+":"+html)
    return