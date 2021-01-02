"""
薬剤師国家試験の勉強をオフラインでする準備。
過去問開設サイトから問題文等をスクレイピングしてきて保存する
"""

import os
import re
from tqdm import tqdm

import requests
from bs4 import BeautifulSoup
import pdfkit
import base64

def get_image_file_as_base64_data(path):
    with open(path,mode='rb') as image_file:
        return base64.b64encode(image_file.read()).decode()

def check_isdir(path):
    tmp = os.path.dirname(path)
    # if not os.path.isdir(tmp):
    os.makedirs(tmp,exist_ok=True)
    
def get_content(url,exam_id,problem_id,out_dir):
    """
    urlから問題、解答、解説に分けて取得、画像は保存しておく
    """
    res = requests.get(url)
    if res.status_code!=200:
        print('{}:{}'.format(res.status_code,url))
        return None,None,None

    soup = BeautifulSoup(res.text,'lxml')

    images = soup.body.find_all('img',class_=re.compile('^alignnone'))

    for i,image in enumerate(images):
        tmp = image['src']
        
        image_path = '{0}/out_html/{1:03d}/img/{1:03d}_{2:03d}_{3:03d}.jpeg'.format(out_dir,exam_id,problem_id,i)

        check_isdir(image_path)

        with open(image_path,mode='wb') as f:
            f.write(requests.get(tmp).content)
        
        # image.replace_with(BeautifulSoup('<img src={}/>'.format(image_path),'lxml'))
        template = "data:;base64,{img_string}"
        image_string = template.format(img_string=get_image_file_as_base64_data(image_path))
        image['src'] = image_string #'./img/{1:03d}_{2:03d}_{3:03d}.jpeg'.format(out_dir,exam_id,problem_id,i)
        image['width'] = str(int(image['width'])*0.7)

        image['height'] = str(int(image['height'])*0.7)
        del image['srcset']

    for f in soup.find_all('a'):
        f.extract()

    search = 'wp-block-cocoon-blocks-blank-box-1 blank-box block-box has-border-color has-red-border-color'

    if not soup.find(class_=search):
        search = "wp-block-cocoon-blocks-blank-box-1 blank-box bb-red block-box"

    problem = list(map(str,list(soup.find(class_=search).previous_siblings)))
    problem = '\n'.join(problem[max(len(problem)-2,0)::-1])

    answer = soup.find(class_=search).text.replace('正解．','')

    description = '\n'.join(list(map(str,list(soup.find(class_=search).next_siblings)[1::])))
    
    return problem,answer,description

def to_html(path,exam_id,problem_id,problem,answer,description):
    html_text = """
        <!DOCTYPE html>
    <html lang="ja">
    <style>
    body
    {{
        color: black;
        background-color: white;
    }}
    div{{
        font-size: 14px;
    }}
    span
    {{
        font-size: 18px;
    }}
    #grad1{{
        background: linear-gradient(transparent 60%,#99e4f1 30%);
        font-size: 18px;
        font-weight: bold;
    }}
    #grad2{{
        background: linear-gradient(transparent 60%,#fda1a1 30%);
        font-size: 18px;
        font-weight: bold;
    }}

    </style>

    <head>
        <meta charset="UTF-8">
        <title>{exam_id}-{problem_id}</title>
    </head>

    <body>
        <h1>
        {prev_path}
        {exam_id}-{problem_id}
        {next_path}
        </h1>
        <div class='problem'>
            <p>
                <span id="grad1">　問題文　</span>
            </p>
            <p>
                {problem}    
            </p>
        </div>
        <hr>

        <input type="button" value="check ans" onclick="toggle_switch()"/>
        
        <div id='toggle'>
        <div class='answer'>
            <p>
                <span id="grad2">　解答　　</span>
            </p>
            <p>
            {answer}
            </p>
        </div>
        <div class='description'>
            <p>
                <span id="grad2">　解説　　</span>
            </p>
            {description}
            </p>
        </div>
        </div>
    </body>
    <script>
    document.getElementById("toggle").style.display="none";
    function toggle_switch(){{
        var x = document.getElementById("toggle");
        if (x.style.display=="block"){{
            x.style.display="none";
        }}
        else{{
            x.style.display="block";
        }}
    }}
    </script>
    """

    prev_path=next_path=''
    if problem_id!=1:
        prev_path = '<a href="./{exam_id:03d}_{problem_id:03d}.html" rel="external" title="prev">≪</a>'.format(path=path,exam_id=exam_id,problem_id=problem_id-1)
    
    if problem_id!=345:
        next_path = '<a href="./{exam_id:03d}_{problem_id:03d}.html" rel="external" title="next">≫</a>'.format(path=path,exam_id=exam_id,problem_id=problem_id+1)
    
    html_text = html_text.format(exam_id=exam_id,problem_id=problem_id,prev_path=prev_path,next_path=next_path,problem=problem,answer=answer,description=description)

    path = '{0}/out_html/{1:03d}/{1:03d}_{2:03d}.html'.format(path,exam_id,problem_id)

    check_isdir(path)
    with open(path,mode='w',encoding='utf-8') as f:
        f.write(html_text)

    # print(html_text)

    return html_text

def to_pdf(path,exam_id,problem_id,problem,answer,description):
    
    html_path = '{0}/out_html/{1:03d}/{1:03d}_{2:03d}.html'.format(path,exam_id,problem_id)
    
    soup = BeautifulSoup(open(html_path),'lxml')
    for f in soup.body.select('a'):
        f.extract()
    soup.body.find('input').extract()
    soup.find('script').extract()

    with open('{0}/out_html/{1:03d}/test.html'.format(path,exam_id,problem_id),mode='w',encoding='utf-8') as f:
        f.write(soup.prettify())

    options = {
            'page-size': 'A5',
            'margin-top': '0.5in',
            'margin-right': '0.4in',
            'margin-bottom': '0.1in',
            'margin-left': '0.4in',
            'encoding': "UTF-8",
            'no-outline': None,
            "zoom":0.85,
            "image-dpi":600,
            "image-quality":94,
            "enable-local-file-access": "",
            "quiet":"",
            }
            
    pdf_path = '{0}/out_pdf/{1:03d}/{1:03d}_{2:03d}.pdf'.format(path,exam_id,problem_id)
    
    check_isdir(pdf_path)
    pdfkit.from_file('{0}/out_html/{1:03d}/test.html'.format(path,exam_id,problem_id),pdf_path,options=options)

    return soup.prettify()

def main():
    out_dir = input('input basedir:')
    for exam_id in range(105,98,-1):
        for problem_id in tqdm(range(1,346)):
            url = 'https://yaku-tik.com/yakugaku/{0}-{1:03d}/'.format(exam_id,problem_id)

            problem,answer,description = get_content(url,exam_id,problem_id,out_dir)

            if not problem:
                continue

            text = to_html(out_dir,exam_id,problem_id,problem,answer,description)
            pdf = to_pdf(out_dir,exam_id,problem_id,problem,answer,description)
            # return
    print('finish')

def test():
    res = requests.get('https://yaku-tik.com/yakugaku/99-280/')
    soup = BeautifulSoup(res.text,'lxml')

    search = "wp-block-cocoon-blocks-blank-box-1 blank-box bb-red block-box"
    
    problem = list(map(str,list(soup.find(class_=search).previous_siblings)))
    problem = '\n'.join(problem[max(len(problem)-2,0)::-1])
    print(problem)
if __name__=='__main__':
    # test()
    main()