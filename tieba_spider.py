#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import codecs
from pyquery import PyQuery as pq
import re
import requests
from time import sleep


def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    sleep(1)
    return local_filename

def parseBr(doc):
    '''将网页中的<br>标签替换为换行符'''
    return doc.find('br').replaceWith('\n').end()

def parseImg(doc):
    '''将网页中的<img>标签替换为Markdown格式的图片'''
    return doc.find('img').each(_replaceImg).end()

def _replaceImg(i,img):
    '''替换<img>标签的回调函数'''
    imgObj=pq(img) 
    local_filename = download_file(imgObj.attr('src'))
    imgObj.replaceWith(f'![](./{local_filename})')

def fetchTieBaPage(url,file=None,minWords=0):
    '''抓取指定的百度贴吧帖子内容，如果指定file参数则可以输出到文件
    minWords参数指定贴子中需要过滤的最小文字长度，默认为0表示不过滤'''
    if not url:
        return
    #可以输入贴子数字编号来获取内容
    if url.isalnum():
        url='http://tieba.baidu.com/p/'+url+'?see_lz=1'
    elif 'tieba.baidu.com/p/' not in url:
        print('错误：无法识别的贴吧贴子地址！')
        return
    #如果有指定file参数，会将内容保存到文件中
    if file and isinstance(file,str):
        try:
            f=codecs.open(file,mode='wb',encoding='utf-8')
        except:
            print('错误：无法输出至指定文件！','\n')
            f=None
    elif isinstance(file,codecs.StreamReaderWriter):
        f=file
    else:
        f=None
    try:
        page=pq(url)
        doc=page.find('div.d_post_content')
        author=page('a[alog-group="p_author"]').eq(0)
        author_name=author.text()
        author_link='https://tieba.baidu.com' + re.sub(r'\?t=.+&fr=.+', '', author.attr.href)
        title=page('h3.core_title_txt').text()
        f.write(f'# {title}\n\n')
        f.write(f'*[@{author_name}]({author_link})*\n\n')
    except:
        print('错误：无法获取贴子[%s]的内容！'%(url))

    #循环读取每一个楼层的文本内容
    for index, node in enumerate(doc):
        p=pq(node)
        lenWords=len(p.text())
        parseText=parseImg(parseBr(p)).text().lstrip()
        if minWords is None or minWords<=0 or lenWords>minWords:
            if f:
                f.write(f'## {index + 1}楼\n\n')
                f.write(parseText)
                f.write('\n\n')
            else:
                input('')
    #如果有下一页，则读取下一页的内容
    link=page.find('div.l_thread_info').find('a').filter(lambda i: pq(this).text() == '下一页')
    if len(link)>0:
        fetchTieBaPage('http://tieba.baidu.com%s'%(link.eq(0).attr('href')),f,minWords)
    #如果没有下一页则关闭输出的文件对象
    elif isinstance(f,codecs.StreamReaderWriter):
        f.close()

def main():
    url=''
    while not url:
        url=input('请输入百度贴吧贴子地址：')
    f=input('请输入保存的文件名：')
    print('='*80,'\n')        
    fetchTieBaPage(url,f)

if __name__ == '__main__':
    main()
